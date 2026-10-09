"""Step 4 - RFM customer segmentation.

Recency   = days since last order (snapshot = last order date + 1 day)
Frequency = number of distinct orders
Monetary  = total sales
Each metric is scored 1-4 by quartile rank (4 = best); score = R + F + M (3-12).
"""
import pandas as pd
import matplotlib.pyplot as plt
from config import CLEAN, FIG, TAB, BLUE, TEAL, RED, AMBER, GREY, INK

df = pd.read_csv(CLEAN, parse_dates=["order_date"])
snapshot = df.order_date.max() + pd.Timedelta(days=1)

rfm = df.groupby("customer_id").agg(
    recency=("order_date", lambda s: (snapshot - s.max()).days),
    frequency=("order_id", "nunique"),
    monetary=("sales", "sum"),
    profit=("profit", "sum"),
)
# rank(method="first") breaks ties so quartiles are balanced
rfm["R"] = pd.qcut(rfm.recency.rank(method="first", ascending=False), 4, labels=[1, 2, 3, 4]).astype(int)
rfm["F"] = pd.qcut(rfm.frequency.rank(method="first"), 4, labels=[1, 2, 3, 4]).astype(int)
rfm["M"] = pd.qcut(rfm.monetary.rank(method="first"), 4, labels=[1, 2, 3, 4]).astype(int)
rfm["score"] = rfm[["R", "F", "M"]].sum(axis=1)


def segment(s):
    if s >= 10: return "Champions"
    if s >= 8:  return "Loyal"
    if s >= 6:  return "Potential"
    if s >= 4:  return "At Risk"
    return "Lost"


rfm["segment"] = rfm.score.apply(segment)
order = ["Champions", "Loyal", "Potential", "At Risk", "Lost"]
seg = rfm.groupby("segment").agg(customers=("monetary", "size"), sales=("monetary", "sum"), profit=("profit", "sum"),
                                 avg_recency_days=("recency", "mean"), avg_orders=("frequency", "mean")).reindex(order)
seg["customer_share_pct"] = seg.customers / seg.customers.sum() * 100
seg["sales_share_pct"] = seg.sales / seg.sales.sum() * 100
seg["avg_sales_per_customer"] = seg.sales / seg.customers
seg.round(2).to_csv(TAB / "10_rfm_segments.csv")
rfm.reset_index().round(2).to_csv(TAB / "10_rfm_customers.csv", index=False)
print(seg.round(1))

fig, ax = plt.subplots(figsize=(8, 4.2))
x = range(len(seg)); w = 0.38
ax.bar([i - w/2 for i in x], seg.customer_share_pct, w, color=GREY, label="% of customers")
ax.bar([i + w/2 for i in x], seg.sales_share_pct, w, color=BLUE, label="% of sales")
for i, (a, b) in enumerate(zip(seg.customer_share_pct, seg.sales_share_pct)):
    ax.text(i - w/2, a + 0.6, f"{a:.0f}%", ha="center", fontsize=8); ax.text(i + w/2, b + 0.6, f"{b:.0f}%", ha="center", fontsize=8)
ax.set_xticks(list(x), seg.index); ax.legend(frameon=False)
for sp in ["top", "right"]: ax.spines[sp].set_visible(False)
ax.set_title("RFM segments: share of customers vs share of sales", loc="left", fontweight="bold")
fig.savefig(FIG / "11_rfm_segments.png", dpi=150, bbox_inches="tight")
