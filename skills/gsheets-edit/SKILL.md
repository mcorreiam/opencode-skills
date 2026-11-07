---
name: gsheets-edit
description: Google Sheets via API USER_ENTERED. Use when writing formulas or comma-decimal numbers, managing tabs, styling tables with filters, building charts and stats, or when MCP gsheets_update_cell stores formulas as text.
---

# Edit Google Sheets

Write with the Sheets REST API using `valueInputOption=USER_ENTERED`,
authenticated with the MCP's own OAuth material. The MCP writer hardcodes
`RAW` (`@isaacphi/mcp-gdrive/dist/tools/gsheets_update_cell.js:30`):
`=1+1` lands as text, and `"50"` lands as text that `SUM` silently skips
(the live `O11=0` incident). Read through the `drive` MCP
(`gsheets_read`); verify with `valueRenderOption`.

## Steps

### 1. Read before writing

Call `gsheets_read` or `GET spreadsheets.values/{range}` first. State the
tab, the exact range, and which cells hold values.

Done when: tab, range, and current values are stated.

### 2. Write with USER_ENTERED

`POST`/`PUT` to `sheets.googleapis.com/v4/spreadsheets/{id}/...` with
`valueInputOption=USER_ENTERED`:

- `GOOGLE_DESKTOP_CLIENT_ID` / `GOOGLE_DESKTOP_CLIENT_SECRET` from env
- refresh token in `/home/marco/.config/mcp-gdrive/.gdrive-server-credentials.json`
- refresh via `POST https://oauth2.googleapis.com/token` (snippet in
  Reference), use the `access_token` as `Authorization: Bearer`

Single range:

```bash
curl -X PUT \
  "https://sheets.googleapis.com/v4/spreadsheets/$SID/values/$RANGE?valueInputOption=USER_ENTERED" \
  -H "Authorization: Bearer $AT" -H "Content-Type: application/json" \
  -d '{"values":[["=SOMA(A1:B1)"]]}'
```

Batch (preferred, one round-trip):

```bash
curl -X POST \
  "https://sheets.googleapis.com/v4/spreadsheets/$SID/values:batchUpdate" \
  -H "Authorization: Bearer $AT" -H "Content-Type: application/json" \
  -d '{"valueInputOption":"USER_ENTERED","data":[
    {"range":"Aba!O2:O17","values":[["=SOMA(D2:N2)"],["=SOMA(D3:N3)"]]},
    {"range":"Aba!P2:P17","values":[["=C2*11"],["=C3*11"]]}
  ]}'
```

Done when: the response reports the expected `updatedCells` /
`totalUpdatedCells`.

### 3. Verify with render options

Fetch the range three ways: `FORMULA` shows stored expressions
(`=SUM(...)`); `UNFORMATTED_VALUE` separates real numbers (JSON numbers)
from text strings (the bug signal); `FORMATTED_VALUE` matches the pt-BR
UI. Full semantics and the pt-BR rules behind them: [locale.md](locale.md).

Done when: `FORMULA` holds the intended expression, `UNFORMATTED_VALUE`
holds numbers where numbers belong, `FORMATTED_VALUE` matches the UI.

### 4. Keep the browser read-only

`browser_navigate` to the sheet URL plus `browser_take_screenshot` only;
the API remains the only writer. The screenshot confirms the grid matches
the API reads.

Done when: screenshot values match the `FORMATTED_VALUE` read.

### 5. Style tables → [design.md](design.md)

Headers, banding, filters, validation, currency, native tables, and the
style gallery live in [design.md](design.md) (tested: `TesteDesign`,
`TesteEstilos`, `TesteTabela`). `batchUpdate` requests apply in order and
atomically; `GridRange` indexes are 0-based, end-exclusive.

Done when: `GET ...?fields=sheets(properties,bandedRanges,basicFilter)`
shows the intended state, and the screenshot shows it.

### 6. Chart and analyze → [charts.md](charts.md), [locale.md](locale.md)

Charts ([charts.md](charts.md), tested: `TesteStats`) and aggregations
(pt-BR stats + `QUERY` in [locale.md](locale.md)).

Done when: `GET ...?fields=sheets(charts)` lists the charts, stats read
back the expected values, and the screenshot shows the rendered charts.

## Reference

### Sheet tabs

List: `GET /v4/spreadsheets/{id}?fields=sheets.properties` returns
`sheetId`, `title`, `gridProperties`. Add:
`{"requests":[{"addSheet":{"properties":{"title":"Name"}}}]}` returns the
new `sheetId`. Delete: `{"requests":[{"deleteSheet":{"sheetId":ID}}]}`.
Prefix ranges with the tab: `Aba!A1:B1`.

### Clear

`POST /v4/spreadsheets/{id}/values/{range}:clear` with body `{}` removes
values. Empty string via update also works for single cells.

### Branch references

- [locale.md](locale.md) — writing values and formulas in pt-BR, stats, `QUERY`.
- [design.md](design.md) — styling tables, filters, gallery, native tables.
- [charts.md](charts.md) — creating and managing charts.

### Auth refresh (python stdlib)

```python
import json, os, urllib.request, urllib.parse
saved = json.load(open("/home/marco/.config/mcp-gdrive/.gdrive-server-credentials.json"))
data = urllib.parse.urlencode({
  "client_id": os.environ["GOOGLE_DESKTOP_CLIENT_ID"],
  "client_secret": os.environ["GOOGLE_DESKTOP_CLIENT_SECRET"],
  "refresh_token": saved["refresh_token"], "grant_type": "refresh_token",
}).encode()
at = json.load(urllib.request.urlopen(
  urllib.request.Request("https://oauth2.googleapis.com/token", data=data),
  timeout=30))["access_token"]
```

Print only counts (`updatedCells`, `clearedRange`), never the token.
