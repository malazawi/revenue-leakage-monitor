# Baseline (Desktop, refreshed, 2026-10-22) - taken BEFORE any file edits

## Totals (no filters)
As Of Date 2026-10-16 | Hours 579876.25 | Late Hours % 0.13774145776792893 | Very Late % 0.017292913789795666 | Avg Entry Lag 4.54846773937269
Standard Value Billed 211871120 | Billed Value 179052238.69000015 | Billing Realization 0.8450997884468641
Realization Leakage 32818881.309999853 | Agreed Discounts 12974022.4375 | Write-downs 19844858.872499853
Unbilled WIP 6219976.25 | Aged WIP 90+ 1378155
Open AR 11062458.809999997 | AR 90+ 2960948.660000001 | AR 90+ % 0.26765737263793726
Billed 179052238.69 | Write-offs 2155424.1299999994
Cash Received 168936458.33 | Unapplied Cash 3102102.58 | Unapplied Cash 14+ 2794797.69 | Slow-Applied Cash 6178790.12

## Pre-checks
- Write-off amount with blank write_off_date: 0; before Date start: 0; after Date end: blank (none)
- Write-off rows with date: 177 = rows with amount > 0 (177). Max write_off_date 2026-10-15; Date table 2024-01-01..2026-10-31
- invoices: 16365 rows, 16365 distinct invoice_id, no blank ids
- time_entries with non-blank invoice_id: 183353; orphans (no matching invoice): none (blank)
- Cash measures identical across every Practice and Fee type (confirms they are unaffected by those slicers); they vary by Industry.

## Queries to rerun for the diff (all 22 measures)
Totals; by engagements[practice]; by engagements[fee_type]; by clients[industry]; by Date[Year-Month]; Billing Realization/Hours/Write-downs by time_entries[Entry Timeliness].
Expected change after #3: ONLY Write-offs by Date[Year-Month] (re-bucketed by write-off month). Everything else identical.
Expected after #5: one new measure; all others identical. #2 and #1: no measure changes.
