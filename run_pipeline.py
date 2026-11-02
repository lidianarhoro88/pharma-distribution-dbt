"""End-to-end demo run.

1. Generate the day-1 ERP extract and build everything (snapshot captures version 1 of each pharmacy).
2. Generate the day-2 extract, where 18 pharmacies change district, segment or credit limit.
3. Build again: the snapshot closes the old versions and opens new ones (SCD Type 2),
   and every test runs against the new data.
4. Generate the static dbt docs site into docs/.
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
os.environ.setdefault("DBT_PROFILES_DIR", str(ROOT))


def run(*cmd: str) -> None:
    print("\n$", " ".join(cmd), flush=True)
    subprocess.run(cmd, cwd=ROOT, check=True)


if __name__ == "__main__":
    db = ROOT / "pharma.duckdb"
    if db.exists():
        db.unlink()
    run(sys.executable, "scripts/generate_data.py", "--day", "1")
    run("dbt", "build")
    run(sys.executable, "scripts/generate_data.py", "--day", "2")
    run("dbt", "build")
    run("dbt", "docs", "generate", "--static")
    docs = ROOT / "docs"
    docs.mkdir(exist_ok=True)
    shutil.copy(ROOT / "target" / "static_index.html", docs / "index.html")
    print("\nDone. Warehouse: pharma.duckdb · Docs: docs/index.html")
