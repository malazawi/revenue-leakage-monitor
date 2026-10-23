# Run 1 answers

Source: open Power BI Desktop model "Revenue Leakage Monitor" (local instance, port 60518). All figures come from DAX run against that model only.

**Model facts that affect every answer**
- Data runs 2024-01-01 to **2026-10-16**. The model's `As Of Date` is 2026-10-16, and all aging columns (WIP Age, Days Outstanding, Days To Apply) are measured against it, not against today (2026-10-23).
- Two realization definitions exist in the model:
  - **Billing Realization** = Billed Value / Standard Value Billed. Agreed discounts count as leakage. This is the model's headline measure, and I use it unless a question says otherwise.
  - **Operational Realization** = Billed Value / (Standard Value Billed − Agreed Discounts). Agreed discounts are excluded.
- Figures are rounded for readability. The raw values are in the DAX results.

---

## 1. How many hours has the firm logged in total?
**579,876.25 hours** (2024-01-01 to 2026-10-16).
```dax
EVALUATE ROW("Hours", [Hours])   -- SUM(time_entries[hours])
```
Assumption: all time entries count, billed or not.

## 2. What is the firm-wide billing realization?
**84.5%**. Billed value $179,052,239 over standard value billed $211,871,120. Excluding agreed discounts, operational realization is 90.0%.
```dax
EVALUATE ROW("Real", [Billing Realization], "OpReal", [Operational Realization])
```
Assumption: realization is calculated on billed time only. Unbilled WIP is excluded.

## 3. How much in agreed discounts has the firm given?
**$12,974,022**.
```dax
EVALUATE ROW("Disc", [Agreed Discounts])
-- SUMX(billed time entries, standard_value * RELATED(engagements[agreed_discount_pct]))
```
Assumption: this is the model's own definition (standard value × engagement discount %, on billed entries).

## 4. What is the total of write-downs?
**$19,844,859**. This is standard value billed − agreed discounts − billed value, which is the unexplained gap between standard and billed. It is a different thing from AR write-offs (Q12), which total $2,155,424.
```dax
EVALUATE ROW("WD", [Write-downs])
```
Assumption: "write-downs" means the model's `Write-downs` measure, not AR write-offs.

## 5. What is the current open AR?
**$11,062,459**, as of 2026-10-16.
```dax
EVALUATE ROW("OpenAR", [Open AR])   -- SUM(invoices[balance])
```

## 6. How much AR is more than 90 days old?
**$2,960,949**, or 26.8% of open AR. Counting exactly 90 days gives the same total.
```dax
EVALUATE ROW("AR90", [AR 90+])
```
Assumption: age is days since invoice date as of 2026-10-16.

## 7. How much cash has gone unapplied for 14+ days?
**$2,794,798**. The model's measure uses "more than 14 days". Using "14 or more" gives the same figure. Total unapplied cash of any age is $3,102,103, across 297 payments, and 257 of those are 14+ days.
```dax
EVALUATE ROW("Unap14", [Unapplied Cash 14+ Days],
  "Unap14ge", CALCULATE([Cash Received], ISBLANK(payments[applied_date]), payments[Days To Apply] >= 14))
```
Assumption: "unapplied" means `applied_date` is blank. Age runs from received date to 2026-10-16.

## 8. What is the total unbilled WIP?
**$6,219,976**, at standard value.
```dax
EVALUATE ROW("WIP", [Unbilled WIP])
```
Assumption: unbilled means the time entry has no `invoice_id`.

## 9. What is billing realization for each fee type?
| Fee type | Billing realization | Operational realization |
|---|---|---|
| Hourly | 90.8% | 96.8% |
| Capped | 79.3% | 84.4% |
| Fixed Fee | 67.5% | 71.8% |

```dax
EVALUATE ADDCOLUMNS(VALUES(engagements[fee_type]), "Real", [Billing Realization], "OpReal", [Operational Realization])
```

## 10. Which practice has the lowest billing realization?
**Risk & Compliance, at 83.9%**. Finance Transformation is almost identical at 83.9% (83.88% vs 83.94%). The practices are tightly clustered.

