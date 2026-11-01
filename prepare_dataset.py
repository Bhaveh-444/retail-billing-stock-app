"""prepare_dataset.py - converts a downloaded Kaggle CSV or Excel file (e.g. Zepto) into stock.csv.
Usage:  python prepare_dataset.py zepto_v1.xlsx [--rows 800] [--price-divisor 100]
It guesses column names; if it guesses wrong, edit CANDIDATES below.
(Some datasets store prices in paise - then use --price-divisor 100.)
"""
import argparse
import csv
import io

CANDIDATES = {
    "name": ["name", "product_name", "productname", "item", "title"],
    "category": ["category", "product_category", "categoryname"],
    "price": ["discountedsellingprice", "selling_price", "price", "unit_price", "mrp"],
    "qty": ["availablequantity", "quantity", "qty", "stock", "inventory"],
}


def pick(header, options):
    lookup = {h.strip().lower().replace(" ", "_"): h for h in header}
    for opt in options:
        if opt in lookup:
            return lookup[opt]
    return None


parser = argparse.ArgumentParser()
parser.add_argument("source")
parser.add_argument("--rows", type=int, default=800)
parser.add_argument("--price-divisor", type=float, default=1)
args = parser.parse_args()

csv.field_size_limit(2 ** 30)   # avoid "field larger than field limit" errors

# 1. load the file as a list of rows (dictionaries) + the column names
if args.source.lower().endswith((".xlsx", ".xls")):
    import pandas as pd                      # needs: pip install pandas openpyxl
    frame = pd.read_excel(args.source)
    fieldnames = [str(c) for c in frame.columns]
    records = frame.to_dict("records")
    print("Excel file loaded.", end=" ")
else:
    with open(args.source, "rb") as f:
        raw = f.read()
    if raw.lstrip()[:1] == b"{":
        raise SystemExit("This file is JSON (probably a Jupyter notebook), not the dataset. "
                         "Download the real data file (e.g. zepto_v1.xlsx) from the Kaggle dataset page.")
    if raw[:2] in (b"\xff\xfe", b"\xfe\xff"):
        text = raw.decode("utf-16")
    else:
        try:
            text = raw.decode("utf-8-sig")
        except UnicodeDecodeError:
            text = raw.decode("latin-1")
    try:
        delimiter = csv.Sniffer().sniff(text[:5000], delimiters=",;\t|").delimiter
    except csv.Error:
        delimiter = ","
    reader = csv.DictReader(io.StringIO(text, newline=""), delimiter=delimiter)
    fieldnames, records = reader.fieldnames, reader
print("Columns found:", fieldnames)
cols = {key: pick(fieldnames, opts) for key, opts in CANDIDATES.items()}
print("Column mapping:", cols)
missing = [k for k, v in cols.items() if v is None]
if missing and missing != ["qty"]:
    raise SystemExit(f"Could not find columns for: {missing}. Edit CANDIDATES.")

out, seen = [], set()
for row in records:
    try:
        name = str(row[cols["name"]]).strip()
        price = round(float(row[cols["price"]]) / args.price_divisor, 2)
        qty = int(float(row[cols["qty"]])) if cols["qty"] else 50
    except (ValueError, KeyError, AttributeError, TypeError):
        continue
    if not name or price <= 0 or name in seen:
        continue
    seen.add(name)
    out.append([name, str(row[cols["category"]] or "").strip() or "General", price, max(qty, 0)])
    if len(out) >= args.rows:
        break

with open("stock.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["id", "name", "category", "price", "qty"])
    for i, r in enumerate(out, start=1001):
        w.writerow([i] + r)
print(f"Created stock.csv with {len(out)} items")
