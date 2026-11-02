"""Generate synthetic source extracts for a fictional Istanbul pharmaceutical wholesaler.

The data imitates what an ERP export really looks like: inconsistent district
names, mixed-case codes, a few duplicate order lines, cancelled orders, returns
for expired stock and late deliveries. Two "days" can be generated so that the
dbt snapshot captures real changes to pharmacy master data (SCD Type 2).

Usage:
    python scripts/generate_data.py            # day 1 extract
    python scripts/generate_data.py --day 2    # day 2: pharmacies change segment, credit limit or district
"""
from __future__ import annotations

import argparse
import csv
import random
from datetime import date, datetime, timedelta
from pathlib import Path

RAW = Path(__file__).resolve().parents[1] / "data" / "raw"
SEED = 2026

DISTRICTS = {
    "Kadıköy": ["Kadıköy", "KADIKOY", "kadikoy", "Kadikoy "],
    "Beşiktaş": ["Beşiktaş", "BESIKTAS", "Besiktas"],
    "Üsküdar": ["Üsküdar", "USKUDAR", "Uskudar"],
    "Şişli": ["Şişli", "SISLI", "Sisli"],
    "Bakırköy": ["Bakırköy", "BAKIRKOY"],
    "Ataşehir": ["Ataşehir", "ATASEHIR"],
    "Fatih": ["Fatih", "FATIH"],
    "Pendik": ["Pendik", "PENDIK"],
}
CATEGORIES = [  # ATC level-1 groups
    ("A", "Alimentary tract & metabolism"), ("C", "Cardiovascular system"), ("J", "Anti-infectives"),
    ("N", "Nervous system"), ("R", "Respiratory system"), ("L", "Antineoplastic & immunomodulating"),
]
WAREHOUSES = ["IST-ANADOLU", "IST-AVRUPA"]


def write(name: str, header: list[str], rows: list[list]) -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    with open(RAW / f"{name}.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)
    print(f"  {name}.csv  {len(rows):>6} rows")


def main(day: int) -> None:
    rnd = random.Random(SEED)
    print(f"Generating day {day} extract → {RAW}")

    # ---------------- pharmacies (customers)
    pharmacies = []
    for i in range(1, 181):
        district = rnd.choice(list(DISTRICTS))
        spelled = rnd.choice(DISTRICTS[district]) if rnd.random() < 0.3 else district
        segment = rnd.choices(["Chain", "Independent", "Hospital"], [2, 7, 1])[0]
        credit = rnd.choice([50_000, 100_000, 150_000, 250_000])
        pharmacies.append([f"ph-{i:04d}" if rnd.random() < 0.1 else f"PH-{i:04d}",
                           f"Eczane {rnd.choice(['Şifa', 'Hayat', 'Deniz', 'Yıldız', 'Merkez', 'Güneş', 'Lale', 'Nur'])} {i}",
                           spelled, segment, credit, (date(2024, 1, 1) + timedelta(days=rnd.randint(0, 600))).isoformat()])
    if day >= 2:  # master data changes between extracts → SCD2
        crnd = random.Random(SEED + day)
        for p in crnd.sample(pharmacies, 18):
            change = crnd.choice(["segment", "credit", "district"])
            if change == "segment":
                p[3] = "Chain" if p[3] != "Chain" else "Independent"
            elif change == "credit":
                p[4] = p[4] + 50_000
            else:
                p[2] = crnd.choice(list(DISTRICTS))
    write("pharmacies", ["pharmacy_code", "pharmacy_name", "district", "segment", "credit_limit_try", "opened_on"], pharmacies)

    # ---------------- products
    products = []
    for i in range(1, 121):
        atc, _ = rnd.choice(CATEGORIES)
        cold = atc == "L" or rnd.random() < 0.08
        price = round(rnd.uniform(35, 420) * (6 if atc == "L" else 1), 2)
        products.append([f"SKU{i:05d}", f"{rnd.choice(['Cardio', 'Neuro', 'Resp', 'Gastro', 'Immuno', 'Anti'])}"
                         f"{rnd.choice(['vex', 'lin', 'mab', 'pril', 'zol', 'cin'])} {rnd.choice([5, 10, 20, 50, 100])}mg",
                         atc, "Y" if cold else "N", price])
    write("products", ["sku", "product_name", "atc_group", "cold_chain", "list_price_try"], products)

    # ---------------- orders, lines, deliveries, returns
    orders, lines, deliveries, returns = [], [], [], []
    start = date(2026, 1, 1)
    line_id = 0
    for o in range(1, 3201):
        ph = rnd.choice(pharmacies)
        od = datetime.combine(start + timedelta(days=rnd.randint(0, 299)), datetime.min.time()) + timedelta(hours=rnd.randint(8, 18), minutes=rnd.randint(0, 59))
        status = rnd.choices(["DELIVERED", "CANCELLED", "IN_TRANSIT"], [92, 5, 3])[0]
        wh = rnd.choice(WAREHOUSES)
        orders.append([f"SO-{o:06d}", ph[0].upper(), od.strftime("%Y-%m-%d %H:%M:%S"), wh, status])
        n_lines = rnd.randint(1, 6)
        for sku in rnd.sample(products, n_lines):
            line_id += 1
            qty = rnd.choice([1, 2, 5, 10, 20, 50]) if sku[2] != "L" else rnd.choice([1, 2, 4])
            disc = rnd.choice([0, 0, 0, 2.5, 5, 7.5, 10])
            lines.append([line_id, f"SO-{o:06d}", sku[0], qty, sku[4], disc])
            if rnd.random() < 0.004:  # duplicated line in the extract
                lines.append([line_id, f"SO-{o:06d}", sku[0], qty, sku[4], disc])
            if status == "DELIVERED" and rnd.random() < 0.035:
                reason = rnd.choices(["EXPIRED", "DAMAGED", "WRONG_ITEM"], [5, 3, 2])[0]
                returns.append([f"RT-{len(returns) + 1:05d}", line_id, (od + timedelta(days=rnd.randint(3, 40))).date().isoformat(),
                                max(1, qty // rnd.choice([1, 2, 5])), reason])
        if status != "CANCELLED":
            dispatched = od + timedelta(hours=rnd.uniform(1, 10))
            promised = (od + timedelta(days=1)).replace(hour=18, minute=0, second=0)
            delivered = None
            if status == "DELIVERED":
                late = rnd.random() < (0.16 if wh == "IST-AVRUPA" else 0.09)
                delivered = promised - timedelta(hours=rnd.uniform(1, 20)) if not late else promised + timedelta(hours=rnd.uniform(2, 40))
                if delivered < dispatched:
                    delivered = dispatched + timedelta(hours=rnd.uniform(1, 4))
            deliveries.append([f"SO-{o:06d}", rnd.choice(["Courier-A", "Courier-B", "Own fleet"]),
                               dispatched.strftime("%Y-%m-%d %H:%M:%S"), promised.strftime("%Y-%m-%d %H:%M:%S"),
                               delivered.strftime("%Y-%m-%d %H:%M:%S") if delivered else ""])

    write("orders", ["order_id", "pharmacy_code", "ordered_at", "warehouse", "status"], orders)
    write("order_lines", ["line_id", "order_id", "sku", "quantity", "unit_price_try", "discount_pct"], lines)
    write("deliveries", ["order_id", "carrier", "dispatched_at", "promised_at", "delivered_at"], deliveries)
    write("returns", ["return_id", "line_id", "returned_on", "quantity", "reason"], returns)
    (RAW / "_extract_day.txt").write_text(str(day))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--day", type=int, default=1)
    main(ap.parse_args().day)
