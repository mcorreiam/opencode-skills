# Charts

Create and manage charts with `addChart` on the same `batchUpdate`
endpoint. Tested on `TesteStats` (sheetId `1934443130`): column chart
`1324520033` (`R$/mês por pessoa`), pie chart `64878206` (`Status`).
Sources: docs `samples/charts`.

## Column chart

```json
{"addChart": {"chart": {
  "spec": {"title": "R$/mês por pessoa",
    "basicChart": {"chartType": "COLUMN", "legendPosition": "BOTTOM_LEGEND",
      "axis": [{"position": "BOTTOM_AXIS", "title": "Nome"}, {"position": "LEFT_AXIS", "title": "R$/mês"}],
      "domains": [{"domain": {"sourceRange": {"sources": [
        {"sheetId": 1934443130, "startRowIndex": 0, "endRowIndex": 6, "startColumnIndex": 0, "endColumnIndex": 1}]}}}],
      "series": [{"series": {"sourceRange": {"sources": [
        {"sheetId": 1934443130, "startRowIndex": 0, "endRowIndex": 6, "startColumnIndex": 2, "endColumnIndex": 3}]}},
        "targetAxis": "LEFT_AXIS"}],
      "headerCount": 1}},
  "position": {"overlayPosition": {"anchorCell": {"sheetId": 1934443130, "rowIndex": 10, "columnIndex": 5},
    "widthPixels": 600, "heightPixels": 371}}}}}
```

Include the header row in the ranges with `headerCount: 1`.
`chartType` values include `COLUMN`, `BAR`, `LINE`, `AREA`, `SCATTER`.
Omit `chartId`; the API assigns one.

## Pie chart

`spec.pieChart` replaces `basicChart`:

```json
{"pieChart": {"legendPosition": "RIGHT_LEGEND",
  "domain": {"sourceRange": {"sources": [RANGE_OF_LABELS]}},
  "series": {"sourceRange": {"sources": [RANGE_OF_VALUES]}}}}
```

Aggregate the slices first (counter helpers or `QUERY` in
[locale.md](locale.md)) — the pie reads plain ranges.

## Manage

- List: `GET ...?fields=sheets(charts)` returns `chartId` + `spec`.
- Edit: `updateChartSpec` replaces the full `spec`; partial edits are
  not possible.
- Move/resize: `updateEmbeddedObjectPosition` with a `fields` mask.
- Delete: `deleteEmbeddedObject` with `objectId: chartId`.
- API limitation: some settings (background color, axis label
  formatting) are inaccessible, and edits can reset them.
