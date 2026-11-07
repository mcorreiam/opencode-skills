# Locale and formulas (pt-BR)

Rules for writing values and formulas the pt-BR sheet parses as intended.
All facts below were reproduced on live sheets (`Mensalidades`,
`TesteSkill`, `TesteStats`).

## Write mode

| write path | cell input | stored as | evaluates |
|---|---|---|---|
| MCP `gsheets_update_cell` (`RAW`) `=1+1` | text `=1+1` | string | no |
| API `USER_ENTERED` `=1+1` | formula | `2` | yes |
| MCP (`RAW`) `77,77` | text `77,77` | string | `SUM` ignores it |
| API `USER_ENTERED` `77,77` | number | yes |

Sources: Sheets guides `values` + `ValueRenderOption` reference
(developers.google.com/workspace/sheets/api).

## pt-BR facts

- Decimal separator is comma: write `10,50`, `56,78`. The string `12.34`
  stays text in a pt-BR sheet; the dot is not a decimal separator.
- Display trims trailing zeros: stored `10.5` renders `10,5`.
- Formula argument separator is semicolon: `=SOMA(A1;B1)` works,
  `=SOMA(A1,B1)` returns `#ERROR! (Formula parse error.)`.
- Range operator is still colon: `=SOMA(D2:N2)`, `=SOMA(O2:O17)`.
- Function names in either language work on write; reads normalize to
  English: writing `=SOMA(A1:B1)` reads back `=SUM(A1:B1)`, writing
  `=SE(A1>0;"sim";"não")` reads back `=IF(A1>0;"sim";"não")`. The `;`
  separators are preserved.

## Statistics (tested on 50, 75, 50, 50, 75)

| write (pt-BR) | reads back | result |
|---|---|---|
| `=SOMA(C2:C6)` | `=SUM(...)` | 300 |
| `=MÉDIA(C2:C6)` | `=AVERAGE(...)` | 60 |
| `=MEDIANA(C2:C6)` | `=MEDIAN(...)` | 50 |
| `=MÁXIMO(C2:C6)` | `=MAX(...)` | 75 |
| `=MÍNIMO(C2:C6)` | `=MIN(...)` | 50 |
| `=DESVPAD(C2:C6)` | `=STDEV(...)` | 13,69306394 |
| `=CONT.SE(D2:D6;"Pago")` | `=COUNTIF(...)` | 3 |
| `=SOMASE(D2:D6;"Pago";C2:C6)` | `=SUMIF(...)` | 175 |

Counter pattern: `=CONT.SE($D$2:$D$6;I2)` with absolute refs, copied down
per label (`Pago 3, Pendente 2, Atrasado 0`).

## QUERY

Aggregates without helper columns. Separators are `;` outside; SQL commas
stay commas inside the quoted string:

```text
=QUERY(A1:D6;"select D, count(A) group by D label D 'Status', count(A) 'Qtd'";1)
```

Tested result: `Pago 3, Pendente 2` — groups with zero rows (Atrasado)
don't appear. Third arg `1` = one header row. Sources: support
`QUERY function` + Visualization Query Language reference.
