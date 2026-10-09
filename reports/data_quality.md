# Data Quality Log

- Raw file rows: 10,800
- Dropped 806 non-order rows (appended 'People'/'Returns' sheets)
- Missing postal_code: 11 rows (all Burlington, VT) -> filled with 05401
- Validation passed: unique row_id, sales > 0, 0 <= discount <= 1, ship >= order, no NaN
- Order lines sharing the same (order_id, product_id): 16 rows - kept (different quantities/discounts, valid lines)
- Clean rows: 9,994 | period 2015-01-03 to 2018-12-30
- Orders: 5,009 | Customers: 793 | Products: 1,862
