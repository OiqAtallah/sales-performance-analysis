-- Q8. Customer concentration: sales share of the top 20% of customers
WITH cust AS (
    SELECT customer_id, SUM(sales) AS sales
    FROM orders
    GROUP BY customer_id
),
ranked AS (
    SELECT customer_id, sales,
           ROW_NUMBER() OVER (ORDER BY sales DESC) AS rnk,
           COUNT(*) OVER ()                         AS n
    FROM cust
)
SELECT ROUND(100.0 * SUM(CASE WHEN rnk <= 0.2 * n THEN sales END) / SUM(sales), 2) AS top20pct_customers_sales_share,
       MAX(n)                                                                     AS total_customers
FROM ranked;
