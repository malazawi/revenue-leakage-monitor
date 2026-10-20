"""
Synthetic data generator - Revenue Leakage Monitor (portfolio project 2)

Fictional firm: Brightwater Advisory Partners (a made-up professional services / consulting firm).
Every person, company and email address is fake. Client emails use the reserved example.com domain.

Business problems are built in on purpose so the dashboard has real things to find:
  1. A group of chronically late time-enterers; late entries get written down more at billing.
  2. Fixed-fee and capped engagements overrun their fees, so realization is lower.
  3. A few billing partners sit on unbilled WIP for months (billing holds).
  4. Public Sector and Healthcare clients pay slowly; a handful of clients barely pay at all.
  5. A billing-system migration in Mar-Apr 2026 left a spike of payments unapplied.
  6. Collections history with promises to pay, some of them broken, plus disputes and payment plans.

Run:  python scripts/generate_data.py  -> writes CSVs to ./data (requires pandas, numpy, faker)
"""
import numpy as np
import pandas as pd
from faker import Faker
from pathlib import Path

SEED = 42
rng = np.random.default_rng(SEED)
fake = Faker("en_US")
Faker.seed(SEED)

START = pd.Timestamp("2024-01-01")
AS_OF = pd.Timestamp("2026-10-16")          # data snapshot date (a Friday)
OUT = Path(__file__).resolve().parent.parent / "data"   # repo: scripts/ -> data/
OUT.mkdir(exist_ok=True)

FIRM_DOMAIN = "brightwater-advisory.example.com"

# --------------------------------------------------------------------------- staff
TITLES = [  # title, count, rate range, monthly target hours
    ("Partner", 15, (650, 850), 110),
    ("Director", 15, (500, 600), 125),
    ("Senior Manager", 20, (400, 480), 135),
    ("Manager", 30, (320, 380), 140),
    ("Senior Consultant", 35, (250, 300), 145),
    ("Consultant", 35, (180, 230), 145),
]
OFFICES = ["Minneapolis", "Charlotte", "Phoenix", "Columbus", "Salt Lake City"]
PRACTICES = ["Finance Transformation", "Risk & Compliance", "Operations Excellence",
             "Technology Advisory", "Transactions"]

