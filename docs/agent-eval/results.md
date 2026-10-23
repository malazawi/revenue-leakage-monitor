# Talk-to-Data Agent: Accuracy Report Card

**Agent:** Claude Code (Sonnet 5.5) connected to the Power BI semantic model through Microsoft's
Power BI Modeling MCP server. Read-only DAX queries only.

**Test:** 30 business questions in 4 tiers ([questions](../../questions.md)), graded against an
answer key computed with DAX and cross-checked against the published findings
([answer key](answer-key.md)). The agent ran in a separate, empty folder with no access to the
repo, the answer key, or the project notes. It saw only the questions and the model.

## Score: 29 / 30 → 30 / 30 after one business rule

| Tier | What it tests | Score |
|---|---|---|
| 1. Direct lookups | One measure, no filters | 8 / 8 |
| 2. Sliced questions | Picking the right field and filter | 8 / 8 |
| 3. Business language | Mapping how managers talk to the right measure | 8 / 8 |
| 4. Traps | Refusing or caveating when the data can't answer | 5 / 6 → 6 / 6 |

**Scoring:** ✅ correct (within 0.5%, or the right entity) · 🟡 correct but missing a needed
caveat · ❌ wrong · 🛑 correctly refused or flagged.

## What it got right

- **Refused to make things up.** Said "not answerable" for December 2026 realization (no data),
  an unknown client ("Acme Corporation"), and profit margin (no cost data in the model).
- **Handled ambiguity openly.** "How did Q1 do?" with no year: showed all three years and named
  its assumption. "Last quarter": stated it used Q3 2026 based on the data's as-of date.
- **Kept similar terms apart.** Separated write-downs ($19.8M, billing gap) from write-offs
  ($2.2M, AR written off), and agreed discounts from operational leakage.
- **Flagged partial periods.** Compared 2026 year-to-date against the same period of 2025, not
  the full year.

## The one miss, and the fix

**#25: "How much unapplied cash does the Transactions practice have?"** 🟡 in Run 1

The agent correctly said the model can't answer this directly, since unapplied cash isn't tied
to practices. It then offered an estimate ($764,592) by tracing each payment's remittance invoice
to a practice. The method was disclosed, but in practice a number like that travels without its
caveat. The problem was a missing business rule, not bad math.

**Fix:** a short [business rules](business-rules.md) file, the same kind of guidance you would add
to Power BI's AI instructions:
- Unapplied cash is company-wide only.
- Never estimate a number the business doesn't officially track.

**Run 2 (question 25 only):** the agent said unapplied cash isn't tracked by practice, gave the
company-wide figure instead ($3.10M across 297 payments), gave no Transactions number, and named
both rules it applied. ✅

## Why it scored this well

The agent read the model's structure and the descriptions on every measure, and used them
correctly. A clean semantic model with clear names and documented measures is what made the
answers accurate. The model work came first, and the AI benefited from it.

## Files

- [questions.md](../../questions.md): the 30 questions with scoring notes
- [answer-key.md](answer-key.md): correct answers and the DAX behind each
- [run1-answers.md](run1-answers.md): the agent's full answers, with its DAX and assumptions
- [business-rules.md](business-rules.md): the rule added after Run 1
- [run2-q25.md](run2-q25.md): the rerun of question 25
