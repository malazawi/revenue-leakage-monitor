# After fixes (Desktop reopened and refreshed, 2026-10-22)

Compared with `baseline.md`. Fixes applied: #5 new measure, #3 write-off date relationship + `Write-offs`, #2 inactive `time_entries -> invoices` relationship, #1 report-only (interactions and labels).

Live model when this comparison was run: 12 relationships (10 before + 2 inactive), 23 measures (22 before + `Operational Realization`). Fix #2 was reverted afterwards (see Known side effects), so the final model has 11 relationships (one inactive).

## Diff summary

| Check | Result |
|---|---|
| 21 original measures, firm-wide totals | Identical to baseline, every digit |
| 21 original measures by Practice, Fee type, Industry | Identical to baseline (including `Write-offs`, which has no date filter there) |
| Billing Realization / Hours / Write-downs by Entry Timeliness | Identical |
| All measures by month except `Write-offs` | Identical |
| `Write-offs` by month | **Changed, as intended** (now by write-off month) |
| `Write-offs` total | $2,155,424.13 before and after; sum of months also $2,155,424.13 |
| `Operational Realization` | New |
| Cash measures across Practice / Fee type | Still the same value for every Practice and Fee type (all-practice figure) |

## Write-offs: by month, before -> after

Invoice month was used before; write-off month is used now. Months not listed were `blank` before and after.

| Month | Before | After |
|---|---|---|
| 2024-02 .. 2024-12 | $0.04M-$0.22M per month (invoice month) | blank |
| 2025-01 | $142,713 | blank |
| 2025-02 | $88,001 | $66,398 |
| 2025-03 | $173,342 | $6,856 |
| 2025-04 | $171,787 | $55,679 |
| 2025-05 | $55,460 | $123,108 |
| 2025-06 | $49,712 | $26,160 |
| 2025-07 | $89,502 | $204,008 |
| 2025-08 | $123,215 | $102,914 |
| 2025-09 | $38,034 | $153,832 |
| 2025-10 | $0 | $101,064 |
| 2025-11 | $0 | $89,489 |
| 2025-12 | $0 | $93,841 |
| 2026-01 | $0 | $189,108 |
| 2026-02 | $0 | $71,566 |
| 2026-03 | $0 | $193,361 |
| 2026-04 | $0 | $145,058 |
| 2026-05 | $0 | $51,146 |
| 2026-06 | $0 | $177,466 |
| 2026-07 | $0 | $40,719 |
| 2026-08 | $0 | $91,524 |
| 2026-09 | $0 | $67,395 |
| 2026-10 | $0 | $104,733 |
| (blank date) | n/a | $0 |

Write-offs now start in 2025-02 (about a year after the first invoices) instead of the invoice months, and appear in 2025-10 onward instead of showing $0.

## Operational Realization (new)

| Scope | Billing Realization | Operational Realization | Hand-calculated expectation |
|---|---|---|---|
| Firm-wide | 84.5% | 90.0% (0.90023) | 90.0% |
| Hourly | 90.8% | 96.8% | 96.8% |
| Capped | 79.3% | 84.4% | 84.4% |
| Fixed Fee | 67.5% | 71.8% | 71.8% |

By practice: 89.6% (Operations Excellence) to 90.8% (Technology Advisory).

## Fix #2 check (before it was reverted)

The inactive `time_entries[invoice_id] -> invoices[invoice_id]` relationship loads without error. A test query using `USERELATIONSHIP` ran with no ambiguity error:
- Billed time entries on invoices in the "120+" aging bucket: 2,719 rows.
- Hours on invoices with an open balance: 36,249.5 of 579,876.25 total.

Nothing in the report uses this relationship yet.

## New behaviour to be aware of

1. **Blank Date row for `Write-offs`.** Because `Write-offs` now uses the write-off date, a query grouped by `Date` returns one extra blank-date row with `Write-offs` = $0 (invoices with no write-off date). It only shows if `Write-offs` is placed in a visual with a Date field. The report's Write-offs card has no date field, so nothing changes today.
2. **Extra blank row for Practice and Fee type.** A query that grouped by `engagements[practice]` or `engagements[fee_type]` and included a cash measure returned an extra blank row carrying only the all-practice cash figure. The baseline had no such row, and the Industry query never did. A data check found no orphan rows, so the data was not the cause. This was later traced to fix #2; see below.

## Known side effects

### Blank Date row from #3 (kept)
`Write-offs` now uses the inactive `invoices[write_off_date] -> Date[Date]` relationship. Invoices with no write-off date (16,188 of 16,365; only 177 have one) fall on the blank member of `Date`, so any visual that puts `Write-offs` next to a Date field gets one extra blank-date row showing $0. The current report is not affected, because the Write-offs card has no date field. If you add a month chart of write-offs, filter the blank out (for example with a visual-level filter on the Date field).

### Fix #2 reverted (inactive `time_entries[invoice_id] -> invoices[invoice_id]`)
- **Why:** with this relationship in the model, queries by Practice or Fee type that included a cash measure gained an extra blank row (see item 2 above).
- **Test:** after the revert and a refresh, `SUMMARIZECOLUMNS(engagements[practice], [Hours], [Cash Received])` returned 5 rows (no blank row), and the fee-type version returned 3. The blank row is gone, so fix #2 was the cause.
- **Likely mechanism (inferred, not proven):** 5,453 of 188,806 time entries (the unbilled WIP, 16,865 hours) have a blank `invoice_id`. Blank keys on the "many" side land on a virtual blank member of the "one" side (`invoices`). The baseline had the same blank keys, so they only matter once the relationship exists. Why this surfaced as a blank Practice and Fee type row, but not a blank Industry row, was not established.
- **Cost of the revert:** none today. No measure or visual used the relationship.
- **If it is added again:** expect a blank `invoices` member holding the unbilled time. Re-run the Practice and Fee type check above before keeping it. Alternatives are a bridge or filtered key (for example a column that is blank-free for billed rows only) or doing the link inside a measure with `TREATAS`.

### Cash cards
The cash cards remain unaffected by the Practice and Fee type slicers. The report-level interactions and labels from #1 are separate from the model and unchanged by the revert. Verified in Power BI Desktop's UI: changing the Practice or Fee type slicer does not change the cash cards, and the new labels ("Unapplied cash 14+ days (all practices & fee types)" and "Cash application backlog (all practices & fee types)") fit.