st_rows = []
i = 0
for title, n, (lo, hi), target in TITLES:
    for _ in range(n):
        i += 1
        first, last = fake.first_name(), fake.last_name()
        chronic_late = rng.random() < (0.30 if title in ("Partner", "Director") else 0.12)
        st_rows.append({
            "staff_id": f"ST{i:03d}",
            "staff_name": f"{first} {last}",
            "email": f"{first.lower()}.{last.lower()}@{FIRM_DOMAIN}",
            "title": title,
            "office": rng.choice(OFFICES, p=[0.32, 0.26, 0.16, 0.14, 0.12]),
            "practice": rng.choice(PRACTICES),
            "standard_rate": int(rng.integers(lo, hi + 1) // 5 * 5),
            "monthly_target_hours": target,
            "h_late_profile": "chronic" if chronic_late else "normal",
        })
staff = pd.DataFrame(st_rows)
partners = staff[staff.title == "Partner"].staff_id.tolist()
# Billing-hold partners: sit on WIP
hold_partners = set(rng.choice(partners, size=3, replace=False))

# --------------------------------------------------------------------------- clients
INDUSTRIES = {  # industry: (share, payment-behaviour weights prompt/average/slow/very_slow, terms)
    "Financial Services": (0.20, [0.45, 0.40, 0.12, 0.03], 30),
    "Manufacturing":      (0.18, [0.35, 0.45, 0.15, 0.05], 30),
    "Technology":         (0.16, [0.40, 0.40, 0.15, 0.05], 30),
    "Retail":             (0.12, [0.30, 0.45, 0.18, 0.07], 30),
    "Energy":             (0.10, [0.40, 0.40, 0.15, 0.05], 30),
    "Healthcare":         (0.14, [0.15, 0.35, 0.35, 0.15], 45),
    "Public Sector":      (0.10, [0.05, 0.30, 0.40, 0.25], 45),
}
REGIONS = ["Midwest", "Northeast", "South", "West"]
ind_names = list(INDUSTRIES)
ind_p = np.array([v[0] for v in INDUSTRIES.values()]); ind_p /= ind_p.sum()

# Invented brand names built from nonsense syllables + an industry word, so clients are clearly fictional
ONSET = ["Qu", "Tal", "Ver", "Zan", "Mor", "Kel", "Bryn", "Cal", "Dra", "Fen", "Lor", "Nyx", "Ost", "Pra", "Sol",
         "Tor", "Vel", "Xan", "Yor", "Zep", "Ard", "Cor", "Ely", "Hal", "Ivo", "Jar", "Lum", "Nor", "Ory", "Ruv"]
VOWEL = ["a", "e", "i", "o", "u", "ae", "io"]
CODA = ["vane", "merix", "dris", "thar", "quin", "lume", "stra", "vex", "ryn", "dalis", "corra", "nith", "plex", "varo", "zent"]
SUFFIX = {
    "Financial Services": ["Capital", "Financial", "Credit Union", "Trust"],
    "Manufacturing": ["Industries", "Manufacturing", "Components", "Fabrication"],
    "Technology": ["Systems", "Software", "Labs", "Networks"],
    "Retail": ["Retail", "Outfitters", "Markets", "Home Goods"],
    "Energy": ["Energy", "Power", "Renewables", "Utilities"],
    "Healthcare": ["Health", "Medical Group", "Care Partners", "Clinics"],
    "Public Sector": ["Transit Authority", "Water District", "Housing Authority", "Port Authority"],
}
cl_rows, used = [], set()
for c in range(1, 451):
    ind = rng.choice(ind_names, p=ind_p)
    while True:
        brand = rng.choice(ONSET) + rng.choice(VOWEL) + rng.choice(CODA)
        name = f"{brand} {rng.choice(SUFFIX[ind])}"
        if brand not in used:
            used.add(brand)
            break
    behaviour = rng.choice(["prompt", "average", "slow", "very_slow"], p=INDUSTRIES[ind][1])
    slug = "".join(ch for ch in name.lower() if ch.isalnum())[:20]
    cfirst, clast = fake.first_name(), fake.last_name()
    cl_rows.append({
        "client_id": f"C{c:04d}",
        "client_name": name,
        "industry": ind,
        "region": rng.choice(REGIONS),
        "payment_terms_days": INDUSTRIES[ind][2],
        "ap_contact_name": f"{cfirst} {clast}",
        "ap_contact_email": f"ap.{clast.lower()}@{slug}.example.com",
        "h_behaviour": behaviour,
    })
clients = pd.DataFrame(cl_rows)
# A few "problem" clients that barely pay
problem_clients = set(rng.choice(clients.client_id, size=8, replace=False))
clients.loc[clients.client_id.isin(problem_clients), "h_behaviour"] = "problem"

# --------------------------------------------------------------------------- engagements
eng_rows = []
non_partners = staff[staff.title != "Partner"]
for e in range(1, 1801):
    client = clients.sample(1, random_state=int(rng.integers(1e9))).iloc[0]
    start = START - pd.Timedelta(days=180) + pd.Timedelta(days=int(rng.integers(0, (AS_OF - START).days + 160)))
    months = int(rng.choice([1, 2, 3, 4, 6, 9, 12], p=[.12, .18, .22, .16, .16, .09, .07]))
    end = min(start + pd.DateOffset(months=months), AS_OF)
    if end < START:
        end = START + pd.Timedelta(days=int(rng.integers(20, 60)))
    fee_type = rng.choice(["Hourly", "Fixed Fee", "Capped"], p=[0.65, 0.20, 0.15])
    partner = rng.choice(partners)
    team = [partner] + list(rng.choice(non_partners.staff_id, size=int(rng.integers(2, 7)), replace=False))
    eng_rows.append({
        "engagement_id": f"E{e:05d}",
        "client_id": client.client_id,
        "engagement_name": f"{rng.choice(PRACTICES)} - {fake.bs().title()}"[:80],
        "practice": rng.choice(PRACTICES),
        "billing_partner_id": partner,
        "fee_type": fee_type,
        "agreed_discount_pct": float(rng.choice([0, 0, 0.05, 0.10, 0.15])),
        "start_date": start.normalize(),
        "end_date": end.normalize(),
        "h_team": team,
        "h_intensity": float(rng.uniform(0.14, 0.43)),  # share of business days each member logs time
    })
engagements = pd.DataFrame(eng_rows)

# --------------------------------------------------------------------------- time entries
st = staff.set_index("staff_id")
te_rows = []
tid = 0
for e in engagements.itertuples():
    days = pd.bdate_range(max(e.start_date, START), e.end_date)  # history before 2024 is not in the extract
    if len(days) == 0:
        continue
    for member in e.h_team:
        mask = rng.random(len(days)) < e.h_intensity * (0.5 if member == e.billing_partner_id else 1)
        for d in days[mask]:
            hrs = float(np.clip(np.round(rng.gamma(2.2, 1.4) * 4) / 4, 0.25, 10))
            prof = st.at[member, "h_late_profile"]
            lag = int(rng.choice([0, 1, 2, 3, 5]) if prof == "normal" and rng.random() < 0.85
                      else rng.gamma(2.0, 9 if prof == "chronic" else 4))
            entered = d + pd.Timedelta(days=lag)
            if entered > AS_OF:
                continue  # not entered yet as of the snapshot
            tid += 1
            rate = int(st.at[member, "standard_rate"])
            te_rows.append((f"T{tid:07d}", e.engagement_id, member, d, entered, hrs, rate, round(hrs * rate, 2)))
time_entries = pd.DataFrame(te_rows, columns=[
    "entry_id", "engagement_id", "staff_id", "work_date", "entry_date", "hours", "standard_rate", "standard_value"])
time_entries["entry_lag_days"] = (time_entries.entry_date - time_entries.work_date).dt.days

# --------------------------------------------------------------------------- billing (monthly cycles)
# Entries are billed on the 10th of the month after they were ENTERED (late entries miss the cycle),
# unless the engagement's partner holds billing (WIP sits 2-6 extra months), and nothing is billed after AS_OF.
eng = engagements.set_index("engagement_id")
te = time_entries.merge(engagements[["engagement_id", "billing_partner_id", "fee_type", "agreed_discount_pct", "client_id"]],
                        on="engagement_id")
cycle = (te.entry_date + pd.offsets.MonthBegin(1)).dt.normalize() + pd.Timedelta(days=9)
u = rng.random(len(te))
hold = (te.billing_partner_id.isin(hold_partners) & (u < 0.55)) | (~te.billing_partner_id.isin(hold_partners) & (u < 0.03))
extra = pd.to_timedelta(np.where(hold, rng.integers(2, 7, len(te)) * 30, 0), unit="D")
te["bill_date"] = (cycle + extra)
te.loc[te.bill_date > AS_OF, "bill_date"] = pd.NaT

# Realization: discount, plus write-downs that grow with lateness, plus fee-type overruns
late_wd = np.select([te.entry_lag_days >= 30, te.entry_lag_days >= 8], [rng.uniform(0.12, 0.30, len(te)), rng.uniform(0.03, 0.10, len(te))], 0)
fee_wd = np.select([te.fee_type == "Fixed Fee", te.fee_type == "Capped"], [rng.uniform(0.15, 0.35, len(te)), rng.uniform(0.05, 0.20, len(te))], 0)
base_wd = rng.uniform(0, 0.04, len(te))
te["billed_value"] = (te.standard_value * (1 - te.agreed_discount_pct) * (1 - np.clip(late_wd + fee_wd + base_wd, 0, 0.6))).round(2)

billed = te[te.bill_date.notna()].copy()
inv = (billed.groupby(["engagement_id", "client_id", "bill_date"], as_index=False)
       .agg(standard_value=("standard_value", "sum"), invoice_amount=("billed_value", "sum")))
inv = inv.sort_values(["bill_date", "engagement_id"]).reset_index(drop=True)
inv["invoice_id"] = [f"INV{n:06d}" for n in range(100001, 100001 + len(inv))]
inv = inv.merge(clients[["client_id", "payment_terms_days", "h_behaviour"]], on="client_id")
inv["invoice_date"] = inv.bill_date
inv["due_date"] = inv.invoice_date + pd.to_timedelta(inv.payment_terms_days, unit="D")
inv["invoice_amount"] = inv.invoice_amount.round(2)
inv["standard_value"] = inv.standard_value.round(2)
billed = billed.merge(inv[["engagement_id", "bill_date", "invoice_id"]], on=["engagement_id", "bill_date"])
time_entries = time_entries.merge(billed[["entry_id", "invoice_id", "billed_value"]], on="entry_id", how="left")

# --------------------------------------------------------------------------- payments
DAYS_TO_PAY = {"prompt": (22, 6), "average": (38, 10), "slow": (70, 20), "very_slow": (115, 30), "problem": (200, 60)}
NEVER = {"prompt": 0.001, "average": 0.003, "slow": 0.01, "very_slow": 0.025, "problem": 0.22}
pay_rows, pid = [], 0
for r in inv.itertuples():
    if rng.random() < NEVER[r.h_behaviour]:
        continue
    mu, sd = DAYS_TO_PAY[r.h_behaviour]
    paid_on = r.invoice_date + pd.Timedelta(days=int(max(5, rng.normal(mu, sd))))
    if paid_on > AS_OF:
        continue
    amounts = [r.invoice_amount]
    if rng.random() < 0.08 and r.invoice_amount > 5000:      # occasional partial payment
        part = round(r.invoice_amount * rng.uniform(0.3, 0.7), 2)
        amounts = [part] if paid_on + pd.Timedelta(days=45) > AS_OF else [part, round(r.invoice_amount - part, 2)]
    for k, amt in enumerate(amounts):
        received = paid_on + pd.Timedelta(days=45 * k)
        if received > AS_OF:
            break
        pid += 1
        # cash application: normally 1-5 days; migration window Mar-Apr 2026 creates a backlog; some never applied
        migration = pd.Timestamp("2026-03-01") <= received <= pd.Timestamp("2026-04-30")
        p_unapplied = 0.22 if migration else 0.025
        if rng.random() < p_unapplied:
            applied = received + pd.Timedelta(days=int(rng.integers(20, 160)))
            applied = applied if applied <= AS_OF and rng.random() < 0.6 else pd.NaT
        else:
            applied = received + pd.Timedelta(days=int(rng.integers(0, 6)))
            applied = applied if applied <= AS_OF else pd.NaT
        pay_rows.append({
            "payment_id": f"P{pid:06d}",
            "client_id": r.client_id,
            "received_date": received.normalize(),
            "amount": amt,
            "remittance_invoice_id": r.invoice_id,            # what the payment was meant for
            "applied_invoice_id": r.invoice_id if pd.notna(applied) else None,
            "applied_date": applied.normalize() if pd.notna(applied) else pd.NaT,
            "method": rng.choice(["ACH", "Wire", "Check"], p=[0.6, 0.25, 0.15]),
        })
payments = pd.DataFrame(pay_rows)

# --------------------------------------------------------------------------- open AR, collections history, exceptions
applied = payments[payments.applied_invoice_id.notna()].groupby("applied_invoice_id").amount.sum()
inv["amount_applied"] = inv.invoice_id.map(applied).fillna(0).round(2)
inv["balance"] = (inv.invoice_amount - inv.amount_applied).clip(lower=0).round(2)
# Bad-debt write-offs: invoices still unpaid about a year after issue get written off (unless disputed/on a plan later)
wo_date = inv.invoice_date + pd.to_timedelta(365 + rng.integers(0, 90, len(inv)), unit="D")
wo = (inv.balance > 0.01) & (wo_date <= AS_OF)
inv["write_off_amount"] = np.where(wo, inv.balance, 0.0).round(2)
inv["write_off_date"] = wo_date.where(wo)
inv["balance"] = (inv.balance - inv.write_off_amount).round(2)
inv["days_past_due"] = (AS_OF - inv.due_date).dt.days

coll_rows, cid = [], 0
exc_rows = []
for r in inv[(inv.days_past_due > 0)].itertuples():
    # history of contacts on invoices that went past due (paid or not)
    paid_date = payments.loc[payments.remittance_invoice_id == r.invoice_id, "received_date"].max() if r.balance == 0 else pd.NaT
    horizon = paid_date if pd.notna(paid_date) else AS_OF
    if horizon <= r.due_date + pd.Timedelta(days=10):
        continue
    d = r.due_date + pd.Timedelta(days=int(rng.integers(7, 25)))
    while d < horizon and rng.random() < 0.8:
        cid += 1
        outcome = rng.choice(["No response", "Promise to pay", "Acknowledged", "Dispute"], p=[0.45, 0.30, 0.20, 0.05])
        promise = d + pd.Timedelta(days=int(rng.integers(7, 30))) if outcome == "Promise to pay" else pd.NaT
        coll_rows.append({"contact_id": f"CT{cid:06d}", "invoice_id": r.invoice_id, "contact_date": d.normalize(),
                          "method": rng.choice(["Email", "Phone", "Partner call"], p=[0.6, 0.3, 0.1]),
                          "outcome": outcome, "promised_date": promise})
        if outcome == "Dispute" and r.balance > 0:
            exc_rows.append({"invoice_id": r.invoice_id, "exception_type": "Disputed", "flag_date": d.normalize()})
            break
        d = d + pd.Timedelta(days=int(rng.integers(14, 40)))
collections_log = pd.DataFrame(coll_rows)
open_late = inv[(inv.balance > 0) & (inv.days_past_due > 60)]
plan = open_late.sample(frac=0.06, random_state=SEED)
for r in plan.itertuples():
    exc_rows.append({"invoice_id": r.invoice_id, "exception_type": "Payment plan", "flag_date": (AS_OF - pd.Timedelta(days=int(rng.integers(5, 90)))).normalize()})
ar_exceptions = pd.DataFrame(exc_rows).drop_duplicates("invoice_id")

# --------------------------------------------------------------------------- write
def save(df, name, drop=()):
    df = df.drop(columns=[c for c in df.columns if c.startswith("h_")] + list(drop), errors="ignore")
    for c in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[c]):
            df[c] = df[c].dt.strftime("%Y-%m-%d")
    df.to_csv(OUT / f"{name}.csv", index=False)
    print(f"{name:18s} {len(df):>8,} rows  {(OUT / f'{name}.csv').stat().st_size / 1e6:6.1f} MB")

save(staff, "staff")
save(clients, "clients")
save(engagements, "engagements")
save(time_entries, "time_entries")
save(inv[["invoice_id", "engagement_id", "client_id", "invoice_date", "due_date", "standard_value", "invoice_amount",
          "write_off_amount", "write_off_date"]], "invoices")
save(payments, "payments")
save(collections_log, "collections_log")
save(ar_exceptions, "ar_exceptions")
print("as of", AS_OF.date(), "| billing-hold partners:", sorted(hold_partners), "| problem clients:", len(problem_clients))
