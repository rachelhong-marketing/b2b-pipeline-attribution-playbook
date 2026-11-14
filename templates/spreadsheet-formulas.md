# Spreadsheet formulas

For teams that report from exported CRM data in Excel or Google Sheets. Column letters are examples.

## Funnel and cost

Assume one row per campaign: A = campaign, B = cost, C = leads, D = MQLs, E = leads at target accounts.

| Metric | Formula |
|---|---|
| Lead-to-MQL rate | `=IFERROR(D2/C2, 0)` |
| Cost per lead | `=IFERROR(B2/C2, 0)` |
| Cost per MQL | `=IFERROR(B2/D2, 0)` |
| % of leads from target accounts | `=IFERROR(E2/C2, 0)` |

## Sourced vs. influenced

Assume an opportunity export: A = opportunity ID, B = amount, C = primary campaign (blank if none), D = number of influencing campaigns.

| Metric | Formula |
|---|---|
| Marketing-sourced pipeline | `=SUMIF(C:C, "<>", B:B)` |
| % of pipeline marketing sourced | `=SUMIF(C:C, "<>", B:B) / SUM(B:B)` |
| % of deals marketing influenced | `=COUNTIF(D:D, ">0") / COUNTA(A:A)` (subtract 1 from COUNTA if row 1 is a header) |

## Even-split credit

Assume a touch export with one row per deal and campaign: A = opportunity ID, B = campaign, C = deal amount.

| Metric | Formula |
|---|---|
| Credit for this row | `=C2 / COUNTIF(A:A, A2)` |
| Total credit by campaign | Pivot table: rows = campaign, values = sum of credit |
