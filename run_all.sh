#!/usr/bin/env bash
# Reproduce the whole pipeline: clean -> SQL -> analysis -> RFM -> dashboard
set -euo pipefail
cd "$(dirname "$0")/src"
python 01_clean.py
python 02_run_sql.py
python 03_analysis.py
python 04_rfm.py
python 05_build_dashboard.py
echo "Done. Open dashboard/index.html"
