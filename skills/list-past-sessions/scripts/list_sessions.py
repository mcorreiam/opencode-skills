#!/usr/bin/env python3
r"""
list_sessions.py — bundle para skill list-past-sessions
Transforma 3 queries + conversão de timestamp em um comando único:

  python3 scripts/list_sessions.py --limit 5 --scope current
  opencode db --format json "..." | python3 scripts/list_sessions.py --stdin  # futuro

Gera tabela Markdown pronta com header <!-- projeto:... total/exibindo/scope -->
e converte time_created/time_updated (ms) -> DD/MM/YYYY HH:MM via astimezone().
Escapa title (| -> \|, \ -> \\) e trunca 120c automaticamente.

Requer: opencode >=0.8 (primário, read-only) ou fallback Python sqlite3 ?mode=ro.
Nunca exige binário sqlite3.
"""
import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

DEFAULT_LIMIT = 50
DEFAULT_SCOPE = "current"

def run_opencode_json(sql: str) -> list | dict:
    """Executa opencode db --format json e retorna JSON parseado. Levanta se falhar."""
    result = subprocess.run(
        ["opencode", "db", "--format", "json", sql],
        capture_output=True, text=True, timeout=15
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or f"opencode db falhou: {sql[:120]}")
    out = result.stdout.strip()
    if not out:
        return []
    return json.loads(out)

def db_path_fallback() -> str:
    try:
        r = subprocess.run(["opencode", "db", "path"], capture_output=True, text=True, timeout=5)
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout.strip()
    except Exception:
        pass
    if os.environ.get("OPENCODE_DATA_DIR"):
        return os.path.join(os.environ["OPENCODE_DATA_DIR"], "opencode.db")
    xdg = os.environ.get("XDG_DATA_HOME", os.path.join(Path.home(), ".local", "share"))
    return os.path.join(xdg, "opencode", "opencode.db")

def query_via_sqlite_fallback(sql: str, db_path: str) -> list:
    """Fallback Python sqlite3 ?mode=ro — somente se opencode CLI indisponível."""
    import sqlite3
    uri = f"file:{db_path}?mode=ro"
    con = sqlite3.connect(uri, uri=True)
    try:
        con.row_factory = sqlite3.Row
        cur = con.execute(sql)
        cols = [d[0] for d in cur.description] if cur.description else []
        rows = []
        for row in cur.fetchall():
            rows.append({c: row[c] for c in cols})
        return rows
    finally:
        con.close()

def try_query(sql: str) -> list:
    try:
        return run_opencode_json(sql)
    except (FileNotFoundError, RuntimeError) as e:
        # tenta fallback sqlite se opencode não existir
        if "No such file" in str(e) or "not found" in str(e).lower() or "opencode" in str(e):
            db = db_path_fallback()
            if os.path.exists(db):
                return query_via_sqlite_fallback(sql, db)
        raise

def fmt_ts(ts) -> str:
    if ts is None:
        return "[Dado Indisponível]"
    try:
        v = int(ts)
    except (ValueError, TypeError):
        return str(ts)
    if v > 1e14:  # micros
        v = v / 1e6
    elif v > 1e12:  # millis (schema atual v1.18.23)
        v = v / 1e3
    # SQL helper alternativo: datetime(v/1000,'unixepoch','localtime') — aqui usamos Python astimezone()
    return datetime.fromtimestamp(v).astimezone().strftime("%d/%m/%Y %H:%M")

def escape_title(s: str | None, limit: int = 120) -> str:
    if s is None or str(s).strip() == "":
        return "[Dado Indisponível]"
    # remove quebras, colapsa espaços
    t = re.sub(r"[\r\n]+", " ", str(s))
    t = re.sub(r"\s{2,}", " ", t).strip()
    # escape obrigatório p/ Markdown table — ordem importa: \ antes de |
    t = t.replace("\\", "\\\\").replace("|", "\\|")
    if len(t) > limit:
        t = t[:limit].rstrip() + "…"
    if not t:
        return "[Dado Indisponível]"
    return t

