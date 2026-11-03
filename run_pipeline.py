"""End-to-end demo run.

1. Generate the day-1 ERP extract and build everything (snapshot captures version 1 of each pharmacy).
2. Generate the day-2 extract, where 18 pharmacies change district, segment or credit limit.
3. Build again: the snapshot closes the old versions and opens new ones (SCD Type 2),
   and every test runs against the new data.
4. Generate the static dbt docs site into docs/.
5. Export the marts to powerbi/data/ for the Power BI report.
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
os.environ.setdefault("DBT_PROFILES_DIR", str(ROOT))

# Call dbt through this Python interpreter, so it works even when the `dbt`
# command is not on PATH (common in Codespaces and fresh virtual environments).
DBT = (sys.executable, "-m", "dbt.cli.main")


def run(*cmd: str) -> None:
    print("\n$", " ".join(cmd), flush=True)
    subprocess.run(cmd, cwd=ROOT, check=True)


if __name__ == "__main__":
    db = ROOT / "pharma.duckdb"
    if db.exists():
        db.unlink()
    run(sys.executable, "scripts/generate_data.py", "--day", "1")
    run(*DBT, "build")
    run(sys.executable, "scripts/generate_data.py", "--day", "2")
    run(*DBT, "build")
    run(*DBT, "docs", "generate", "--static")
    docs = ROOT / "docs"
    docs.mkdir(exist_ok=True)
    shutil.copy(ROOT / "target" / "static_index.html", docs / "index.html")
    run(sys.executable, "scripts/export_powerbi.py")
    print("\nDone. Warehouse: pharma.duckdb · Docs: docs/index.html · Power BI data: powerbi/data/")
