-- Q1. Overall performance per year: sales, profit, margin, YoY growth
-- Dialect: SQLite (window functions need SQLite >= 3.25)
WITH yearly AS (
    SELECT order_year                          AS yr,
           ROUND(SUM(sales), 2)                AS sales,
           ROUND(SUM(profit), 2)               AS profit,
           COUNT(DISTINCT order_id)            AS orders,
           COUNT(DISTINCT customer_id)         AS customers
    FROM orders
    GROUP BY order_year
)
SELECT yr, sales, profit, orders, customers,
       ROUND(100.0 * profit / sales, 2)                                           AS margin_pct,
       ROUND(sales / orders, 2)                                                   AS avg_order_value,
       ROUND(100.0 * (sales  - LAG(sales)  OVER (ORDER BY yr)) / LAG(sales)  OVER (ORDER BY yr), 2) AS sales_yoy_pct,
       ROUND(100.0 * (profit - LAG(profit) OVER (ORDER BY yr)) / LAG(profit) OVER (ORDER BY yr), 2) AS profit_yoy_pct
FROM yearly
ORDER BY yr;
