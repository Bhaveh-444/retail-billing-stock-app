"""storage.py - file handling: stock in CSV, bills in JSON + printable TXT."""
import csv
import json

STOCK_FILE = "stock.csv"
BILLS_FILE = "bills.json"
BILL_TEXT_FILE = "bills.txt"
FIELDS = ("id", "name", "category", "price", "qty")   # tuple of column names


def load_stock():
    """Read stock.csv into a list of dictionaries. Bad rows are skipped."""
    stock = []
    try:
        with open(STOCK_FILE, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                try:
                    stock.append({"id": int(row["id"]), "name": row["name"].strip(),
                                  "category": row["category"].strip(),
                                  "price": float(row["price"]), "qty": int(row["qty"])})
                except (ValueError, KeyError, AttributeError):
                    continue            # skip malformed row
    except FileNotFoundError:
        print(f"{STOCK_FILE} not found. Starting with empty stock.")
    return stock


def save_stock(stock):
    try:
        with open(STOCK_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDS)
            writer.writeheader()
            writer.writerows(stock)
    except OSError as err:
        print(f"Could not save stock: {err}")


def load_bills():
    try:
        with open(BILLS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_bills(bills):
    try:
        with open(BILLS_FILE, "w", encoding="utf-8") as f:
            json.dump(bills, f, indent=4)
    except OSError as err:
        print(f"Could not save bills: {err}")


def append_bill_text(text):
    try:
        with open(BILL_TEXT_FILE, "a", encoding="utf-8") as f:
            f.write(text + "\n\n")
    except OSError as err:
        print(f"Could not write bill text: {err}")