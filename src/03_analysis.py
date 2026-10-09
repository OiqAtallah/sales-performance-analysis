"""Step 3 - Analysis & figures (pandas + matplotlib).

Reads data/processed/orders_clean.csv, writes PNG charts to reports/figures and a
machine-readable summary to reports/key_findings.json (used by dashboard & slides).
"""
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from config import CLEAN, FIG, REPORTS, BAND_LABELS, BLUE, TEAL, RED, AMBER, GREY, INK

FIG.mkdir(parents=True, exist_ok=True)
plt.rcParams.update({
    "figure.dpi": 150, "savefig.dpi": 150, "savefig.bbox": "tight",
    "font.family": "DejaVu Sans", "font.size": 10,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.edgecolor": GREY, "axes.labelcolor": INK, "xtick.color": INK, "ytick.color": INK,
    "axes.titleweight": "bold", "axes.titlesize": 12, "axes.titlelocation": "left",
})
def money_k(x, d=0):
    return f"{'-' if x < 0 else ''}${abs(x)/1000:,.{d}f}K"


usd_k = FuncFormatter(lambda x, _: money_k(x))

df = pd.read_csv(CLEAN, parse_dates=["order_date", "ship_date"])
years = sorted(df.order_year.unique())
first_y, last_y = years[0], years[-1]
K = {}  # key findings

# ---------- 1. Yearly performance ----------
y = df.groupby("order_year").agg(sales=("sales", "sum"), profit=("profit", "sum"),
                                  orders=("order_id", "nunique"), customers=("customer_id", "nunique"))
y["margin"] = y.profit / y.sales * 100
y["aov"] = y.sales / y.orders
y["sales_yoy"] = y.sales.pct_change() * 100
K["total_sales"] = df.sales.sum(); K["total_profit"] = df.profit.sum()
K["total_margin"] = K["total_profit"] / K["total_sales"] * 100
K["total_orders"] = int(df.order_id.nunique()); K["total_customers"] = int(df.customer_id.nunique())
K["yearly"] = y.reset_index().round(2).to_dict("records")

fig, ax = plt.subplots(figsize=(8, 4.2))
x = np.arange(len(y)); w = 0.38
ax.bar(x - w/2, y.sales, w, color=BLUE, label="Sales")
ax.bar(x + w/2, y.profit, w, color=TEAL, label="Profit")
ax.set_xticks(x, y.index); ax.yaxis.set_major_formatter(usd_k)
for i, (s, p) in enumerate(zip(y.sales, y.profit)):
    ax.text(i - w/2, s, f"${s/1000:,.0f}K", ha="center", va="bottom", fontsize=8)
    ax.text(i + w/2, p, f"${p/1000:,.0f}K", ha="center", va="bottom", fontsize=8)
ax2 = ax.twinx(); ax2.plot(x, y.margin, color=AMBER, marker="o", lw=2, label="Margin %")
ax2.set_ylim(0, 20); ax2.spines["right"].set_visible(True); ax2.spines["right"].set_color(GREY)
ax2.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:.0f}%"))
for i, m in enumerate(y.margin): ax2.text(i, m + 0.9, f"{m:.1f}%", ha="center", color=AMBER, fontsize=8, fontweight="bold")
h1, l1 = ax.get_legend_handles_labels(); h2, l2 = ax2.get_legend_handles_labels()
ax.legend(h1 + h2, l1 + l2, loc="upper left", frameon=False, ncol=3)
ax.set_title("Sales, profit and margin by year")
fig.savefig(FIG / "01_yearly_performance.png"); plt.close(fig)

# ---------- 2. Sub-category growth & profit ----------
sc_year = df.pivot_table(index="sub_category", columns="order_year", values="sales", aggfunc="sum")
n = last_y - first_y
cagr = ((sc_year[last_y] / sc_year[first_y]) ** (1 / n) - 1) * 100
sc = df.groupby("sub_category").agg(sales=("sales", "sum"), profit=("profit", "sum"))
sc["margin"] = sc.profit / sc.sales * 100
sc["cagr"] = cagr
K["subcat"] = sc.round(2).reset_index().to_dict("records")

