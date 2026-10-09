// Build slides/Sales_Performance_Report.pptx from reports/key_findings.json
const pptxgen = require("pptxgenjs");
const fs = require("fs");
const path = require("path");
const K = JSON.parse(fs.readFileSync(path.join(__dirname, "..", "reports", "key_findings.json"), "utf8"));

const C = { ink: "0F172A", mut: "64748B", blue: "2563EB", teal: "0D9488", red: "DC2626", amber: "D97706", bg: "F8FAFC", line: "E2E8F0" };
const F = "Calibri";
const pres = new pptxgen();
pres.layout = "LAYOUT_16x9";
pres.title = "Sales Performance Report - Superstore 2015-2018";
pres.author = "Atallah";

const k = (x) => `${x < 0 ? "-" : ""}$${Math.abs(x / 1000).toFixed(0)}K`;

function base(title, sub) {
  const s = pres.addSlide();
  s.background = { color: "FFFFFF" };
  s.addText(title, { x: 0.5, y: 0.3, w: 9, h: 0.6, fontFace: F, fontSize: 24, bold: true, color: C.ink, margin: 0, isTextBox: true });
  if (sub) s.addText(sub, { x: 0.5, y: 0.9, w: 9, h: 0.4, fontFace: F, fontSize: 13, color: C.mut, margin: 0, isTextBox: true });
  return s;
}
function bullets(s, items, x, y, w, h) {
  s.addText(items.map((t, i) => ({ text: t, options: { bullet: true, breakLine: i < items.length - 1, paraSpaceAfter: 8 } })),
    { x, y, w, h, fontFace: F, fontSize: 13, color: C.ink, valign: "top", margin: 0, isTextBox: true });
}
const axis = { catAxisLabelColor: C.mut, valAxisLabelColor: C.mut, catAxisLabelFontSize: 10, valAxisLabelFontSize: 10,
  valGridLine: { color: C.line, size: 0.5 }, catGridLine: { style: "none" } };

// 1. Title
{
  const s = pres.addSlide(); s.background = { color: C.ink };
  s.addText("Sales Performance Report", { x: 0.6, y: 1.7, w: 8.8, h: 0.9, fontFace: F, fontSize: 40, bold: true, color: "FFFFFF", margin: 0, isTextBox: true });
  s.addText("Superstore 2015-2018: overall performance, promotion effectiveness and customer behaviour", { x: 0.6, y: 2.7, w: 8.2, h: 0.8, fontFace: F, fontSize: 16, color: "CBD5E1", margin: 0, isTextBox: true });
  s.addText("Data Analyst portfolio project  |  SQL, Python, dashboard", { x: 0.6, y: 4.6, w: 8, h: 0.4, fontFace: F, fontSize: 12, color: "94A3B8", margin: 0, isTextBox: true });
}

// 2. Executive summary
{
  const s = base("Executive summary", "Growth is healthy, but discounting and a stalled customer base put it at risk");
  const y = K.yearly;
  const cards = [
    [`$${(K.total_sales / 1e6).toFixed(2)}M`, "Total sales"],
    [`$${(K.total_profit / 1e3).toFixed(0)}K`, `Profit (${K.total_margin.toFixed(1)}% margin)`],
    [`+${((y[3].sales / y[0].sales - 1) * 100).toFixed(0)}%`, "Sales growth 2015 to 2018"],
    [k(K.loss_hi), `Lost on >20% discount lines`],
  ];
  cards.forEach(([v, l], i) => {
    const x = 0.5 + i * 2.28;
    s.addShape(pres.shapes.RECTANGLE, { x, y: 1.5, w: 2.1, h: 1.15, fill: { color: C.bg }, line: { color: C.line, width: 0.75 } });
    s.addText(v, { x, y: 1.58, w: 2.1, h: 0.6, align: "center", fontFace: F, fontSize: 26, bold: true, color: i === 3 ? C.red : C.blue, margin: 0, isTextBox: true });
    s.addText(l, { x, y: 2.2, w: 2.1, h: 0.4, align: "center", fontFace: F, fontSize: 11, color: C.mut, margin: 0, isTextBox: true });
  });
  bullets(s, [
    `Discounts above 20% are ${K.hi_lines_share.toFixed(0)}% of order lines but erase ${K.leak_pct.toFixed(0)}% of the profit earned elsewhere, with no gain in units per order.`,
    "Tables, Bookcases and Supplies lose money; Copiers grows fastest with a 37% margin.",
    "New customers fell from 136 (2016) to 11 (2018): growth relies on a saturated base of about 790 customers.",
  ], 0.5, 3.0, 9, 2.2);
}

