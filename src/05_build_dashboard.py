"""Step 5 - Build a self-contained HTML dashboard (works offline / on GitHub Pages).

Reads reports/key_findings.json + reports/figures/*.png -> dashboard/index.html
"""
import base64
import json
from config import ROOT, FIG, REPORTS

K = json.loads((REPORTS / "key_findings.json").read_text())
OUT = ROOT / "dashboard" / "index.html"
OUT.parent.mkdir(exist_ok=True)


def img(name, alt):
    b64 = base64.b64encode((FIG / name).read_bytes()).decode()
    return f'<img alt="{alt}" src="data:image/png;base64,{b64}">'


def usd(x, d=0):
    return f"{'-' if x < 0 else ''}${abs(x):,.{d}f}"


y = K["yearly"]
kpis = [
    ("Total sales", usd(K["total_sales"] / 1e6, 2) + "M", "2015-2018"),
    ("Total profit", usd(K["total_profit"] / 1e3, 0) + "K", f"{K['total_margin']:.1f}% margin"),
    ("Sales growth", f"+{(y[-1]['sales'] / y[0]['sales'] - 1) * 100:.0f}%", "2018 vs 2015"),
    ("Orders", f"{K['total_orders']:,}", f"{K['total_customers']:,} customers"),
    ("Profit lost to >20% discounts", usd(-K["loss_hi"] / 1e3, 0) + "K", f"{K['leak_pct']:.0f}% of profit made elsewhere"),
]
kpi_html = "".join(f'<div class="kpi"><span>{a}</span><b>{b}</b><small>{c}</small></div>' for a, b, c in kpis)

sections = [
    ("1 &middot; Overall performance", "Sales grew 51% from 2015 to 2018, but margin peaked in 2017 and slipped in 2018.",
     [("01_yearly_performance.png", "Yearly performance"), ("10_region.png", "Region")],
     [f"Sales: ${y[0]['sales']/1e3:,.0f}K (2015) &rarr; ${y[-1]['sales']/1e3:,.0f}K (2018); 2016 dipped {y[1]['sales_yoy']:.1f}%.",
      f"Average order value fell from ${y[0]['aov']:,.0f} to ${y[-1]['aov']:,.0f} while orders rose {(y[-1]['orders']/y[0]['orders']-1)*100:.0f}%: growth is more, smaller orders.",
      "Central has the lowest margin (7.9%) and the heaviest discounting (24% average)."]),
    ("2 &middot; Product sub-categories", "A few high-growth, high-margin lines carry the business; three sub-categories lose money.",
     [("02_subcategory_growth.png", "Sub-category growth"), ("03_subcategory_profit.png", "Sub-category profit"), ("04_margin_heatmap.png", "Margin heatmap")],
     ["Tables lose $17.7K on $207K sales (-8.6% margin); Bookcases and Supplies also negative.",
      "Copiers: +80% sales CAGR with a 37% margin. Machines: shrinking (-11% CAGR) and loss-making in 2018.",
      f"{K['tables_hi_share']:.0f}% of Tables lines are discounted by more than 20%."]),
    ("3 &middot; Promotion effectiveness", "Discounts above 20% cost margin and do not buy volume.",
     [("05_discount_effectiveness.png", "Discount effectiveness"), ("06_discount_leakage.png", "Discount leakage")],
     [f"Margin is {K['zero_disc_margin']:.1f}% at no discount, 11.6% at 11-20%, and negative above 20%.",
      "Average quantity per line is ~3.7-3.9 in every band: deeper discounts do not coincide with bigger baskets.",
      f"Lines above 20% discount are {K['hi_lines_share']:.0f}% of volume but erase {usd(-K['loss_hi']/1e3)}K ({K['leak_pct']:.0f}%) of the profit earned at &le;20%.",
      f"Losses on loss-making lines rose from ${K['loss_by_year']['2015']/1e3:,.0f}K (2015) to ${K['loss_by_year']['2018']/1e3:,.0f}K (2018) at a flat ~15.6% average discount."]),
    ("4 &middot; Customer behaviour & growth", "Growth comes from existing customers; acquisition has almost stopped.",
     [("07_new_vs_returning.png", "New vs returning"), ("08_retention.png", "Retention"), ("09_customer_pareto.png", "Pareto"), ("11_rfm_segments.png", "RFM")],
     ["New customers per year: 136 (2016) &rarr; 51 (2017) &rarr; 11 (2018). 2015 is the first year in the data, so all its customers count as new.",
      "Retention improved from 73% to 87%; 98% of customers order at least twice.",
      f"Top 20% of customers generate {K['top20_share']:.0f}% of sales; RFM Champions are 24% of customers and 40% of sales."]),
]
sec_html = ""
for title, lead, imgs, bullets in sections:
    figs = "".join(f"<figure>{img(f, a)}</figure>" for f, a in imgs)
    lis = "".join(f"<li>{b}</li>" for b in bullets)
    sec_html += f'<section><h2>{title}</h2><p class="lead">{lead}</p><div class="grid">{figs}</div><ul>{lis}</ul></section>'