c = cagr.sort_values()
fig, ax = plt.subplots(figsize=(7, 5.4))
ax.barh(c.index, c.values, color=[RED if v < 0 else BLUE for v in c.values])
for i, v in enumerate(c.values):
    ax.text(v + (2 if v >= 0 else -2), i, f"{v:+.0f}%", va="center", ha="left" if v >= 0 else "right", fontsize=8)
ax.axvline(0, color=INK, lw=0.8); ax.set_xlim(-30, 95)
ax.set_xlabel(f"Sales CAGR {first_y}-{last_y}"); ax.set_title("Which sub-categories are growing?")
fig.savefig(FIG / "02_subcategory_growth.png"); plt.close(fig)

p = sc.profit.sort_values()
fig, ax = plt.subplots(figsize=(7, 5.4))
ax.barh(p.index, p.values, color=[RED if v < 0 else TEAL for v in p.values])
for i, (name, v) in enumerate(p.items()):
    m = sc.loc[name, "margin"]
    ax.text(v + (1500 if v >= 0 else -1500), i, f"{money_k(v, 1)}  ({m:.0f}%)", va="center",
            ha="left" if v >= 0 else "right", fontsize=8)
ax.axvline(0, color=INK, lw=0.8); ax.xaxis.set_major_formatter(usd_k); ax.set_xlim(-45000, 80000)
ax.set_title("Total profit by sub-category (margin in brackets)")
fig.savefig(FIG / "03_subcategory_profit.png"); plt.close(fig)

# margin heatmap
mh = df.pivot_table(index="sub_category", columns="order_year", values=["profit", "sales"], aggfunc="sum")
mh = (mh["profit"] / mh["sales"] * 100).loc[sc.sort_values("profit").index]
fig, ax = plt.subplots(figsize=(6, 5.6))
im = ax.imshow(mh.values, cmap="RdYlGn", vmin=-30, vmax=40, aspect="auto")
ax.set_xticks(range(len(mh.columns)), mh.columns); ax.set_yticks(range(len(mh.index)), mh.index)
for i in range(mh.shape[0]):
    for j in range(mh.shape[1]):
        ax.text(j, i, f"{mh.values[i, j]:.0f}%", ha="center", va="center", fontsize=8)
ax.spines[:].set_visible(False); ax.set_title("Profit margin by sub-category and year")
fig.savefig(FIG / "04_margin_heatmap.png"); plt.close(fig)

# ---------- 3. Promotion (discount) effectiveness ----------
b = df.groupby("discount_band").agg(lines=("sales", "size"), sales=("sales", "sum"), profit=("profit", "sum"),
                                    qty=("quantity", "mean"), loss_pct=("is_loss", "mean")).reindex(BAND_LABELS)
b["margin"] = b.profit / b.sales * 100; b["share"] = b.sales / b.sales.sum() * 100
K["bands"] = b.round(2).reset_index().to_dict("records")
hi = df[df.discount > 0.20]; lo = df[df.discount <= 0.20]
K["profit_lo"] = lo.profit.sum(); K["loss_hi"] = hi.profit.sum()
K["hi_sales_share"] = hi.sales.sum() / df.sales.sum() * 100
K["hi_lines_share"] = len(hi) / len(df) * 100
K["leak_pct"] = -hi.profit.sum() / lo.profit.sum() * 100
K["zero_disc_margin"] = b.loc["0%", "margin"]

fig, axes = plt.subplots(1, 2, figsize=(10, 4.2), gridspec_kw={"width_ratios": [1.25, 1]})
ax = axes[0]
ax.bar(b.index, b.margin, color=[TEAL if v >= 0 else RED for v in b.margin])
for i, v in enumerate(b.margin):
    ax.text(i, v + (3 if v >= 0 else -3), f"{v:.1f}%", ha="center", va="bottom" if v >= 0 else "top", fontsize=9, fontweight="bold")
ax.axhline(0, color=INK, lw=0.8); ax.set_ylim(-140, 45)
ax.set_xlabel("Discount band"); ax.set_ylabel("Profit margin"); ax.set_title("Margin collapses above 20% discount")
ax = axes[1]
ax.bar(b.index, b.qty, color=BLUE)
for i, v in enumerate(b.qty): ax.text(i, v + 0.05, f"{v:.2f}", ha="center", fontsize=9)
ax.set_ylim(0, 5); ax.set_xlabel("Discount band"); ax.set_ylabel("Avg. quantity per order line")
ax.set_title("...without selling more units")
fig.tight_layout(); fig.savefig(FIG / "05_discount_effectiveness.png"); plt.close(fig)

