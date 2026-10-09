-- Q4. Promotion effectiveness: does a deeper discount buy volume or only lose margin?
SELECT discount_band,
       COUNT(*)                                  AS order_lines,
       ROUND(SUM(sales), 2)                      AS sales,
       ROUND(SUM(profit), 2)                     AS profit,
       ROUND(100.0 * SUM(profit) / SUM(sales), 2) AS margin_pct,
       ROUND(AVG(quantity), 2)                   AS avg_quantity,
       ROUND(100.0 * AVG(is_loss), 2)            AS loss_line_pct,
       ROUND(100.0 * SUM(sales) / (SELECT SUM(sales) FROM orders), 2) AS sales_share_pct
FROM orders
GROUP BY discount_band
ORDER BY MIN(discount);
