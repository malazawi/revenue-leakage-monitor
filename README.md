# Revenue Leakage Monitor + Collections Agent

**A Power BI dashboard that shows where a professional services firm loses money between work performed and cash collected, plus an n8n + AI agent that acts on it every morning.**

Most dashboards stop at "here's the problem." This project goes one step further: the dashboard finds the leakage, and the agent works the receivables queue, drafting the follow-ups a collections team would otherwise write by hand.

![Dashboard](images/dashboard.png)

---

## The business problem

In a professional services firm, revenue leaks at five points between doing the work and getting paid:

| Leakage point | What goes wrong |
|---|---|
| **Late time entry** | Hours entered days or weeks late miss billing cycles and get written down |
| **Billing write-downs** | Work billed for less than its standard value |
| **Unbilled WIP** | Work sits unbilled for months and becomes harder to collect |
| **Aging receivables** | Invoices go unpaid until they are written off |
| **Unapplied cash** | Payments arrive but aren't matched to invoices, so AR looks worse than it is and clients get chased for bills they already paid |

## Part 1: Power BI dashboard

### Key findings (Jan 2024 to Oct 2026)

**1. $19.8M was written down at billing, beyond the discounts the firm agreed to.**
Overall billing realization is 84.5%. I separated **$13.0M of contractual discounts** (a pricing decision) from **$19.8M of write-downs** (operational leakage), so the number leadership sees is the one they can actually act on.

**2. Late time entry has a measurable cost.**
13.8% of hours are entered 8+ days after the work. Realization falls from **85.7%** for time entered on time, to **79.5%** for late entries, to **65.8%** for entries 30+ days late.

**3. Fixed-fee engagements under-recover.**
Fixed-fee work realizes **67.5%** of standard value vs. **90.8%** for hourly. Capped fees fall in between at 79.3%. This points to a scoping and pricing issue, not a billing one.

**4. Three partners hold 83% of unbilled work older than 90 days.**
$1.4M of WIP is over 90 days old, concentrated in a few billing partners' engagements. That makes it a conversation with three people, not a firm-wide policy change.

**5. A cash-application backlog followed a system migration.**
Payments taking 14+ days to apply jumped from about $0.15M in a normal month to about **$1.05M in both March and April 2026** (7x). $2.8M of cash is still unapplied after 14+ days, and $3.0M of AR is more than 90 days old.

### How it's built
- **Data model:** a star schema with 8 tables loaded from CSV through Power Query, a single `DataFolder` parameter, a marked Date table and 10 relationships.
- **Power Query:** invoice balances are computed in M by joining applied payments and write-offs to invoices.
- **DAX:** 22 documented measures in display folders (Time Entry, Realization, WIP, Receivables, Cash Application), plus calculated columns for aging buckets and entry timeliness.
- **Saved as PBIP:** the model (TMDL) and report (PBIR) are plain text, so every measure is readable and diffable on GitHub.

## Part 2: n8n Collections Agent

![Workflow](images/n8n-workflow.png)

Every weekday morning, the agent:
1. **Reads** the AR aging report and the outreach log from Google Sheets.
2. **Applies the business rules** ([docs/business_rules.md](docs/business_rules.md)): 31+ days past due, $5K+ balance, not disputed or on a payment plan, and not contacted in the last 14 days.
3. **Scores** each invoice (balance 40%, days past due 35%, days since last contact 15%, broken promises 10%) and **groups by client**, so each client gets one email, not one per invoice.
4. **Splits into two lanes:**
   - **31–120 days:** the top 10 clients get an AI-drafted email in the right tone (friendly → firm → urgent), using only the facts provided.
   - **120+ days:** no client email. Each billing partner gets one internal note listing all of their escalated clients.
5. **Saves everything as Gmail drafts.** A person reviews and sends; nothing goes to a client automatically.
6. **Logs** every action to the outreach log (which also enforces the 14-day rule) and **emails a daily summary** of what was drafted, escalated and skipped, and why.

**Example run:** 1,184 open invoices scanned → 149 eligible → 86 clients → 10 client drafts + 15 partner notes covering 58 clients ($2.05M). Running it again the same day correctly skipped everyone already contacted and moved on to the next 10 clients.

![Example client draft](images/client-draft.png)

### Guardrails
- **Human in the loop:** drafts only; the workflow never sends to clients.
- **Facts only:** the AI is told to use only the invoice data provided and never invent amounts, dates or consequences. No threats or legal language.
- **No double contact:** the 14-day rule is enforced from the agent's own log as well as the team's contact history.
- **Fails safely:** OpenAI calls are rate-limited (one every 1.5 seconds), retried up to 3 times and time out after 30 seconds.
- **Configurable:** thresholds, daily cap and model live in one Config node.

## Repository structure

```
Revenue Leakage Monitor.pbip              ← open in Power BI Desktop
Revenue Leakage Monitor.SemanticModel/    ← data model as code (TMDL): tables, relationships, measures
Revenue Leakage Monitor.Report/           ← report page and visuals (PBIR JSON) + theme
n8n/collections_agent.json                ← import into n8n
docs/business_rules.md                    ← rules for the dashboard and the agent
docs/data_dictionary.md                   ← every table and column
data/                                     ← synthetic CSVs
scripts/                                  ← data generator
images/                                   ← screenshots
```

## Run it yourself

**Dashboard:** open `Revenue Leakage Monitor.pbip` → Transform data → set the `DataFolder` parameter to your copy of `/data` → Refresh.

**Agent:** upload `data/ar_aging_for_agent.csv` to a Google Sheet tab named **AR Aging**, add an **Outreach Log** tab (headers are in the business rules doc), import `n8n/collections_agent.json` into n8n, connect Google Sheets, Gmail and OpenAI credentials, and set your email in **Config**.

## About the data

The firm, Brightwater Advisory Partners, is fictional, and the data is synthetic. It was generated by `scripts/generate_data.py` (AI-assisted Python) with a fixed random seed, so it reproduces exactly. The business rules, data model, DAX, analysis and agent design are my own work, based on my experience in time, billing and AR reporting.

## Tools

Power BI Desktop · Power Query (M) · DAX · TMDL / PBIR · n8n · OpenAI API · Google Sheets · Gmail · Git

---

*Built by Mohammad (Mo) Alazawi, MS in Business Analytics.*
