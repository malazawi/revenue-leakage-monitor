# Answer Key: Talk-to-Data Agent Test Questions

Answers for `questions.md` (30 questions). All values come from read-only DAX queries (`EVALUATE`)
run against the open Power BI Desktop model on 2026-10-23. No model or report files were changed.

**Data facts used throughout (proven by query):**
- Latest `work_date` / `entry_date` = **2026-10-16**. Latest invoice = 2026-10-10. Latest payment = 2026-10-16. Latest write-off = 2026-10-15.
- Earliest work date = 2024-01-01. The Date table runs to 2026-10-31 (no later dates).
- October 2026 has hours logged (5,669) but **no billed time yet**, so Billing Realization for Oct 2026 is blank. The last month with a realization figure is **Sep 2026 (85.3%)**.
- 450 clients, 1,800 engagements, 150 staff, 15,943 payments.

**Convention:** "today" is 2026-10-23, so "this year" = 2026, "last year" = 2025, "last quarter" = Q3 2026.
Dollar figures are rounded; scoring tolerance in `questions.md` is 0.5%.

---

## Tier 1: Direct lookups

### 1. Total hours logged
**Answer: 579,876 hours** (579,876.25).
```dax
EVALUATE ROW("Hours", [Hours])
```

### 2. Firm-wide billing realization
**Answer: 84.5%** (0.84510).
```dax
EVALUATE ROW("Billing Realization", [Billing Realization])
```

### 3. Agreed discounts
**Answer: $13.0M** ($12,974,022).
```dax
EVALUATE ROW("Agreed Discounts", [Agreed Discounts])
```

### 4. Total write-downs
**Answer: $19.8M** ($19,844,859). Write-downs = standard value billed − agreed discounts − billed value.
```dax
EVALUATE ROW("Write-downs", [Write-downs])
```

### 5. Current open AR
**Answer: $11.06M** ($11,062,459). Sum of `invoices[balance]`.
```dax
EVALUATE ROW("Open AR", [Open AR])
```

### 6. AR more than 90 days old
**Answer: $2.96M** ($2,960,949), about 26.8% of open AR.
```dax
EVALUATE ROW("AR 90+", [AR 90+], "AR 90+ %", [AR 90+ %])
```

### 7. Unapplied cash 14+ days
**Answer: $2.79M** ($2,794,798), across 257 payments. (All unapplied cash regardless of age is $3.10M, 297 payments.)
```dax
EVALUATE ROW("Unapplied 14+", [Unapplied Cash 14+ Days], "All unapplied", [Unapplied Cash])
```

### 8. Total unbilled WIP
**Answer: $6.22M** ($6,219,976), at standard value. Of that, $1.38M is aged 90+ days.
```dax
EVALUATE ROW("Unbilled WIP", [Unbilled WIP], "Aged WIP 90+", [Aged WIP 90+])
```

---

## Tier 2: Sliced questions

### 9. Billing realization by fee type
**Answer:** Hourly **90.8%** · Capped **79.3%** · Fixed Fee **67.5%**.
```dax
EVALUATE SUMMARIZECOLUMNS(engagements[fee_type], "Realization", [Billing Realization])
```

### 10. Practice with the lowest billing realization
**Answer: Risk & Compliance, 83.9%** (0.83876).
Full ranking: Risk & Compliance 83.88% · Finance Transformation 83.94% · Operations Excellence 84.37% · Technology Advisory 85.03% · Transactions 85.20%.
*Scoring rule:* the bottom two are only 0.06 points apart.
- ✅ Names Risk & Compliance (83.9%).
- 🟡 Names Finance Transformation but says it is nearly tied with Risk & Compliance.
- ❌ Names Finance Transformation (or any other practice) as the clear lowest, with no mention of the near-tie.
```dax
EVALUATE SUMMARIZECOLUMNS(engagements[practice], "Realization", [Billing Realization]) ORDER BY [Realization] ASC
```

### 11. Industry with the highest open AR
**Answer: Manufacturing, $2.21M** ($2,208,181).
Next: Financial Services $1.94M · Technology $1.94M · Healthcare $1.85M · Retail $1.37M · Public Sector $1.08M · Energy $0.67M.
```dax
EVALUATE SUMMARIZECOLUMNS(clients[industry], "OpenAR", [Open AR]) ORDER BY [OpenAR] DESC
```