// 3. Yearly performance
{
  const s = base("Sales grew 51% since 2015; margin peaked in 2017", "Sales and profit by year (USD)");
  const yrs = K.yearly.map((r) => String(r.order_year));
  s.addChart(pres.charts.BAR, [
    { name: "Sales", labels: yrs, values: K.yearly.map((r) => Math.round(r.sales)) },
    { name: "Profit", labels: yrs, values: K.yearly.map((r) => Math.round(r.profit)) },
  ], { x: 0.5, y: 1.4, w: 5.6, h: 3.9, barDir: "col", barGapWidthPct: 60, chartColors: [C.blue, C.teal], showLegend: true, legendPos: "b", legendFontSize: 10,
       showValue: true, dataLabelFormatCode: "$#,##0,\"K\"", dataLabelFontSize: 9, dataLabelPosition: "outEnd", valAxisLabelFormatCode: "$#,##0,\"K\"", ...axis });
  const y = K.yearly;
  bullets(s, [
    `2016 dipped ${Math.abs(y[1].sales_yoy).toFixed(1)}%, then +${y[2].sales_yoy.toFixed(0)}% (2017) and +${y[3].sales_yoy.toFixed(0)}% (2018).`,
    `Margin: ${y[0].margin.toFixed(1)}% (2015), ${y[2].margin.toFixed(1)}% (2017), ${y[3].margin.toFixed(1)}% (2018).`,
    `Orders up ${((y[3].orders / y[0].orders - 1) * 100).toFixed(0)}% but average order value down from $${y[0].aov.toFixed(0)} to $${y[3].aov.toFixed(0)}.`,
  ], 6.4, 1.6, 3.1, 3.5);
}

// 4. Sub-category profit
{
  const s = base("Three sub-categories lose money", "Total profit by sub-category, 2015-2018 (USD)");
  const sc = [...K.subcat].sort((a, b) => a.profit - b.profit);
  s.addChart(pres.charts.BAR, [{ name: "Profit", labels: sc.map((r) => r.sub_category), values: sc.map((r) => Math.round(r.profit)) }],
    { x: 0.4, y: 1.3, w: 5.8, h: 4.1, barDir: "bar", chartColors: [C.teal], invertedColors: [C.red], showLegend: false, showValue: false,
      valAxisLabelFormatCode: "$#,##0,\"K\"", catAxisOrientation: "maxMin", catAxisLabelPos: "low", ...axis });
  const t = K.subcat.find((r) => r.sub_category === "Tables");
  const c = K.subcat.find((r) => r.sub_category === "Copiers");
  const m = K.subcat.find((r) => r.sub_category === "Machines");
  bullets(s, [
    `Tables: ${k(t.sales)} sales but ${k(t.profit)} profit (${t.margin.toFixed(1)}% margin); ${K.tables_hi_share.toFixed(0)}% of lines discounted over 20%.`,
    `Copiers: sales CAGR +${c.cagr.toFixed(0)}% with a ${c.margin.toFixed(0)}% margin.`,
    `Machines: sales CAGR ${m.cagr.toFixed(0)}% and loss-making in 2018.`,
    "Paper, Labels and Envelopes: 42-44% margins on small revenue; bundling candidates.",
  ], 6.4, 1.5, 3.2, 3.8);
}

// 5. Discount effectiveness
{
  const s = base("Discounts above 20% destroy margin without lifting volume", "Profit margin and average quantity by discount band");
  const b = K.bands;
  s.addChart(pres.charts.BAR, [{ name: "Profit margin %", labels: b.map((r) => r.discount_band), values: b.map((r) => r.margin) }],
    { x: 0.4, y: 1.4, w: 5.3, h: 3.9, barDir: "col", chartColors: [C.teal], invertedColors: [C.red], showLegend: false, showValue: true,
      dataLabelFormatCode: "0.0\"%\"", dataLabelFontSize: 9, dataLabelPosition: "outEnd", valAxisLabelFormatCode: "0\"%\"", showTitle: true, title: "Profit margin by discount band", titleFontSize: 11, titleColor: C.ink, ...axis });
  const q = b.map((r) => r.qty);
  bullets(s, [
    `Margin ${K.zero_disc_margin.toFixed(1)}% at no discount, 11.6% at 11-20%, then negative: -10%, -25%, -119%.`,
    `Average quantity per line stays between ${Math.min(...q).toFixed(1)} and ${Math.max(...q).toFixed(1)} in every band.`,
    `Lines above 20%: ${K.hi_lines_share.toFixed(0)}% of volume, ${k(K.loss_hi)} profit, equal to ${K.leak_pct.toFixed(0)}% of the ${k(K.profit_lo)} earned at 20% or less.`,
    "Discount is a proxy for promotions; the data shows association, not causation.",
  ], 5.95, 1.5, 3.6, 3.8);
}