leak = df.assign(hi=np.where(df.discount > 0.20, "Discount > 20%", "Discount <= 20%")) \
         .pivot_table(index="sub_category", columns="hi", values="profit", aggfunc="sum").fillna(0)
leak = leak.sort_values("Discount > 20%").head(8)
fig, ax = plt.subplots(figsize=(7.5, 4.2))
yy = np.arange(len(leak))
ax.barh(yy + 0.2, leak["Discount <= 20%"], 0.4, color=TEAL, label="Profit at discount <= 20%")
ax.barh(yy - 0.2, leak["Discount > 20%"], 0.4, color=RED, label="Profit at discount > 20%")
ax.set_yticks(yy, leak.index); ax.invert_yaxis(); ax.xaxis.set_major_formatter(usd_k); ax.axvline(0, color=INK, lw=0.8)
ax.legend(frameon=False, loc="lower right"); ax.set_title("Where deep discounts destroy profit")
fig.savefig(FIG / "06_discount_leakage.png"); plt.close(fig)

# loss trend
loss = df[df.profit < 0].groupby("order_year").profit.sum().abs()
K["loss_by_year"] = loss.round(2).to_dict()
K["avg_discount_by_year"] = (df.groupby("order_year").discount.mean() * 100).round(2).to_dict()

# ---------- 4. Customers ----------
first = df.groupby("customer_id").order_year.min().rename("first_year")
d2 = df.join(first, on="customer_id")
nv = d2.groupby("order_year").apply(lambda g: pd.Series({
    "new": g.loc[g.first_year == g.name, "customer_id"].nunique(),
    "returning": g.loc[g.first_year < g.name, "customer_id"].nunique(),
    "new_sales": g.loc[g.first_year == g.name, "sales"].sum(),
    "returning_sales": g.loc[g.first_year < g.name, "sales"].sum()}), include_groups=False)
active = df.groupby("order_year").customer_id.apply(set)
ret = pd.Series({yr: len(active[yr] & active[yr + 1]) / len(active[yr]) * 100 for yr in years[:-1]})
K["new_vs_returning"] = nv.round(2).reset_index().to_dict("records")
K["retention"] = ret.round(2).to_dict()
orders_per_cust = df.groupby("customer_id").order_id.nunique()
K["pct_repeat_customers"] = (orders_per_cust >= 2).mean() * 100
K["median_orders_per_customer"] = float(orders_per_cust.median())
cs = df.groupby("customer_id").sales.sum().sort_values(ascending=False)
K["top20_share"] = cs.head(int(len(cs) * 0.2)).sum() / cs.sum() * 100

fig, ax = plt.subplots(figsize=(8, 4.2))
ax.bar(nv.index.astype(str), nv.returning, color=BLUE, label="Returning customers")
ax.bar(nv.index.astype(str), nv.new, bottom=nv.returning, color=AMBER, label="New customers")
for i, (r, nw) in enumerate(zip(nv.returning, nv.new)):
    if nw > 25: ax.text(i, r + nw / 2, f"{nw:.0f}", ha="center", va="center", color="white", fontsize=9, fontweight="bold")
    elif nw > 0: ax.text(i, r + nw + 10, f"{nw:.0f} new", ha="center", fontsize=8, color=AMBER, fontweight="bold")
    if r > 0: ax.text(i, r / 2, f"{r:.0f}", ha="center", va="center", color="white", fontsize=9, fontweight="bold")
ax.set_ylabel("Active customers"); ax.legend(frameon=False, loc="upper left", ncol=2)
ax.set_title(f"Customer base: new vs returning ({first_y} = first year in data, so all 'new')")
fig.savefig(FIG / "07_new_vs_returning.png"); plt.close(fig)

fig, ax = plt.subplots(figsize=(6.5, 4.2))
ax.plot(ret.index.astype(str), ret.values, marker="o", color=TEAL, lw=2.5)
for xi, v in zip(ret.index.astype(str), ret.values): ax.text(xi, v + 1.5, f"{v:.0f}%", ha="center", fontweight="bold")
ax.set_ylim(50, 100); ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:.0f}%"))
ax.set_ylabel("Share ordering again next year"); ax.set_title("Year-over-year customer retention")
fig.savefig(FIG / "08_retention.png"); plt.close(fig)

