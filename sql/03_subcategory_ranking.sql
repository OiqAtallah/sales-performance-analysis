-- Q3. Sub-category ranking over the full period (sales share, margin, profit rank)
WITH sc AS (
    SELECT category, sub_category,
           SUM(sales) AS sales, SUM(profit) AS profit
    FROM orders
    GROUP BY category, sub_category
)
SELECT category, sub_category,
       ROUND(sales, 2)  AS sales,
       ROUND(profit, 2) AS profit,
       ROUND(100.0 * profit / sales, 2)                    AS margin_pct,
       ROUND(100.0 * sales / SUM(sales) OVER (), 2)        AS sales_share_pct,
       RANK() OVER (ORDER BY profit DESC)                  AS profit_rank
FROM sc
ORDER BY profit_rank;
