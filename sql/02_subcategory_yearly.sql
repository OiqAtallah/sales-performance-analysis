-- Q2. Sub-category performance per year, with YoY sales growth
WITH sc AS (
    SELECT sub_category, order_year AS yr,
           SUM(sales) AS sales, SUM(profit) AS profit
    FROM orders
    GROUP BY sub_category, order_year
)
SELECT sub_category, yr,
       ROUND(sales, 2)  AS sales,
       ROUND(profit, 2) AS profit,
       ROUND(100.0 * profit / sales, 2) AS margin_pct,
       ROUND(100.0 * (sales - LAG(sales) OVER (PARTITION BY sub_category ORDER BY yr))
             / LAG(sales) OVER (PARTITION BY sub_category ORDER BY yr), 2) AS sales_yoy_pct
FROM sc
ORDER BY sub_category, yr;
