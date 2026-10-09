-- Q7. Year-over-year retention: share of customers active in year Y who ordered again in Y+1
WITH active AS (
    SELECT DISTINCT customer_id, order_year AS yr FROM orders
)
SELECT a.yr,
       COUNT(*)                                             AS active_customers,
       COUNT(b.customer_id)                                 AS retained_next_year,
       ROUND(100.0 * COUNT(b.customer_id) / COUNT(*), 2)    AS retention_pct
FROM active a
LEFT JOIN active b ON b.customer_id = a.customer_id AND b.yr = a.yr + 1
WHERE a.yr < (SELECT MAX(order_year) FROM orders)
GROUP BY a.yr
ORDER BY a.yr;