| Practice | Billing realization |
|---|---|
| Risk & Compliance | 83.88% |
| Finance Transformation | 83.94% |
| Operations Excellence | 84.37% |
| Technology Advisory | 85.03% |
| Transactions | 85.20% |

```dax
EVALUATE ADDCOLUMNS(VALUES(engagements[practice]), "Real", [Billing Realization])
```
Assumption: practice is the engagement's practice (`engagements[practice]`), not the timekeeper's practice in `staff`.

## 11. Which industry has the highest open AR?
**Manufacturing, at $2,208,181**. Next are Financial Services at $1,940,379 and Technology at $1,936,399. Energy is lowest at $670,011.
```dax
EVALUATE ADDCOLUMNS(VALUES(clients[industry]), "OpenAR", [Open AR])
```

## 12. How much was written off in October 2026?
**$104,733**, with write-off dates running through 2026-10-15 (the data ends 2026-10-16).
```dax
EVALUATE ROW("WO", CALCULATE([Write-offs], 'Date'[Year] = 2026, 'Date'[Month Num] = 10))
-- uses the inactive invoices[write_off_date] relationship via USERELATIONSHIP
```
Assumption: write-offs are dated by `write_off_date`, not invoice date.

## 13. How much cash was received in 2025?
**$69,400,301**.
```dax
EVALUATE ROW("Cash2025", CALCULATE([Cash Received], 'Date'[Year] = 2025))
```
Assumption: calendar year, by `received_date`.

## 14. What is realization for very late time entries (30+ days)?
**65.8%** billing realization (70.2% operational), versus 85.7% for on-time entries. Very late entries total 10,028 hours.
```dax
EVALUATE ROW("VL", CALCULATE([Billing Realization], time_entries[entry_lag_days] >= 30))
```
Assumption: "late" means `entry_lag_days`, the days between work date and entry date.

## 15. Which three billing partners hold the most aged WIP (90+ days)?
1. **Patricia Miller**: $467,145
2. **Danielle Johnson**: $352,379
3. **Christopher Davis**: $322,831

The firm total is $1,378,155.
```dax
EVALUATE TOPN(3, ADDCOLUMNS(VALUES(engagements[Billing Partner]), "AgedWIP", [Aged WIP 90+]), [AgedWIP], DESC)
```
Assumption: "90+" uses the model's measure, which is more than 90 days.

## 16. What is billing realization for Manufacturing clients?
**83.8%** (89.1% operational), against 84.5% firm-wide.
```dax
EVALUATE ROW("Mfg", CALCULATE([Billing Realization], clients[industry] = "Manufacturing"))
```

## 17. How much money are we leaving on the table?
This question is ambiguous, so here are the pieces:
- **Realization leakage: $32,818,881.** Standard value billed minus billed value, made up of:
  - $12,974,022 in agreed discounts, which is intentional.
  - $19,844,859 in write-downs, which is the unexplained gap.
- Separately, AR written off after billing: **$2,155,424**.
- Not yet billed: $6.22M of WIP. It is timing, not loss, and $1.38M of it is 90+ days old.

Controllable leakage is the write-downs, about $19.8M.
```dax
EVALUATE ROW("Leak", [Realization Leakage], "Disc", [Agreed Discounts], "WD", [Write-downs], "WO", SUM(invoices[write_off_amount]))
```
Assumption: "leaving on the table" means billing leakage, not a profit measure.

## 18. What's our realization?
**84.5%** billing realization, or 90.0% operational (after agreed discounts). The headline is the same as Q2. The year-to-date figure for 2026 is 84.5%.

## 19. How did Q1 do?
No year is given, so here are all three. Billing realization was close to flat across years.

| | Realization | Leakage | Hours | Billed | Write-offs |
|---|---|---|---|---|---|
| Q1 2026 | 84.7% | $2.89M | 50,901 | $16.01M | $454,035 |
| Q1 2025 | 84.7% | $3.23M | 55,818 | $17.83M | $73,253 |
| Q1 2024 | 83.6% | $3.68M | 59,285 | $18.72M | none |