def main():
    p = argparse.ArgumentParser(description="Lista sessões do OpenCode em Markdown (bundle da skill list-past-sessions)")
    p.add_argument("--limit", type=int, default=DEFAULT_LIMIT, help="quantidade máxima (default 50)")
    p.add_argument("--offset", type=int, default=0, help="offset p/ paginação (default 0)")
    p.add_argument("--scope", choices=["current", "all"], default=DEFAULT_SCOPE,
                   help="current=isola por worktree == realpath(pwd) (default), all=todos os projetos incl. global")
    p.add_argument("--worktree", type=str, default=None,
                   help="sobrescreve detecção de projeto (default: realpath(pwd))")
    p.add_argument("--order-by", choices=["updated", "created"], default="updated",
                   help="ordenação: updated=time_updated DESC (mais recente primeiro, default), created=time_created DESC")
    p.add_argument("--json-out", type=str, default=None,
                   help="opcional: salva JSON bruto em arquivo além do Markdown stdout")
    args = p.parse_args()

    if args.limit < 0 or args.offset < 0:
        print("error: --limit/--offset devem ser >=0", file=sys.stderr)
        sys.exit(2)

    # 1) detecção de projeto
    worktree = os.path.realpath(args.worktree) if args.worktree else os.path.realpath(os.getcwd())
    projects = []
    project_table_exists = True
    try:
        projects = try_query("SELECT id, worktree, name FROM project ORDER BY worktree")
        if not isinstance(projects, list):
            projects = []
    except Exception as e:
        # schema antigo sem tabela project
        if "no such table: project" in str(e).lower():
            project_table_exists = False
            projects = []
        else:
            print(f"error ao consultar project: {e}", file=sys.stderr)
            sys.exit(1)

    project_id = None
    project_id_short = "n/a"
    scope_effective = args.scope
    header_worktree = worktree if args.scope == "current" else "all"

    if args.scope == "current" and project_table_exists:
        for pr in projects:
            wt = pr.get("worktree")
            # realpath já normalizado; compara exato
            if wt and os.path.realpath(wt) == worktree:
                project_id = pr.get("id")
                break
        if project_id:
            project_id_short = project_id[:4] + "..." if len(project_id) > 4 else project_id
        else:
            # sem match -> 0 sessões neste worktree
            # mantém mensagem exata do passo 8, mas com dica em stderr
            print(f"Nenhuma sessão de conversa anterior foi localizada.", file=sys.stdout)
            print(f"# dica: worktree '{worktree}' não encontrado em project; tente --scope all", file=sys.stderr)
            sys.exit(0)
    elif args.scope == "current" and not project_table_exists:
        # sem isolamento
        scope_effective = "current(no-project-table)"
        header_worktree = worktree + " (sem tabela project)"

    # 2) COUNT(*) filtrado (para header total) + SELECT paginado
    where = f"WHERE s.project_id = '{project_id}'" if project_id else ""
    # scope=all → sem WHERE
    if args.scope == "all":
        where = ""

    # ordenação por time_updated (mais recente primeiro, default) ou time_created
    if args.order_by == "created":
        order_clause = "ORDER BY s.time_created DESC, s.time_updated DESC"
    else:
        order_clause = "ORDER BY s.time_updated DESC, s.time_created DESC"

    count_sql = f"SELECT COUNT(*) as total FROM session s {where};"
    select_sql = (
        "SELECT s.id, s.title, s.time_created, s.time_updated as time_final "
        "FROM session s "
        f"{where} "
        f"{order_clause} "
        f"LIMIT {args.limit} OFFSET {args.offset};"
    )
    # Para nome: COALESCE(title, primeiro session_input.prompt) — faz fallback leve se title vazio
    # Evita escanear session_message.data (caro). Se quiser mais completo, descomentar join.
    # Mantemos query simples por performance; title vazio será marcado [Dado Indisponível] e pode ser
    # enriquecido com subquery opcional: (SELECT si.prompt FROM session_input si WHERE si.session_id=s.id ORDER BY si.time_created ASC LIMIT 1)
    # Para não quebrar paginação, enriquecemos em Python se necessário, com 1 query extra por linha sem title.

    try:
        count_rows = try_query(count_sql)
        total = int(count_rows[0].get("total", 0)) if count_rows else 0
    except Exception as e:
        print(f"error COUNT: {e}\nSQL: {count_sql}", file=sys.stderr)
        sys.exit(1)

    # --- hint "hoje" para scope=current: breakdown por projeto via GROUP BY (Q1:a, Q3:a, Q5:b) ---
    hoje_all = None
    hoje_outros = None
    hoje_breakdown_str = None  # ex: "2 opencode-skills, 1 fretes, 1 global"
    if args.scope == "current" and project_table_exists:
        try:
            # calcula janela de hoje 00:00-24:00 no timezone local (astimezone)
            now_local = datetime.now().astimezone()
            start_local = now_local.replace(hour=0, minute=0, second=0, microsecond=0)
            end_local = start_local.replace(hour=0, minute=0, second=0, microsecond=0) + __import__("datetime").timedelta(days=1)
            start_ms = int(start_local.timestamp() * 1000)
            end_ms = int(end_local.timestamp() * 1000)
            # GROUP BY project_id no range de hoje — usa índice session(time_updated)
            # Q3:a todos ordenados c DESC; nome via basename(worktree) ou global
            group_sql = (
                "SELECT s.project_id, p.worktree, p.name, COUNT(*) as c "
                "FROM session s LEFT JOIN project p ON p.id = s.project_id "
                f"WHERE s.time_updated >= {start_ms} AND s.time_updated < {end_ms} "
                "GROUP BY s.project_id ORDER BY c DESC"
            )
            group_rows = try_query(group_sql)
            if isinstance(group_rows, list) and group_rows:
                # mapeia project_id -> label legível
                def label_for(r):
                    wt = r.get("worktree")
                    pid = r.get("project_id")
                    if pid == "global" or wt == "/":
                        return "global"
                    if wt:
                        base = os.path.basename(wt.rstrip("/"))
                        if base:
                            return base
                    name = r.get("name")
                    if name and str(name).strip():
                        return str(name).strip()
                    return (pid[:4] + "...") if pid and len(pid) > 4 else (pid or "desconhecido")
                # limite interno 10 para não estourar linha (Q3:a)
                MAX_BREAKDOWN = 10
                parts = []
                c_map = {}
                for r in group_rows[:MAX_BREAKDOWN]:
                    cnt = int(r.get("c", 0))
                    lbl = label_for(r)
                    parts.append(f"{cnt} {lbl}")
                    c_map[r.get("project_id")] = cnt
                if len(group_rows) > MAX_BREAKDOWN:
                    parts.append(f"+{len(group_rows)-MAX_BREAKDOWN} outros")
                hoje_breakdown_str = ", ".join(parts)
                hoje_all = sum(int(r.get("c", 0)) for r in group_rows)
                cur_cnt = c_map.get(project_id, 0) if project_id else 0
                hoje_outros = hoje_all - cur_cnt if hoje_all is not None else None
            else:
                hoje_all = 0
                hoje_outros = 0
                hoje_breakdown_str = ""
        except Exception as e:
            # Q5:b degradação graciosa — warn em stderr, segue sem dica
            print(f"warn: hoje breakdown indisponível: {e}", file=sys.stderr)
            hoje_all = None
            hoje_outros = None
            hoje_breakdown_str = None

    if total == 0:
        # emite dica hoje mesmo quando total==0 se houver sessões hoje em outros projetos
        if hoje_all is not None and hoje_all > 0 and hoje_breakdown_str is not None:
            print(f"<!-- hoje:{hoje_all} em scope:all ({hoje_breakdown_str}) — use --scope all para listar -->")
            if hoje_outros is not None and hoje_outros > 0:
                print(f"dica: {hoje_outros} sessões hoje em outros projetos (hoje all:{hoje_all} — {hoje_breakdown_str}) — use --scope all", file=sys.stderr)
        print("Nenhuma sessão de conversa anterior foi localizada.")
        sys.exit(0)

    try:
        rows = try_query(select_sql)
        if not isinstance(rows, list):
            rows = []
    except Exception as e:
        print(f"error SELECT: {e}\nSQL: {select_sql}", file=sys.stderr)
        sys.exit(1)

    if args.json_out:
        with open(args.json_out, "w", encoding="utf-8") as f:
            json.dump(rows, f, ensure_ascii=False, indent=2)

    # Enriquecer title vazio com session_input.prompt (1 query por linha sem title, limitado ao LIMIT)
    titles_to_fetch = [r for r in rows if not (r.get("title") and str(r.get("title")).strip())]
    prompt_map = {}
    if titles_to_fetch:
        # batch: busca prompts para ids sem title
        ids = ",".join(f"'{r['id']}'" for r in titles_to_fetch)
        # usa subquery por id para pegar primeiro prompt
        for r in titles_to_fetch:
            try:
                pr = try_query(
                    f"SELECT prompt FROM session_input WHERE session_id='{r['id']}' ORDER BY time_created ASC LIMIT 1"
                )
                if pr and pr[0].get("prompt"):
                    prompt_map[r["id"]] = pr[0]["prompt"]
            except Exception:
                pass

    # 3) formata Markdown
    exibindo = len(rows)
    # header_worktree: para scope all, mostra "all"; para current, worktree real
    proj_label = header_worktree if args.scope == "all" else worktree
    # abreviação id
    pid_disp = project_id_short if project_id else ("all" if args.scope=="all" else "n/a")
    # Q7 sempre visível additive: inclui order
    order_disp = args.order_by
    print(f"<!-- projeto:{proj_label} (id {pid_disp}) — total:{total} exibindo:{exibindo} scope:{scope_effective} limit:{args.limit} offset:{args.offset} order:{order_disp} -->")
    # Q2:b segundo comentário + stderr dica quando scope=current e hoje_outros>0 (Q4:a)
    if args.scope == "current" and hoje_outros is not None and hoje_outros > 0 and hoje_breakdown_str:
        # breakdown já ordenado c DESC, limitado 10
        print(f"<!-- hoje:{hoje_all} em scope:all ({hoje_breakdown_str}) — {hoje_outros} em outros projetos — use --scope all para listar -->")
        print(f"dica: {hoje_outros} sessões hoje em outros projetos (hoje all:{hoje_all} — {hoje_breakdown_str}) — use --scope all", file=sys.stderr)
    print("| ID | Nome da Sessão | Data de Início | Data Final |")
    print("| :--- | :--- | :--- | :--- |")
    for r in rows:
        sid = r.get("id", "[Dado Indisponível]")
        raw_title = r.get("title")
        if not (raw_title and str(raw_title).strip()):
            raw_title = prompt_map.get(r.get("id"), "[Dado Indisponível]")
        title = escape_title(raw_title)
        inicio = fmt_ts(r.get("time_created"))
        fim = fmt_ts(r.get("time_final") if "time_final" in r else r.get("time_updated"))
        # sid preservado sem truncar; title já escapado
        print(f"| {sid} | {title} | {inicio} | {fim} |")

if __name__ == "__main__":
    main()