### 12. Written off in October 2026
**Answer: $104,733** (about $105K). This is **Write-offs** (invoice write-offs by write-off date), the AR measure, not Write-downs. October is month-to-date; the latest write-off in the data is 2026-10-15.
```dax
EVALUATE ROW("Write-offs Oct 2026", CALCULATE([Write-offs], 'Date'[Year] = 2026, 'Date'[Month Num] = 10))
```

### 13. Cash received in 2025
**Answer: $69.4M** ($69,400,301). Cash Received is by `payments[received_date]`.
(For context: 2024 $48.6M, 2026 YTD $50.9M.)
```dax
EVALUATE ROW("Cash 2025", CALCULATE([Cash Received], 'Date'[Year] = 2025))
```

### 14. Realization for very late entries (30+ days)
**Answer: 65.8%** (0.65775).
```dax
EVALUATE ROW("Very late realization", CALCULATE([Billing Realization], time_entries[entry_lag_days] >= 30))
-- same result via the Entry Timeliness column ("Very late (30+ days)")
```

### 15. Three billing partners with the most aged WIP (90+ days)
**Answer:**
1. **Patricia Miller, $467,145**
2. **Danielle Johnson, $352,379**
3. **Christopher Davis, $322,831**

```dax
EVALUATE TOPN(3, SUMMARIZECOLUMNS(engagements[Billing Partner], "AgedWIP", [Aged WIP 90+]), [AgedWIP], DESC) ORDER BY [AgedWIP] DESC
```

### 16. Billing realization for Manufacturing clients
**Answer: 83.8%** (0.83760). Firm-wide is 84.5%, so Manufacturing is slightly below.
```dax
EVALUATE ROW("Manufacturing realization", CALCULATE([Billing Realization], clients[industry] = "Manufacturing"))
```

---

## Tier 3: Business language

### 17. "How much money are we leaving on the table?"
**Expected answer:** separate the two components of realization leakage (total **$32.8M**):
- **Agreed discounts: $13.0M** (contractual, negotiated; not really "lost")
- **Write-downs: $19.8M** (the true leakage: standard value cut at billing with no contractual reason)

Also acceptable to mention, as separate items: AR write-offs of $2.16M (invoices written off after billing) and $6.22M unbilled WIP ($1.38M aged 90+). A good answer does not add all of these into one number.
```dax
EVALUATE ROW("Leakage", [Realization Leakage], "Agreed Discounts", [Agreed Discounts], "Write-downs", [Write-downs], "Write-offs (AR)", [Write-offs])
```

### 18. "What's our realization?"
**Expected answer: Billing Realization 84.5%.** A good answer also notes that **Operational Realization (90.0%)** exists and excludes agreed discounts.
```dax
EVALUATE ROW("Billing Realization", [Billing Realization], "Operational Realization", [Operational Realization])
```

### 19. "How did Q1 do?" (ambiguous)
**Assumption: Q1 2026** (Jan–Mar 2026), the most recent Q1 and the latest completed Q1 as of 2026-10-23. A good answer states the year. Acceptable alternative: show all three years.

| | Q1 2024 | Q1 2025 | **Q1 2026** |
|---|---|---|---|
| Hours | 59,285 | 55,818 | **50,901** |
| Invoiced (Billed) | $11.46M | $17.90M | **$16.80M** |
| Billing realization | 83.6% | 84.7% | **84.7%** (0.84695) |
| Write-offs (by write-off date) | n/a (blank) | $73K | **$454K** |

"Did well/poorly" is a judgment; the facts above are what to check. Q1 2024 invoicing is low because billing ramps up through early 2024 (inferred, not tested).
```dax
EVALUATE SUMMARIZECOLUMNS('Date'[Year], 'Date'[Quarter], FILTER(ALL('Date'[Quarter]), 'Date'[Quarter] = "Q1"),
  "Billed", [Billed], "Realization", [Billing Realization], "Hours", [Hours], "WriteOffs", [Write-offs])
```

### 20. "How much did we write off last quarter?" (ambiguous)
**Assumption: Q3 2026** (Jul–Sep), the last completed quarter as of 2026-10-23. **Answer: $199,637 (about $200K) of Write-offs.** The answer should use write-offs (invoices written off), not write-downs ($19.8M).
For reference: Q4 2026 to date (Oct) = $104,733. If the agent treated "last quarter" as the current quarter to date, flag as a wrong assumption unless it said so.
```dax
EVALUATE ROW("Write-offs Q3 2026", CALCULATE([Write-offs], 'Date'[Year] = 2026, 'Date'[Quarter] = "Q3"))
```

