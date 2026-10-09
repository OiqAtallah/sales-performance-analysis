-- Q9. Region x customer segment view
SELECT region, segment,
       ROUND(SUM(sales), 2)  AS sales,
       ROUND(SUM(profit), 2) AS profit,
       ROUND(100.0 * SUM(profit) / SUM(sales), 2) AS margin_pct,
       COUNT(DISTINCT customer_id) AS customers
FROM orders
GROUP BY region, segment
ORDER BY region, segment;
