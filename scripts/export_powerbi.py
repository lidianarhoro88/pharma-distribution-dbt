"""Export the dbt marts to CSV files for the Power BI report in powerbi/.

Run after `dbt build`:  python scripts/export_powerbi.py
"""
from pathlib import Path

import duckdb

OUT = Path(__file__).resolve().parents[1] / "powerbi" / "data"
DB = Path(__file__).resolve().parents[1] / "pharma.duckdb"

QUERIES = {
    # Current version of each pharmacy, keyed by its business code.
    # (The full SCD2 history stays in marts.dim_pharmacy for point-in-time work.)
    "Pharmacy": """
        select pharmacy_code, pharmacy_name, district, segment, credit_limit_try, opened_on
        from marts.dim_pharmacy where is_current order by pharmacy_code""",
    "Product": "select * from marts.dim_product order by sku",
    "Date": "select * from marts.dim_date order by date_day",
    "Warehouse": """
        select distinct warehouse,
               case warehouse when 'IST-AVRUPA' then 'European side' else 'Anatolian side' end as side
        from marts.fct_deliveries order by 1""",
    "OrderLines": """
        select line_id, order_id, order_date, pharmacy_code, sku, warehouse, order_status, is_cancelled,
               quantity, unit_price_try, discount_pct, gross_amount_try,
               round(net_amount_try, 2) as net_amount_try,
               returned_quantity::int as returned_quantity, expired_quantity::int as expired_quantity,
               round(returned_amount_try, 2) as returned_amount_try,
               round(net_after_returns_try, 2) as net_after_returns_try
        from marts.fct_order_lines order by line_id""",
    "Deliveries": """
        select order_id, order_date, pharmacy_code, warehouse, carrier, has_cold_chain,
               dispatched_at, promised_at, delivered_at, is_delivered,
               round(lead_time_hours, 2) as lead_time_hours, is_on_time, is_in_full, is_otif
        from marts.fct_deliveries order by order_id""",
}


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(DB), read_only=True)
    for name, sql in QUERIES.items():
        path = OUT / f"{name}.csv"
        con.execute(f"copy ({sql}) to '{path.as_posix()}' (header, delimiter ',')")
        rows = con.execute(f"select count(*) from ({sql})").fetchall()[0][0]
        print(f"{path.relative_to(OUT.parents[1])}: {rows:,} rows")


if __name__ == "__main__":
    main()