### 21. "Who owes us the most?"
**Answer: Ivoaelume Medical Group, $350,049** open AR.
Next: Ardedalis Components $255,043 · Loraestra Software $234,480.
```dax
EVALUATE TOPN(3, SUMMARIZECOLUMNS(clients[client_name], "OpenAR", [Open AR]), [OpenAR], DESC) ORDER BY [OpenAR] DESC
```

### 22. "Is fixed-fee work a problem?"
**Expected answer: Yes.** Fixed Fee has the lowest realization:

| Fee type | Billing realization | Operational realization |
|---|---|---|
| Fixed Fee | **67.5%** | **71.8%** |
| Capped | 79.3% | 84.4% |
| Hourly | 90.8% | 96.8% |

Even after removing agreed discounts, fixed fee is at 71.8% (about 28% of standard value is still lost), so the problem is not just discounting. Likely explanation (inferred, not proven): scope creep or overruns on fixed-price work.
```dax
EVALUATE SUMMARIZECOLUMNS(engagements[fee_type], "Billing", [Billing Realization], "Operational", [Operational Realization])
```

### 23. "How bad is the cash application backlog?"
**Expected answer:**
- **$3.10M** of cash is unapplied (297 payments), about 1.8% of the $168.9M ever received.
- **$2.79M** of it (257 payments) has been unapplied 14+ days, which is about 90% of the backlog.
- Another $6.18M was applied but took over 14 days (Slow-Applied Cash). Average days to apply: 9.4.
- Caveat: unapplied cash is a firm-wide number; it is not tied to practices or engagements.

```dax
EVALUATE ROW("Unapplied", [Unapplied Cash], "Unapplied 14+", [Unapplied Cash 14+ Days], "Slow-applied", [Slow-Applied Cash],
  "Unapplied payments", CALCULATE(COUNTROWS(payments), ISBLANK(payments[applied_date])),
  "Unapplied 14+ payments", CALCULATE(COUNTROWS(payments), ISBLANK(payments[applied_date]), payments[Days To Apply] > 14),
  "Avg days to apply", AVERAGE(payments[Days To Apply]))
```

### 24. "Are late timesheets costing us money?"
**Expected answer: Yes.** Realization falls as entries get later:

| Entry timeliness | Hours | Billing realization |
|---|---|---|
| On time (0–7 days) | 500,003 | **85.7%** |
| Late (8–29 days) | 69,845 | **79.5%** |
| Very late (30+ days) | 10,028 | **65.8%** |

About 14% of hours are late. Association is proven; causation (late entry causes write-downs) is a likely explanation, not proven by this query.
```dax
EVALUATE SUMMARIZECOLUMNS(time_entries[Entry Timeliness], "Realization", [Billing Realization], "Hours", [Hours])
```

---

## Tier 4: Traps

### 25. Unapplied cash for the Transactions practice
**Expected behavior: REFUSE the practice cut / say it is firm-wide only.** `payments` relates to `clients` only, so unapplied cash cannot be assigned to a practice. Acceptable response: give the firm-wide figure ($3.10M) clearly labeled as firm-wide, and explain why it can't be split.
**Failure:** reporting $3.10M (or any number) as Transactions' unapplied cash.
*Supporting fact (proven):* filtering `[Unapplied Cash]` by `engagements[practice] = "Transactions"` returns $3,102,102.58, identical to the firm-wide total. The filter is silently ignored, which is why this is a trap.
```dax
EVALUATE ROW("Transactions filtered", CALCULATE([Unapplied Cash], engagements[practice] = "Transactions"), "Firm-wide", [Unapplied Cash])
```

### 26. Billing realization in December 2026
**Expected behavior: FLAG that there is no data.** Data ends 2026-10-16 (today is 2026-10-23); December 2026 hasn't happened. It should say so, not return blank/zero/100% as an answer.
*Supporting facts (proven):* December 2026 hours = blank, realization = blank. October 2026 realization is also blank (hours exist but nothing is billed yet), so the latest month with a realization figure is **Sep 2026 (85.3%)**. A good answer offers Sep 2026 or Dec 2025 (84.9%) as alternatives.
```dax
EVALUATE ROW("Dec 2026 hours", CALCULATE([Hours], 'Date'[Year] = 2026, 'Date'[Month Num] = 12),
  "Dec 2026 realization", CALCULATE([Billing Realization], 'Date'[Year] = 2026, 'Date'[Month Num] = 12),
  "Last entry date", [As Of Date])
```

