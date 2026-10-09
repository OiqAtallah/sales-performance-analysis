"""Step 2 - Load the clean data into SQLite and run every query in /sql.

Output: data/processed/superstore.db (git-ignored), reports/tables/<query>.csv
"""
import sqlite3
import pandas as pd
from config import CLEAN, DB, SQL_DIR, TAB

TAB.mkdir(parents=True, exist_ok=True)
df = pd.read_csv(CLEAN)

with sqlite3.connect(DB) as con:
    df.to_sql("orders", con, if_exists="replace", index=False)
    for path in sorted(SQL_DIR.glob("*.sql")):
        result = pd.read_sql_query(path.read_text(), con)
        result.to_csv(TAB / f"{path.stem}.csv", index=False)
        print(f"{path.name:38s} -> {len(result):>3d} rows")
print("Tables saved to", TAB)