cum = cs.cumsum() / cs.sum() * 100
fig, ax = plt.subplots(figsize=(6.5, 4.2))
ax.plot(np.arange(1, len(cum) + 1) / len(cum) * 100, cum.values, color=BLUE, lw=2.5)
ax.plot([0, 100], [0, 100], color=GREY, ls="--", lw=1)
ax.axvline(20, color=AMBER, ls=":"); ax.scatter([20], [K["top20_share"]], color=AMBER, zorder=5)
ax.annotate(f"Top 20% of customers\n= {K['top20_share']:.0f}% of sales", (20, K["top20_share"]), xytext=(32, 30),
            arrowprops=dict(arrowstyle="->", color=INK), fontsize=9)
ax.set_xlabel("% of customers (ranked by sales)"); ax.set_ylabel("Cumulative % of sales"); ax.set_title("Customer concentration")
fig.savefig(FIG / "09_customer_pareto.png"); plt.close(fig)

# ---------- 5. Region / segment ----------
rg = df.groupby("region").agg(sales=("sales", "sum"), profit=("profit", "sum")); rg["margin"] = rg.profit / rg.sales * 100
sg = df.groupby("segment").agg(sales=("sales", "sum"), profit=("profit", "sum")); sg["margin"] = sg.profit / sg.sales * 100
K["region"] = rg.round(2).reset_index().to_dict("records"); K["segment"] = sg.round(2).reset_index().to_dict("records")
fig, ax = plt.subplots(figsize=(6.5, 4))
rs = rg.sort_values("sales", ascending=False)
ax.bar(rs.index, rs.sales, color=BLUE); ax.yaxis.set_major_formatter(usd_k)
ax3 = ax.twinx(); ax3.plot(rs.index, rs.margin, color=AMBER, marker="o", lw=2); ax3.set_ylim(0, 20)
ax3.spines["right"].set_visible(True); ax3.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:.0f}%"))
for i, m in enumerate(rs.margin): ax3.text(i, m + 0.8, f"{m:.1f}%", ha="center", color=AMBER, fontsize=9, fontweight="bold")
ax.set_title("Sales (bars) and margin (line) by region")
fig.savefig(FIG / "10_region.png"); plt.close(fig)

# region discount diagnostics
rd = df.groupby("region").apply(lambda x: pd.Series({
    "avg_discount": x.discount.mean() * 100,
    "hi_disc_line_share": (x.discount > 0.2).mean() * 100,
    "profit_hi_disc": x.loc[x.discount > 0.2, "profit"].sum(),
    "margin": x.profit.sum() / x.sales.sum() * 100,
    "margin_excl_hi_disc": x.loc[x.discount <= 0.2, "profit"].sum() / x.loc[x.discount <= 0.2, "sales"].sum() * 100}),
    include_groups=False)
K["region_discount"] = rd.round(2).reset_index().to_dict("records")
tb = df[df.sub_category == "Tables"]
K["tables_hi_share"] = (tb.discount > 0.2).mean() * 100
K["tables_profit_lo"] = tb.loc[tb.discount <= 0.2, "profit"].sum()
K["tables_profit_hi"] = tb.loc[tb.discount > 0.2, "profit"].sum()
mc = df[df.sub_category == "Machines"].groupby("order_year").agg(sales=("sales", "sum"), profit=("profit", "sum"))
K["machines"] = mc.round(2).reset_index().to_dict("records")

# ---------- Save ----------
def clean(o):
    if isinstance(o, dict): return {str(k): clean(v) for k, v in o.items()}
    if isinstance(o, list): return [clean(v) for v in o]
    if isinstance(o, (np.integer,)): return int(o)
    if isinstance(o, (np.floating, float)): return None if np.isnan(o) else round(float(o), 2)
    return o
(REPORTS / "key_findings.json").write_text(json.dumps(clean(K), indent=2, allow_nan=False))
print("Figures:", len(list(FIG.glob("*.png"))), "| key findings saved")
for k in ["total_sales", "total_profit", "total_margin", "profit_lo", "loss_hi", "hi_sales_share", "hi_lines_share", "leak_pct", "top20_share", "pct_repeat_customers"]:
    print(f"{k:22s} {K[k]:,.2f}")