```dax
EVALUATE SUMMARIZECOLUMNS('Date'[Year], 'Date'[Quarter], "Real", [Billing Realization], "Leak", [Realization Leakage], "WO", [Write-offs], "Hours", [Hours], "Billed", [Billed Value])
```
Assumption: the most likely reading is Q1 2026, the current year. Q1 write-offs are by write-off date. The Q1 2024 write-offs are blank because the earliest write-off in the data is 2025-02-11.

## 20. How much did we write off last quarter?
**$199,637** in Q3 2026 (Jul–Sep). Assumption: "last quarter" is measured from the data's as-of date (2026-10-16), so it is Q3 2026. Q4 2026 to date is $104,733.
```dax
EVALUATE ROW("WO", CALCULATE([Write-offs], 'Date'[Year] = 2026, 'Date'[Quarter] = "Q3"))
```

## 21. Who owes us the most?
**Ivoaelume Medical Group**, with $350,049 open AR. Next are Ardedalis Components at $255,043 and Loraestra Software at $234,480.
```dax
EVALUATE TOPN(3, ADDCOLUMNS(VALUES(clients[client_name]), "AR", [Open AR]), [AR], DESC)
```
Assumption: "owes" means open invoice balance, and does not include unbilled WIP.

## 22. Is fixed-fee work a problem?
**Yes.** Fixed Fee realization is 67.5%, against 90.8% for Hourly and 79.3% for Capped. Fixed Fee has the largest leakage ($13.29M), and $10.82M of it is write-downs, more than half of all firm write-downs ($19.84M). Even after excluding agreed discounts, operational realization is 71.8%.
```dax
EVALUATE ADDCOLUMNS(VALUES(engagements[fee_type]), "Real", [Billing Realization], "Leak", [Realization Leakage], "WD", [Write-downs])
```
Assumption: "problem" is judged by realization and leakage, with no target in the model to compare against.

## 23. How bad is the cash application backlog?
- **$3,102,103 unapplied across 297 payments.**
- **$2,794,798 (90%)** has been unapplied for more than 14 days.
- $2,739,923 has been unapplied for more than 30 days, and $2,530,414 for more than 60.
- The oldest payment has been unapplied for 924 days.
- Separately, $6.18M of cash across all payments took more than 14 days to apply.
```dax
EVALUATE ROW("Unap", [Unapplied Cash], "Unap14", [Unapplied Cash 14+ Days], "Unap60", CALCULATE([Cash Received], ISBLANK(payments[applied_date]), payments[Days To Apply] > 60))
```
Assumption: the backlog is payments with no `applied_date`. Almost all of it is old, not recent.

## 24. Are late timesheets costing us money?
**Yes.** Realization falls as entry lag grows:

| Entry timeliness | Hours | Realization | Leakage |
|---|---|---|---|
| On time (0–7 days) | 500,003 | 85.7% | $26.00M |
| Late (8–29 days) | 69,845 | 79.5% | $5.46M |
| Very late (30+ days) | 10,028 | 65.8% | $1.35M |

Late and very late entries are about 14% of hours. Roughly 20 points of realization separate very late from on-time entries. This shows an association, not proven causation. Late entries may also differ in fee type or client mix, which I didn't test.
```dax
EVALUATE ADDCOLUMNS(SUMMARIZE(time_entries, time_entries[Entry Timeliness], time_entries[Entry Timeliness Order]), "Hours", [Hours], "Real", [Billing Realization], "Leak", [Realization Leakage])
```

## 25. How much unapplied cash does the Transactions practice have?
**Cannot be answered directly.** Payments link to clients, not engagements or practices, and a client can have engagements in several practices. The model has no practice on a payment.

**Approximation:** each unapplied payment has a `remittance_invoice_id` (all 297 do). Following it to the invoice, then the engagement, then the practice, gives **$764,592** for Transactions. This is the practice of the invoice the client says they were paying, not a model relationship, so treat it as an estimate.
```dax
EVALUATE ROW("Txn", SUMX(FILTER(payments, ISBLANK(payments[applied_date])),
  VAR eng = LOOKUPVALUE(invoices[engagement_id], invoices[invoice_id], payments[remittance_invoice_id])
  VAR p = LOOKUPVALUE(engagements[practice], engagements[engagement_id], eng)
  RETURN IF(p = "Transactions", payments[amount])))
```

