-- Q6. New vs returning customers per year (new = first order in that year)
WITH first_order AS (
    SELECT customer_id, MIN(order_year) AS first_year
    FROM orders
    GROUP BY customer_id
)
SELECT o.order_year AS yr,
       COUNT(DISTINCT CASE WHEN f.first_year =  o.order_year THEN o.customer_id END) AS new_customers,
       COUNT(DISTINCT CASE WHEN f.first_year <  o.order_year THEN o.customer_id END) AS returning_customers,
       ROUND(SUM(CASE WHEN f.first_year =  o.order_year THEN o.sales ELSE 0 END), 2) AS new_customer_sales,
       ROUND(SUM(CASE WHEN f.first_year <  o.order_year THEN o.sales ELSE 0 END), 2) AS returning_customer_sales
FROM orders o
JOIN first_order f USING (customer_id)
GROUP BY o.order_year
ORDER BY yr;
