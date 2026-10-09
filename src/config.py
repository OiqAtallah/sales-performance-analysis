"""Shared paths and constants for the Sales Performance project."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "superstore.csv"
CLEAN = ROOT / "data" / "processed" / "orders_clean.csv"
DB = ROOT / "data" / "processed" / "superstore.db"
SQL_DIR = ROOT / "sql"
FIG = ROOT / "reports" / "figures"
TAB = ROOT / "reports" / "tables"
REPORTS = ROOT / "reports"

# Discount bands used consistently in SQL and pandas (upper bound inclusive)
BAND_EDGES = [-0.01, 0.0, 0.10, 0.20, 0.30, 0.50, 1.0]
BAND_LABELS = ["0%", "1-10%", "11-20%", "21-30%", "31-50%", ">50%"]

# Palette
BLUE = "#2563eb"
TEAL = "#0d9488"
RED = "#dc2626"
AMBER = "#d97706"
GREY = "#94a3b8"
INK = "#0f172a"