## 26. What was billing realization in December 2026?
**Not answerable.** The data ends 2026-10-16, and there are no time entries or invoices for December 2026. Realization returns blank for that month.
```dax
EVALUATE ROW("Dec26", CALCULATE([Billing Realization], 'Date'[Year] = 2026, 'Date'[Month Num] = 12))  -- blank
```

## 27. How much did we bill Acme Corporation?
**Not answerable.** None of the 450 clients has a name containing "Acme". Either the client isn't in this model, or it goes by another name.
```dax
EVALUATE ROW("n", COUNTROWS(FILTER(ALL(clients), CONTAINSSTRING(clients[client_name], "acme"))))  -- blank / zero
```

## 28. What's our profit margin?
**Not answerable.** The model has revenue-side data only (standard rates, billed value, collections). It has no cost, compensation or expense data, so margin can't be computed.

## 29. What is each partner's utilization rate?
The model has `staff.monthly_target_hours` (110 for every partner) and logged hours, so I computed hours ÷ (110 × 12) for calendar 2025. Utilization means logged hours over target hours, not billable hours. It counts all hours entered, billed or not.

| Partner | 2025 hours | Utilization |
|---|---|---|
| Debra Gardner | 2,259 | 171% |
| Robert Johnson | 2,199 | 167% |
| Anthony Gonzalez | 1,883 | 143% |
| Joshua Walker | 1,733 | 131% |
| Matthew Moore | 1,691 | 128% |
| Linda Wolfe | 1,655 | 125% |
| Melanie Munoz | 1,588 | 120% |
| Jeffery Wagner | 1,546 | 117% |
| Lisa Smith | 1,512 | 115% |
| Jill Rhodes | 1,485 | 113% |
| Susan Rogers | 1,406 | 107% |
| Danielle Johnson | 1,402 | 106% |
| Jeffrey Lawrence | 1,363 | 103% |
| Christopher Davis | 1,270 | 96% |
| Patricia Miller | 1,253 | 95% |

```dax
EVALUATE ADDCOLUMNS(FILTER(staff, staff[title] = "Partner"), "Hrs2025", CALCULATE([Hours], 'Date'[Year] = 2025),
  "Util2025", DIVIDE(CALCULATE([Hours], 'Date'[Year] = 2025), 12 * staff[monthly_target_hours]))
```
Assumptions:
- "Partner" means `title = "Partner"` (15 staff). Other titles are not included, and this question asked only about partners.
- I used 2025 because it is the last full year.
- The target of 110 hours a month looks low for partners. The results above 100% reflect that, so the target may need checking.

## 30. Compare this year's realization to last year's.
Billing realization is flat.

| Period | Billing realization | Operational realization | Leakage |
|---|---|---|---|
| 2026 YTD (to 2026-10-16) | 84.46% | 89.92% | $7.77M |
| 2025 same period (to 2025-10-16) | 84.51% | 89.86% | $10.14M |
| 2025 full year | 84.64% | 90.05% | $12.65M |

The 2026 figure is slightly lower than full-year 2025 (−0.2 points), and about the same as the same period of 2025. Leakage is lower in dollars because 2026 billed volume is lower: YTD billed time is down against the same period last year.
```dax
EVALUATE ROW("R2026", CALCULATE([Billing Realization], 'Date'[Year] = 2026),
  "R2025SP", CALCULATE([Billing Realization], 'Date'[Year] = 2025, 'Date'[Date] <= DATE(2025,10,16)),
  "R2025", CALCULATE([Billing Realization], 'Date'[Year] = 2025))
```
Assumption: "this year" is 2026 up to the data's as-of date, and "last year" is 2025. Realization is by work date. Some 2026 time may still be unbilled, which can affect the latest months.

---

## Notes on the model
- `Unapplied Cash 14+ Days` and `AR 90+` use "greater than", not "greater than or equal to". It made no difference to the totals here.
- `Write-downs` (billing gap) and `Write-offs` (AR written off) are different measures, and the questions mix the wording ("write-downs", "written off"). I mapped Q4 to write-downs and Q12 and Q20 to write-offs.
- The `Date` table runs to 2026-10-31, but the facts end 2026-10-16, so the October 2026 figures are partial.