recs = [
    "Cap discounts at 20% with manager approval above that threshold.",
    "Re-price or restructure Tables, Bookcases and Supplies.",
    "Review the Central region's discount policy.",
    "Invest in Copiers, Accessories and Appliances; bundle high-margin Paper, Labels and Envelopes.",
    "Restart customer acquisition; run win-back for At Risk and a loyalty tier for Champions.",
]
rec_html = "".join(f"<li>{r}</li>" for r in recs)

HTML = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Sales Performance Report &middot; Superstore 2015-2018</title>
<style>
:root{--bg:#f8fafc;--card:#fff;--ink:#0f172a;--mut:#64748b;--line:#e2e8f0;--acc:#2563eb}
@media (prefers-color-scheme:dark){:root{--bg:#0b1220;--card:#111a2e;--ink:#e5e7eb;--mut:#94a3b8;--line:#1f2a44;--acc:#60a5fa}
 figure img{background:#fff;border-radius:8px}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.55 system-ui,-apple-system,Segoe UI,Roboto,sans-serif}
header{padding:40px 20px 24px;max-width:1100px;margin:auto}
h1{margin:0 0 6px;font-size:clamp(1.6rem,4vw,2.3rem)}header p{margin:0;color:var(--mut)}
main{max-width:1100px;margin:auto;padding:0 20px 60px}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:12px;margin:8px 0 28px}
.kpi{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:14px 16px;display:flex;flex-direction:column}
.kpi span{color:var(--mut);font-size:.8rem}.kpi b{font-size:1.6rem;margin:2px 0}.kpi small{color:var(--mut)}
section{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:22px;margin-bottom:20px}
h2{margin:0 0 4px;font-size:1.25rem}.lead{margin:0 0 14px;color:var(--mut)}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,420px),1fr));gap:14px}
figure{margin:0}figure img{width:100%;height:auto;display:block}
ul{padding-left:20px;margin:14px 0 0}li{margin:4px 0}
.rec{border-left:4px solid var(--acc)}
footer{max-width:1100px;margin:auto;padding:0 20px 40px;color:var(--mut);font-size:.85rem}
</style></head><body>
<header><h1>Sales Performance Report</h1>
<p>Superstore &middot; 2015-2018 &middot; overall performance, promotion effectiveness, customer behaviour</p></header>
<main>
<div class="kpis">__KPIS__</div>
__SECTIONS__
<section class="rec"><h2>5 &middot; Recommendations</h2><ol>__RECS__</ol></section>
</main>
<footer>Discount is used as a proxy for promotions (no campaign data in the source). Findings show association, not causation. Source: Superstore sample dataset.</footer>
</body></html>"""
OUT.write_text(HTML.replace("__KPIS__", kpi_html).replace("__SECTIONS__", sec_html).replace("__RECS__", rec_html), encoding="utf-8")
print("Saved", OUT, f"({OUT.stat().st_size/1e6:.1f} MB)")