### 27. How much did we bill Acme Corporation?
**Expected behavior: SAY IT CAN'T FIND THE CLIENT.** Don't invent a number, and don't return $0 as if the client exists.
*Supporting facts (proven):* no client in `clients[client_name]` contains "acme" (0 of 450 clients), and no engagement in `engagements[engagement_name]` contains "acme" (0 of 1,800 engagements). Client names are invented (for example Ivoaelume Medical Group, Ardedalis Components). A good answer may offer to look up similarly named clients.
```dax
EVALUATE ROW("Clients matching", COUNTROWS(FILTER(clients, CONTAINSSTRING(clients[client_name], "acme"))),
             "Engagements matching", COUNTROWS(FILTER(engagements, CONTAINSSTRING(engagements[engagement_name], "acme"))))
-- both return blank (COUNTROWS of an empty table), i.e. 0 matches
```

### 28. What's our profit margin?
**Expected behavior: SAY IT CAN'T BE CALCULATED.** The model has revenue-side data only. There are no cost, salary, expense, or overhead fields. `staff` has only `standard_rate` (a billing rate) and `monthly_target_hours`; `standard_rate` is not a cost rate.
**Failure:** presenting realization, a rate-based margin, or any invented margin as "profit margin".
*Supporting facts (proven):* all 23 measures and every column in the 9 tables were reviewed; none are cost fields.

### 29. Each partner's utilization rate
**Expected behavior: SAY THERE IS NO UTILIZATION MEASURE**, or if it builds one, state the definition and caveats clearly.
*Supporting facts:* no utilization measure exists. `staff[monthly_target_hours]` exists, so hours ÷ target hours is possible to compute, but it would be a self-built calculation with these caveats: `time_entries` has no billable/non-billable flag (so it is total, not billable, utilization), and a "partner" would need defining (`staff[title]`, versus the `Billing Partner` on engagements, which is a different thing). The answer should not present the number as an official model metric. No utilization figures were computed for this key.

### 30. Compare this year's realization to last year's (partial trap)
**Assumption: this year = 2026, last year = 2025.**
**Expected behavior: report the numbers AND flag that 2026 is a partial year.**

| | Billing realization | Hours |
|---|---|---|
| 2025 (full year) | **84.6%** (0.84636) | 219,887 |
| 2026 (YTD, billed through Sep) | **84.5%** (0.84457) | 150,508 |

- Realization is a ratio, so the partial year doesn't distort it directly. But 2026 has no billed time for Oct (data ends 2026-10-16), and hours/dollar totals aren't comparable.
- Like-for-like Jan–Sep: **2026 84.46% vs 2025 84.45%**, so essentially flat.
- The flag the agent must give: 2026 is incomplete (about 9.5 months), the latest data is 2026-10-16, and absolute totals (hours, billed value) shouldn't be compared directly.

```dax
EVALUATE SUMMARIZECOLUMNS('Date'[Year], "Realization", [Billing Realization], "Hours", [Hours]) ORDER BY 'Date'[Year]

EVALUATE ROW("Jan-Sep 2026", CALCULATE([Billing Realization], 'Date'[Year] = 2026, 'Date'[Month Num] <= 9),
             "Jan-Sep 2025", CALCULATE([Billing Realization], 'Date'[Year] = 2025, 'Date'[Month Num] <= 9))
```

---

## Notes on proven vs inferred

- **Proven by query:** every number above, the data end dates, the absence of "acme" clients, the ignored practice filter on unapplied cash.
- **Inferred (likely explanations, not tested):** why fixed fee is weak, why late entries realize less, why Q1 2024 invoicing is low.
- **Checks against published findings:** Billing Realization 84.5%, Agreed Discounts $13.0M, Write-downs $19.8M, timeliness 85.7/79.5/65.8%, fee type 67.5/90.8/79.3%, Operational Realization 90.0% (Hourly 96.8 · Capped 84.4 · Fixed 71.8) all reproduce exactly. No measure moved.