// 6. Region
{
  const s = base("Central's low margin is a discount problem", "Region view: margin with and without lines discounted over 20%");
  const rows = [[
    { text: "Region", options: { bold: true, color: "FFFFFF", fill: { color: C.ink } } },
    { text: "Margin", options: { bold: true, color: "FFFFFF", fill: { color: C.ink }, align: "right" } },
    { text: "Avg discount", options: { bold: true, color: "FFFFFF", fill: { color: C.ink }, align: "right" } },
    { text: "Lines >20% disc.", options: { bold: true, color: "FFFFFF", fill: { color: C.ink }, align: "right" } },
    { text: "Profit lost >20%", options: { bold: true, color: "FFFFFF", fill: { color: C.ink }, align: "right" } },
    { text: "Margin if <=20%", options: { bold: true, color: "FFFFFF", fill: { color: C.ink }, align: "right" } },
  ]];
  K.region_discount.forEach((r) => rows.push([
    { text: r.region }, { text: r.margin.toFixed(1) + "%", options: { align: "right" } },
    { text: r.avg_discount.toFixed(1) + "%", options: { align: "right" } },
    { text: r.hi_disc_line_share.toFixed(1) + "%", options: { align: "right" } },
    { text: k(r.profit_hi_disc), options: { align: "right", color: C.red } },
    { text: r.margin_excl_hi_disc.toFixed(1) + "%", options: { align: "right" } },
  ]));
  s.addTable(rows, { x: 0.5, y: 1.5, w: 9, colW: [1.6, 1.2, 1.5, 1.6, 1.6, 1.5], fontFace: F, fontSize: 13, color: C.ink, border: { type: "solid", pt: 0.5, color: C.line }, rowH: 0.42 });
  bullets(s, [
    "Central has the lowest margin (7.9%) and the heaviest discounting (24% average, 28% of lines above 20%).",
    "Excluding lines above 20%, Central's margin (24.8%) is on par with East (25.1%): the gap comes from discount policy, not demand.",
  ], 0.5, 3.85, 9, 1.4);
}

// 7. Customers
{
  const s = base("Growth comes from existing customers", "Active customers per year: new vs returning (2015 is the first year in the data)");
  const yrs = K.new_vs_returning.map((r) => String(r.order_year));
  s.addChart(pres.charts.BAR, [
    { name: "Returning", labels: yrs, values: K.new_vs_returning.map((r) => r.returning) },
    { name: "New", labels: yrs, values: K.new_vs_returning.map((r) => r.new) },
  ], { x: 0.4, y: 1.4, w: 5.4, h: 3.9, barDir: "col", barGrouping: "stacked", chartColors: [C.blue, C.amber], showLegend: true, legendPos: "b", legendFontSize: 10,
       showValue: true, dataLabelPosition: "ctr", dataLabelColor: "FFFFFF", dataLabelFontSize: 9, ...axis });
  const r = K.retention;
  bullets(s, [
    "New customers: 136 (2016), 51 (2017), 11 (2018).",
    `Retention rose from ${r["2015"].toFixed(0)}% to ${r["2017"].toFixed(0)}%; ${K.pct_repeat_customers.toFixed(0)}% of customers order at least twice.`,
    `The top 20% of customers generate ${K.top20_share.toFixed(0)}% of sales.`,
    "RFM: Champions are 24% of customers and 40% of sales; At Risk plus Lost are 25% of customers and 8% of sales.",
  ], 6.05, 1.5, 3.5, 3.8);
}

// 8. Recommendations
{
  const s = base("Recommendations", "Ordered by expected profit impact");
  const recs = [
    ["Cap discounts at 20%", "Require approval above the cap. Deep discounts show no volume benefit."],
    ["Fix Tables, Bookcases, Supplies", "Re-price or restructure; over half of Tables lines carry deep discounts."],
    ["Review Central region pricing", "Margin gap versus East and West is a pricing-discipline issue."],
    ["Grow winners, bundle high-margin lines", "Copiers, Accessories, Appliances; add Paper, Labels, Envelopes to orders."],
    ["Restart customer acquisition", "Win-back for At Risk, loyalty tier for Champions."],
  ];
  recs.forEach(([h, d], i) => {
    const y = 1.45 + i * 0.78;
    s.addShape(pres.shapes.OVAL, { x: 0.5, y: y + 0.05, w: 0.45, h: 0.45, fill: { color: C.blue }, line: { color: C.blue } });
    s.addText(String(i + 1), { x: 0.5, y: y + 0.05, w: 0.45, h: 0.45, align: "center", valign: "middle", fontFace: F, fontSize: 14, bold: true, color: "FFFFFF", margin: 0, isTextBox: true });
    s.addText([{ text: h, options: { bold: true, breakLine: true, fontSize: 15 } }, { text: d, options: { fontSize: 12, color: C.mut } }],
      { x: 1.15, y, w: 8.3, h: 0.6, fontFace: F, color: C.ink, valign: "top", margin: 0, isTextBox: true });
  });
}

pres.writeFile({ fileName: path.join(__dirname, "Sales_Performance_Report.pptx") }).then((f) => console.log("saved", f));
