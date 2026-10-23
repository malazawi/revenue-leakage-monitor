# Run 2: Question 25

**Question:** How much unapplied cash does the Transactions practice have?

## Answer
**Unapplied cash isn't tracked at the practice level, so I can't give a figure for Transactions.**

The model links payments to clients only, not to engagements or practices. The company-wide figure is:

- **Unapplied cash: $3,102,102.58** across 297 payments, as of 2026-10-16.

The model does support this figure by client or industry, if that would help.

## DAX I ran
```dax
EVALUATE ROW(
    "UnappliedCash", [Unapplied Cash],
    "Payments", COUNTROWS(FILTER(payments, ISBLANK(payments[applied_date]))),
    "AsOf", [As Of Date]
)
-- [Unapplied Cash] = CALCULATE([Cash Received], ISBLANK(payments[applied_date]))
```

## Business rule applied
From `business-rules.md`, "Cash and payments":
1. *Unapplied cash is company-wide only.* A practice request gets "not tracked at that level" plus the company-wide figure.
2. *Never estimate a number the business doesn't officially track.* No approximations from indirect fields.

## Note on the earlier run
In run 1 I gave an estimate for this question by tracing remittance invoices to a practice. Under rule 2 that was wrong, and the estimate shouldn't be used. This answer replaces it.

If a practice-level view is wanted, the remittance-invoice tracing is one way to build it. A person would need to decide whether to use it and how to label it.
