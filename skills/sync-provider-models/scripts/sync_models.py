#!/usr/bin/env python3
"""
sync_models.py — Verifica modelos novos/removidos em providers do opencode.

Para cada provider informado:
  1. Lê ~/.local/share/opencode/auth.json para obter a API key.
  2. Lê ~/.cache/opencode/models.json para obter baseUrl (api) e modelos em cache.
  3. Faz GET {baseUrl}/models (compatível OpenAI) com Authorization: Bearer.
  4. Calcula diff: novos (remoto ausente no cache) e removidos (cache ausente no remoto).
  5. Com --apply: adiciona novos ao cache (backup prévio) usando entry template do
     modelo mais próximo da mesma family; modelos "removidos" NUNCA são deletados
     do cache (podem estar deprecated mas ainda utilizáveis, ou o endpoint /models
     não enumerar multimodais).

Uso:
  scripts/sync_models.sh --provider alibaba-token-plan           # report apenas
  scripts/sync_models.sh --provider alibaba-token-plan --apply  # adiciona novos
  scripts/sync_models.sh --provider opencode-go --apply
  scripts/sync_models.sh --provider all                          # todos os providers com auth
  scripts/sync_models.sh --list-providers
  scripts/sync_models.sh --help

Dependências: python3 (stdlib apenas: json, os, sys, argparse, urllib, datetime, shutil).
NÃO requer curl nem binário sqlite3.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import shutil
import sys
import urllib.error
import urllib.request
from pathlib import Path

HOME = Path(os.path.expanduser("~"))
CACHE_PATH = HOME / ".cache" / "opencode" / "models.json"
AUTH_PATH = HOME / ".local" / "share" / "opencode" / "auth.json"

# Providers suportados explicitamente (outros com auth podem funcionar via --provider).
KNOWN_PROVIDERS = ["alibaba-token-plan", "opencode-go", "opencode", "alibaba-coding-plan"]


def _ts_to_date(ts: int | float | None) -> str | None:
    if ts is None:
        return None
    try:
        v = int(ts)
        # heurística de magnitude: s=1e9..1e12, ms=1e12..1e14, us>1e14
        if v > 1e14:
            v = int(v / 1e6)
        elif v > 1e12:
            v = int(v / 1e3)
        return _dt.date.fromtimestamp(v).isoformat()
    except (ValueError, TypeError, OSError):
        return None


def _load_json(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_json(path: Path, data: dict) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)
    os.replace(tmp, path)


def _backup(path: Path) -> Path | None:
    if not path.exists():
        return None
    i = 1
    while True:
        cand = path.with_suffix(path.suffix + f".bak{i}")
        if not cand.exists():
            shutil.copy2(path, cand)
            return cand
        i += 1


def _get_auth_keys() -> dict:
    if not AUTH_PATH.exists():
        return {}
    return _load_json(AUTH_PATH)


def _provider_block(cache: dict, provider_id: str) -> dict | None:
    p = cache.get(provider_id)
    if not isinstance(p, dict):
        return None
    return p


def _fetch_models(base_url: str, api_key: str, timeout: int = 30) -> dict:
    url = base_url.rstrip("/") + "/models"
    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {api_key}",
            "User-Agent": "opencode-sync-models/1.0",
            "Accept": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _pick_template_entry(models: dict, new_id: str) -> dict:
    """
    Escolhe uma entrada existente no cache para servir de template ao novo modelo.
    Estratégia:
      1. Mesma family (campo `family`) se houver.
      2. Mesmo prefixo antes do primeiro '-'.
      3. Primeira entrada disponível.
    Copia shallow + sobrescreve id/name/description/datas.
    """
    new_family = None
    for m in models.values():
        if isinstance(m, dict) and m.get("id") == new_id:
            new_family = m.get("family")
            break
    template = None
    # 1. family
    if not template:
        for m in models.values():
            if isinstance(m, dict) and m.get("family") and m.get("family") == new_family and m.get("id") != new_id:
                template = m
                break
    # 2. prefix
    if not template:
        prefix = new_id.split("-")[0]
        for mid, m in models.items():
            if isinstance(m, dict) and mid.split("-")[0] == prefix and mid != new_id:
                template = m
                break
    # 3. fallback primeiro
    if not template:
        for m in models.values():
            if isinstance(m, dict):
                template = m
                break
    if not template:
        return {
            "id": new_id,
            "name": new_id,
            "description": "Model added by sync-provider-models skill",
            "attachment": False,
            "reasoning": False,
            "tool_call": False,
            "temperature": True,
            "release_date": _dt.date.today().isoformat(),
            "last_updated": _dt.date.today().isoformat(),
            "modalities": {"input": ["text"], "output": ["text"]},
            "open_weights": False,
            "limit": {"context": 32768, "output": 8192},
            "cost": {"input": 0, "output": 0, "cache_read": 0, "cache_write": 0},
        }
    # shallow copy + override
    entry = dict(template)
    entry["id"] = new_id
    # name: Title-case do id
    entry["name"] = " ".join(part.capitalize() for part in new_id.replace("_", "-").split("-"))
    today = _dt.date.today().isoformat()
    entry["release_date"] = today
    entry["last_updated"] = today
    # remove status deprecated herdado se vier do template
    entry.pop("status", None)
    return entry


def _extract_remote_meta(remote_item: dict) -> dict:
    """Extrai metadados adicionais do item retornado pelo /models (ex: created)."""
    meta = {}
    created = remote_item.get("created")
    if created is not None:
        d = _ts_to_date(created)
        if d:
            meta["release_date"] = d
            meta["last_updated"] = d
    return meta


def diff_provider(provider_id: str, cache: dict, auth: dict, *, timeout: int = 30) -> dict:
    """Retorna {provider, base_url, cached, remote, new, removed, error}."""
    out = {
        "provider": provider_id,
        "base_url": None,
        "cached": [],
        "remote": [],
        "new": [],
        "removed": [],
        "error": None,
    }
    block = _provider_block(cache, provider_id)
    if not block:
        out["error"] = f"provider '{provider_id}' não encontrado no cache ({CACHE_PATH})"
        return out
    base_url = block.get("api")
    out["base_url"] = base_url
    models = block.get("models", {})
    if not isinstance(models, dict):
        out["error"] = f"provider '{provider_id}' sem bloco 'models' válido"
        return out
    out["cached"] = sorted(models.keys())
    cred = auth.get(provider_id)
    if not cred or not cred.get("key"):
        out["error"] = f"sem credencial para '{provider_id}' em {AUTH_PATH}"
        return out
    try:
        data = _fetch_models(base_url, cred["key"], timeout=timeout)
    except urllib.error.URLError as e:
        out["error"] = f"HTTP/fetch falhou: {e}"
        return out
    except Exception as e:  # noqa: BLE001
        out["error"] = f"fetch falhou: {e}"
        return out
    if not isinstance(data, dict) or "data" not in data:
        out["error"] = f"resposta inesperada do /models (sem 'data'): {str(data)[:200]}"
        return out
    remote_map = {}
    for item in data.get("data", []):
        if isinstance(item, dict) and item.get("id"):
            remote_map[item["id"]] = item
    remote_ids = set(remote_map.keys())
    cached_ids = set(models.keys())
    out["remote"] = sorted(remote_ids)
    out["new"] = sorted(remote_ids - cached_ids)
    out["removed"] = sorted(cached_ids - remote_ids)
    out["_remote_map"] = remote_map  # privado, usado por apply
    return out


def apply_new(cache: dict, diff: dict) -> list[str]:
    """Adiciona modelos novos ao cache. Retorna lista de ids adicionados."""
    provider = diff["provider"]
    block = cache[provider]
    models = block["models"]
    added = []
    for new_id in diff["new"]:
        template = _pick_template_entry(models, new_id)
        meta = _extract_remote_meta(diff.get("_remote_map", {}).get(new_id, {}))
        template.update(meta)  # sobrescreve datas se a API informou created
        models[new_id] = template
        added.append(new_id)
    return added


def _print_report(diff: dict) -> None:
    p = diff["provider"]
    if diff["error"]:
        print(f"[{p}] ERRO: {diff['error']}", file=sys.stderr)
        return
    print(f"=== {p} ===")
    print(f"base_url: {diff['base_url']}")
    print(f"cache: {len(diff['cached'])} modelos | remoto: {len(diff['remote'])} | comum: {len(set(diff['cached']) & set(diff['remote']))}")
    if diff["new"]:
        print(f"NOVOS ({len(diff['new'])}):")
        for m in diff["new"]:
            print(f"  + {m}")
    else:
        print("NOVOS: (nenhum)")
    if diff["removed"]:
        print(f"NO CACHE SEM REMOTO ({len(diff['removed'])}) — não removidos (podem ser deprecated/multimodais):")
        for m in diff["removed"]:
            print(f"  - {m}")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="sync_models.py",
        description="Verifica e sincroniza modelos de providers do opencode contra a API remota.",
    )
    ap.add_argument("--provider", action="append", default=[], help="ID do provider (repetível). Use 'all' para todos com auth.")
    ap.add_argument("--apply", action="store_true", help="Adiciona modelos novos ao cache (com backup).")
    ap.add_argument("--list-providers", action="store_true", help="Lista providers conhecidos e sai.")
    ap.add_argument("--timeout", type=int, default=30, help="Timeout HTTP em segundos (default 30).")
    ap.add_argument("--no-backup", action="store_true", help="Não cria backup do cache ao aplicar (default: cria).")
    args = ap.parse_args(argv)

    if args.list_providers:
        auth = _get_auth_keys()
        for pid in KNOWN_PROVIDERS:
            mark = "*" if pid in auth else " "
            print(f"{mark} {pid}")
        print("\n* = tem credencial em auth.json")
        return 0

    if not args.provider:
        ap.print_help()
        return 2

    providers: list[str] = []
    for p in args.provider:
        if p == "all":
            auth = _get_auth_keys()
            providers.extend(pid for pid in KNOWN_PROVIDERS if pid in auth)
        else:
            providers.append(p)
    # dedup preservando ordem
    seen = set()
    providers = [p for p in providers if not (p in seen or seen.add(p))]

    if not providers:
        print("nenhum provider para processar.", file=sys.stderr)
        return 1

    if not CACHE_PATH.exists():
        print(f"cache não encontrado: {CACHE_PATH}", file=sys.stderr)
        return 1
    cache = _load_json(CACHE_PATH)
    auth = _get_auth_keys()

    any_new = False
    diffs = []
    for pid in providers:
        d = diff_provider(pid, cache, auth, timeout=args.timeout)
        diffs.append(d)
        _print_report(d)
        if d["new"]:
            any_new = True
        print()

    if args.apply and any_new:
        if not args.no_backup:
            bak = _backup(CACHE_PATH)
            print(f"backup criado: {bak}", file=sys.stderr)
        total_added = 0
        for d in diffs:
            if d.get("error") or not d["new"]:
                continue
            added = apply_new(cache, d)
            total_added += len(added)
            print(f"[{d['provider']}] adicionados ao cache: {', '.join(added)}", file=sys.stderr)
        _save_json(CACHE_PATH, cache)
        print(f"cache atualizado: {total_added} modelo(s) adicionado(s) em {CACHE_PATH}", file=sys.stderr)
    elif args.apply and not any_new:
        print("nada para aplicar (nenhum modelo novo).", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
