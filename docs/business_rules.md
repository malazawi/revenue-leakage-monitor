# Business Rules

These rules drive both the dashboard measures and the Collections Agent. They reflect how billing and collections teams in professional services firms actually work.

## Revenue leakage definitions

| Leakage point | Definition |
|---|---|
| **Late time entry** | Time entered **8+ days** after the work date. **Very late** = 30+ days. Late entries miss billing cycles and get written down more often. |
| **WIP aging** | Unbilled work, aged from the work date: 0–30 / 31–60 / 61–90 / 91–120 / 120+ days. |
| **Billing realization** | Billed value ÷ standard value (hours × standard rate). |
| **Collection realization** | Cash collected ÷ billed value. |
| **AR aging** | Unpaid invoice balances, aged from invoice date, in the same five buckets. |
| **Unapplied cash** | A payment received but not matched to an invoice within **14 days**. |
| **Bad-debt write-off** | Invoice balances written off after roughly a year unpaid. |

## Collections Agent rules

**Who is eligible for outreach (invoice level)**
- 31+ days past due
- Balance of $5,000 or more
- No contact in the last 14 days
- Not flagged **Disputed** or **Payment plan**

**Priority score (0–100)**

| Factor | Weight | Scaled against |
|---|---|---|
| Balance | 40% | $100,000 |
| Days past due | 35% | 180 days |
| Days since last contact | 15% | 60 days (never contacted = 60) |
| Broken promises to pay | 10% | 3 |

**Two lanes, one action per client or partner per day**

| Lane | Applies to | Action |
|---|---|---|
| Client reminders | Clients whose oldest eligible invoice is 31–120 days past due | **One email per client** listing all eligible invoices; top 10 clients per day by score |
| Escalations | Any eligible invoice 120+ days past due | **No client email.** One internal note per billing partner listing their escalated clients |

**Email tone by the client's oldest past-due invoice**

| Days past due | Tone |
|---|---|
| 31–60 | Friendly reminder |
| 61–90 | Firm, asks for a payment date |
| 91–120 | Urgent |
| 120+ | Escalation lane (internal only) |

**Guardrails**
- Emails are created as **Gmail drafts only**. A person reviews and sends them.
- All client contacts in this project are fictional `@example.com` addresses.
- Every action is logged to a tracker sheet, and a daily summary lists what was drafted, escalated and skipped (with the reason).

## Google Sheet layout (for the agent)

- **AR Aging** tab: import `data/ar_aging_for_agent.csv`
- **Outreach Log** tab: row 1 headers
  `run_date | lane | client_id | client_name | recipient | invoices | total_balance | oldest_days_past_due | tone | priority_score | draft_status`
