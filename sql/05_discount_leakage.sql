-- Q5. Profit leakage: profit made at <=20% discount vs. lost above 20%, per sub-category
SELECT sub_category,
       ROUND(SUM(CASE WHEN discount <= 0.20 THEN profit ELSE 0 END), 2) AS profit_up_to_20pct,
       ROUND(SUM(CASE WHEN discount >  0.20 THEN profit ELSE 0 END), 2) AS profit_above_20pct,
       ROUND(100.0 * SUM(CASE WHEN discount > 0.20 THEN sales ELSE 0 END) / SUM(sales), 2) AS sales_above_20pct_share
FROM orders
GROUP BY sub_category
ORDER BY profit_above_20pct;
