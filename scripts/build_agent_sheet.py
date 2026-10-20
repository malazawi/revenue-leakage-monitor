"""
Build the AR aging snapshot the n8n Collections Agent reads (one row per open invoice).
Also scores each row with the priority rules, so the agent's logic can be checked against a known answer.

Run after generate_data.py:  python scripts/build_agent_sheet.py  -> data/ar_aging_for_agent.csv
"""
import numpy as np
import pandas as pd
from pathlib import Path

D = Path(__file__).resolve().parent.parent / "data"   # repo: scripts/ -> data/
AS_OF = pd.Timestamp("2026-10-16")

inv = pd.read_csv(D / "invoices.csv", parse_dates=["invoice_date", "due_date", "write_off_date"])
pay = pd.read_csv(D / "payments.csv", parse_dates=["received_date", "applied_date"])
col = pd.read_csv(D / "collections_log.csv", parse_dates=["contact_date", "promised_date"])
exc = pd.read_csv(D / "ar_exceptions.csv")
eng = pd.read_csv(D / "engagements.csv")
cl = pd.read_csv(D / "clients.csv")
st = pd.read_csv(D / "staff.csv")

applied = pay[pay.applied_invoice_id.notna()].groupby("applied_invoice_id").amount.sum()
inv["balance"] = (inv.invoice_amount - inv.invoice_id.map(applied).fillna(0) - inv.write_off_amount).clip(lower=0).round(2)
ar = inv[inv.balance > 0.01].copy()
ar["days_past_due"] = (AS_OF - ar.due_date).dt.days
ar["aging_bucket"] = pd.cut((AS_OF - ar.invoice_date).dt.days, [-1, 30, 60, 90, 120, 10**6],
                            labels=["0-30", "31-60", "61-90", "91-120", "120+"]).astype(str)

# contact history
last = col.groupby("invoice_id").agg(last_contact_date=("contact_date", "max"), contact_count=("contact_id", "count"))
paid_by = pay.groupby("remittance_invoice_id").received_date.min()
promises = col[col.outcome == "Promise to pay"].copy()
promises["first_payment"] = promises.invoice_id.map(paid_by)
promises["broken"] = (promises.promised_date < AS_OF) & (promises.first_payment.isna() | (promises.first_payment > promises.promised_date))
broken = promises.groupby("invoice_id").broken.sum()

ar = (ar.merge(last, left_on="invoice_id", right_index=True, how="left")
        .merge(exc[["invoice_id", "exception_type"]], on="invoice_id", how="left")
        .merge(eng[["engagement_id", "engagement_name", "billing_partner_id"]], on="engagement_id")
        .merge(cl[["client_id", "client_name", "industry", "ap_contact_name", "ap_contact_email"]], on="client_id")
        .merge(st[["staff_id", "staff_name", "email"]].rename(columns={
            "staff_id": "billing_partner_id", "staff_name": "billing_partner", "email": "billing_partner_email"}),
            on="billing_partner_id"))
ar["broken_promises"] = ar.invoice_id.map(broken).fillna(0).astype(int)
ar["contact_count"] = ar.contact_count.fillna(0).astype(int)
ar["days_since_contact"] = (AS_OF - ar.last_contact_date).dt.days
ar["exception_type"] = ar.exception_type.fillna("")

# ---- Business rules (agreed defaults) ---------------------------------------------------
eligible = (ar.days_past_due >= 31) & (ar.balance >= 5000) & (ar.exception_type == "") & \
           (ar.days_since_contact.isna() | (ar.days_since_contact >= 14))
def norm(s, cap):  # 0..1 scaled, capped
    return (s.clip(lower=0) / cap).clip(upper=1)
score = (0.40 * norm(ar.balance, 100_000) + 0.35 * norm(ar.days_past_due, 180)
         + 0.15 * norm(ar.days_since_contact.fillna(60), 60) + 0.10 * norm(ar.broken_promises, 3))
ar["eligible_for_outreach"] = eligible
ar["priority_score"] = np.where(eligible, (score * 100).round(1), np.nan)
ar["recommended_action"] = np.select(
    [~eligible, ar.days_past_due > 120, ar.days_past_due > 90, ar.days_past_due > 60],
    ["None", "Internal escalation to billing partner", "Urgent reminder", "Firm reminder - ask for payment date"],
    "Friendly reminder")

cols = ["invoice_id", "client_id", "client_name", "industry", "engagement_name", "billing_partner", "billing_partner_email",
        "ap_contact_name", "ap_contact_email", "invoice_date", "due_date", "invoice_amount", "balance", "days_past_due",
        "aging_bucket", "last_contact_date", "days_since_contact", "contact_count", "broken_promises", "exception_type",
        "eligible_for_outreach", "priority_score", "recommended_action"]
out = ar[cols].sort_values(["eligible_for_outreach", "priority_score", "balance"], ascending=[False, False, False])
for c in ["invoice_date", "due_date", "last_contact_date"]:
    out[c] = out[c].dt.strftime("%Y-%m-%d")
out.to_csv(D / "ar_aging_for_agent.csv", index=False)
print(f"open invoices: {len(out):,} | eligible for outreach: {int(out.eligible_for_outreach.sum())} | "
      f"open AR ${out.balance.sum():,.0f}")
print(out[out.eligible_for_outreach].head(10)[["client_name", "balance", "days_past_due", "days_since_contact",
                                               "broken_promises", "priority_score", "recommended_action"]].to_string(index=False))
