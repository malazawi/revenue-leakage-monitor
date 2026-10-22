# CLAUDE.md: Revenue Leakage Monitor

Briefing for Claude Code. Read this before doing anything in this repo.

## What this project is

A public portfolio project by Mo (GitHub: malazawi). It's a Power BI revenue leakage monitor for
**Brightwater Advisory Partners**, a fictional 150-person professional services firm. All data is
synthetic (about 189K time entries, 16K invoices, Jan 2024 to Oct 2026).

- `Revenue Leakage Monitor.SemanticModel/`: the model, as PBIP/TMDL
- `Revenue Leakage Monitor.Report/`: the report (one page)
- `data/`: source CSVs · `scripts/`: data generation · `n8n/`: collections agent workflow
- `docs/model-audit/`: audit trail (`baseline.md`, `after-fixes.md`)

## Working rules (always follow)

1. **Plan first.** Before editing any file, show a plan and wait for Mo's approval.
2. **Never change an existing measure's logic** without explicit approval. If a new view is needed,
   **add a new measure** instead. Published findings depend on these measures and must not move:
   Billing Realization (84.5%), Agreed Discounts ($13.0M), Write-downs ($19.8M), realization by entry
   timeliness (85.7% / 79.5% / 65.8%) and fee type (67.5% fixed / 90.8% hourly / 79.3% capped),
   Aged WIP 90+, AR 90+, Unapplied Cash 14+ Days.
3. **Baseline, then change, then diff.** Before model changes, capture baseline DAX results.
   After changes, rerun the queries and diff them. Save the results in `docs/model-audit/`.
   Report anything unexpected; never hide it.
4. **Power BI Desktop rule.** Desktop must be **closed without saving** before you edit TMDL or
   report JSON files. Desktop overwrites file edits on save. Ask Mo to close it, then reopen and
   refresh it after edits.
5. **Mo commits.** Never run `git commit`, `git push`, or create branches. After each fix, stop and
   list the changed files so Mo can review and commit in GitHub Desktop.
6. **One fix at a time**, so each one can be reverted on its own.
7. **Separate proven from inferred.** In findings and docs, say what a query proved and what is a
   likely explanation.
8. **Explain in plain business language.** Mo is a finance/BI analyst, so explain the "so what"
   for a finance manager, not just the DAX.

## Privacy and publishing (public repo)

- Never commit personal emails, Google Sheet IDs, API keys, or credentials. Mo enters all
  credentials himself. Fake contacts use `@example.com`.
- Keep the data obviously fictional: no law-firm names, vocabulary, or office names.
- Don't put "synthetic data" labels on the dashboard itself. A note in the README or data
  dictionary is fine.

## Tools

- `powerbi-modeling` MCP server (Microsoft Power BI Modeling MCP). DAX queries (`EVALUATE`) and
  List/Get operations are read-only. Any Create, Update, Delete, or Activate operation needs Mo's
  approval.
- Connect to the live model through the open Power BI Desktop instance for queries. Edit
  definitions as TMDL files.

## Model notes (learned in the Oct 2026 audit)

- `Write-offs` uses an **inactive** `invoices[write_off_date] -> Date[Date]` relationship via
  `USERELATIONSHIP`. Date-grouped queries show a $0 blank-date row (invoices with no write-off).
- `time_entries[invoice_id]` is blank for unbilled WIP (~5,450 rows). A relationship to
  `invoices` creates a blank member and added blank Practice/Fee rows, so it was **reverted**. If you
  need that link, consider `TREATAS` inside a measure, and rerun the Practice/Fee check.
- `payments` relates to `clients` only. Unapplied cash isn't tied to engagements by definition.
  Cash visuals ignore the Practice and Fee type slicers on purpose.
- `Operational Realization` (added Oct 2026) excludes agreed discounts: 90.0% firm-wide;
  Hourly 96.8% · Capped 84.4% · Fixed fee 71.8%. `Billing Realization` is unchanged.
- Open backlog from the audit (not yet done): hard-coded thresholds (8/30/90/14 days), Date table
  quarter/month labels without year, unused measures and tables, hard-coded data path, missing
  table/column descriptions.
