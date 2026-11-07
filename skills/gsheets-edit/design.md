# Table design

Styling goes through `POST /v4/spreadsheets/{id}:batchUpdate` with a
`requests[]` array (applied in order, atomically — one invalid request
fails the whole batch). Resolve the numeric `sheetId` first
(`GET ...?fields=sheets.properties`); `GridRange` indexes are 0-based,
end-exclusive (`A1:D6` = rows `0–6`, cols `0–4`). Tested on
`TesteDesign` (sheetId `784369592`) and `TesteEstilos` (`1162299639`).

## Header + freeze

Always bound the columns: omitting `startColumnIndex`/`endColumnIndex`
paints the entire row, leaking color past the table (seen live on
`TesteDesign`; cleanup recipe below).

```json
{"repeatCell": {"range": {"sheetId": 784369592, "startRowIndex": 0, "endRowIndex": 1, "startColumnIndex": 0, "endColumnIndex": 4},
  "cell": {"userEnteredFormat": {"backgroundColor": {"red": 0.13, "green": 0.13, "blue": 0.13},
    "horizontalAlignment": "CENTER",
    "textFormat": {"foregroundColor": {"red": 1.0, "green": 1.0, "blue": 1.0}, "fontSize": 11, "bold": true}}},
  "fields": "userEnteredFormat(backgroundColor,textFormat,horizontalAlignment)"}},
{"updateSheetProperties": {"properties": {"sheetId": 784369592, "gridProperties": {"frozenRowCount": 1}},
  "fields": "gridProperties.frozenRowCount"}}
```

`fields` is a mask: only listed format paths change, the rest is kept.

Cleanup for a leaked header row (reset `E1` onward to default):

```json
{"repeatCell": {"range": {"sheetId": 784369592, "startRowIndex": 0, "endRowIndex": 1, "startColumnIndex": 4},
  "cell": {"userEnteredFormat": {"backgroundColor": {"red": 1.0, "green": 1.0, "blue": 1.0},
    "horizontalAlignment": "LEFT",
    "textFormat": {"foregroundColor": {"red": 0.0, "green": 0.0, "blue": 0.0}, "fontSize": 10, "bold": false}}},
  "fields": "userEnteredFormat(backgroundColor,textFormat,horizontalAlignment)"}}
```

## Banding

Put `addBanding` before the header `repeatCell` (banding would otherwise
paint over the header):

```json
{"addBanding": {"bandedRange": {
  "range": {"sheetId": 784369592, "startRowIndex": 0, "endRowIndex": 6, "startColumnIndex": 0, "endColumnIndex": 4},
  "rowProperties": {"headerColor": {"red": 0.13, "green": 0.13, "blue": 0.13},
    "firstBandColor": {"red": 1.0, "green": 1.0, "blue": 1.0},
    "secondBandColor": {"red": 0.95, "green": 0.95, "blue": 0.95}}}}}
```

## Filter

One basic filter per sheet; the range must include the header row:

```json
{"setBasicFilter": {"filter": {"range": {"sheetId": 784369592, "startRowIndex": 0, "endRowIndex": 6, "startColumnIndex": 0, "endColumnIndex": 4}}}}
```

Remove with `{"clearBasicFilter": {"sheetId": 784369592}}`. Verify with
`GET ...?fields=sheets(properties,bandedRanges,basicFilter)`.

## Data formats

Currency on `C2:C6` (renders `R$50,00`):

```json
{"repeatCell": {"range": {"sheetId": 784369592, "startRowIndex": 1, "endRowIndex": 6, "startColumnIndex": 2, "endColumnIndex": 3},
  "cell": {"userEnteredFormat": {"numberFormat": {"type": "CURRENCY", "pattern": "\"R$\"#,##0.00"}}},
  "fields": "userEnteredFormat.numberFormat"}}
```

Dropdown on `D2:D6`:

```json
{"setDataValidation": {"range": {"sheetId": 784369592, "startRowIndex": 1, "endRowIndex": 6, "startColumnIndex": 3, "endColumnIndex": 4},
  "rule": {"condition": {"type": "ONE_OF_LIST", "values": [
    {"userEnteredValue": "Pago"}, {"userEnteredValue": "Pendente"}, {"userEnteredValue": "Atrasado"}]},
    "showCustomUi": true, "strict": true, "inputMessage": "Escolha o status"}}}
```

Fit columns: `{"autoResizeDimensions": {"dimensions":
{"sheetId": 784369592, "dimension": "COLUMNS", "startIndex": 0, "endIndex": 4}}}`.

Sources: API samples `formatting` and `data`, guides `filters`, `tables`.

## Style gallery (Excel quick styles)

Sheets has no named style gallery in the API. Built-in UI paths:
`Format > Alternating colors` (default presets + custom colors,
auto-applied to new rows) and `Insert > Pre-built table` /
`Format > Convert to table` (templates with column types and filters).
Via API every style is explicit RGB in `addBanding` + header `repeatCell`.

Palettes (`headerColor` / `firstBand` / `secondBand`, header text white
bold 11 centered):

| Style (Excel equiv.) | header | band 1 | band 2 | tested on |
|---|---|---|---|---|
| Escuro (Média preta) | 0.13,0.13,0.13 | 1,1,1 | 0.95,0.95,0.95 | TesteDesign |
| Azul Média | 0.18,0.46,0.71 | 1,1,1 | 0.87,0.92,0.97 | TesteEstilos |
| Verde Clara | 0.23,0.55,0.34 | 1,1,1 | 0.90,0.95,0.90 | — |
| Laranja Média | 0.91,0.49,0.13 | 1,1,1 | 0.98,0.93,0.88 | — |
| Cinza Clara | 0.42,0.42,0.42 | 1,1,1 | 0.95,0.95,0.95 | — |

Excel → Sheets mapping:

| Excel option | Sheets equivalent |
|---|---|
| Linha de Cabeçalho | header `repeatCell` + `frozenRowCount: 1` |
| Linha de Totais | total row with `SOMA` formulas, or table footer toggle |
| Linhas em Tiras | banding `rowProperties` |
| Colunas em Tiras | banding `columnProperties` |
| Primeira/Última coluna | `repeatCell` on that column range |
| Botão Filtro | `setBasicFilter`, or native table filter |
| Estilos Rápidos | palettes above (API has no named presets) |

## Native tables (tested: TesteTabela `Curujas`, sheetId `225854180`)

`addTable` creates a structured table (name, column types, filter UI,
Sheets-owned banded look):

```json
{"addTable": {"table": {"name": "Curujas", "tableId": "curujas1",
  "range": {"sheetId": 225854180, "startRowIndex": 0, "endRowIndex": 6, "startColumnIndex": 0, "endColumnIndex": 4},
  "columnProperties": [
    {"columnIndex": 0, "columnName": "Nome", "columnType": "TEXT"},
    {"columnIndex": 1, "columnName": "Time", "columnType": "TEXT"}]}}}
```

Verified `columnType: TEXT`; docs example uses `PERCENT` plus `DROPDOWN`
(`DROPDOWN` requires a `dataValidationRule` with `ONE_OF_LIST`).
Grow via `UpdateTableRequest` (range, footer toggle),
`InsertRangeRequest`/`InsertDimensionRequest`, append via
`AppendCellsRequest` with `tableId`. Remove with `deleteTable` (table +
contents) or `deleteBanding` (keeps data).
