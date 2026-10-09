"""Step 1 - Data cleaning & validation.

Input : data/raw/superstore.csv
Output: data/processed/orders_clean.csv, reports/data_quality.md
"""
import pandas as pd
from config import RAW, CLEAN, BAND_EDGES, BAND_LABELS, REPORTS

log = []


def note(msg):
    print(msg)
    log.append(msg)


raw = pd.read_csv(RAW)
note(f"Raw file rows: {len(raw):,}")

# 1. The export contains extra worksheets (People / Returns) appended below the
#    orders table. They have no Order Date, so they are dropped.
df = raw.dropna(subset=["Order Date"]).copy()
note(f"Dropped {len(raw) - len(df):,} non-order rows (appended 'People'/'Returns' sheets)")

# 2. Standardise column names
df.columns = (
    df.columns.str.strip().str.lower().str.replace(r"[^a-z0-9]+", "_", regex=True).str.strip("_")
)

# 3. Types
df["order_date"] = pd.to_datetime(df["order_date"], format="%m/%d/%Y")
df["ship_date"] = pd.to_datetime(df["ship_date"], format="%m/%d/%Y")
df["row_id"] = df["row_id"].astype(int)
df["quantity"] = df["quantity"].astype(int)

# 4. Missing postal code: Burlington, Vermont (ZIP 05401)
miss = df["postal_code"].isna()
note(f"Missing postal_code: {miss.sum()} rows (all Burlington, VT) -> filled with 05401")
df.loc[miss, "postal_code"] = 5401
df["postal_code"] = df["postal_code"].astype(int).astype(str).str.zfill(5)

# 5. Validation checks
assert df["row_id"].is_unique, "row_id must be unique"
assert (df["sales"] > 0).all(), "sales must be positive"
assert df["discount"].between(0, 1).all(), "discount must be within [0, 1]"
assert (df["ship_date"] >= df["order_date"]).all(), "ship_date before order_date"
assert df.isna().sum().sum() == 0, "unexpected missing values"
note("Validation passed: unique row_id, sales > 0, 0 <= discount <= 1, ship >= order, no NaN")

dup_lines = df.duplicated(subset=["order_id", "product_id"], keep=False).sum()
note(f"Order lines sharing the same (order_id, product_id): {dup_lines} rows - kept (different quantities/discounts, valid lines)")

# 6. Feature engineering
df["order_year"] = df["order_date"].dt.year
df["order_month"] = df["order_date"].dt.month
df["year_month"] = df["order_date"].dt.to_period("M").astype(str)
df["ship_days"] = (df["ship_date"] - df["order_date"]).dt.days
df["margin_pct"] = df["profit"] / df["sales"] * 100
df["is_loss"] = (df["profit"] < 0).astype(int)
df["discount_band"] = pd.cut(df["discount"], BAND_EDGES, labels=BAND_LABELS).astype(str)

note(f"Clean rows: {len(df):,} | period {df.order_date.min():%Y-%m-%d} to {df.order_date.max():%Y-%m-%d}")
note(f"Orders: {df.order_id.nunique():,} | Customers: {df.customer_id.nunique():,} | Products: {df.product_id.nunique():,}")

df.sort_values("row_id").to_csv(CLEAN, index=False, date_format="%Y-%m-%d")

REPORTS.mkdir(parents=True, exist_ok=True)
with open(REPORTS / "data_quality.md", "w") as f:
    f.write("# Data Quality Log\n\n" + "\n".join(f"- {m}" for m in log) + "\n")
print("Saved", CLEAN)
