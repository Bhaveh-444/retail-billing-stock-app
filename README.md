# Retail Billing & Stock Management System

A Streamlit app for retail stores and warehouse managers to track stock, bill customers and see sales, built in Python for the PPS mini project.

## Features
- **Dashboard:** item count, units in stock, stock value, low-stock alerts and stock value by category
- **View Stock:** search by name and filter by category
- **Add / Update / Delete items:** changes are saved to `stock.csv`
- **New Bill:** cart with stock checks (no overselling), 5% / 10% discount slabs and 18% GST, downloadable bill
- **Sales Report:** total revenue, top items by units sold and a viewer for past bills

## Python concepts used
- Lists and dictionaries: stock and cart are a list of dictionaries
- Tuples: `DISCOUNT_SLABS` and `FIELDS`
- Dictionary counting: `units_sold()` in `billing.py`
- File handling: `stock.csv` (CSV), `bills.json` (JSON), `bills.txt` (text) in `storage.py`
- Exception handling: `try/except` in `storage.py` and `checkout()`
- Modules and reusable functions: `inventory.py`, `billing.py`, `storage.py`

## Project structure
| File | Purpose |
|---|---|
| `app.py` | Streamlit user interface |
| `inventory.py` | add, update, delete, search and low-stock logic |
| `billing.py` | cart, totals, checkout and sales statistics |
| `storage.py` | reading and writing CSV / JSON / text files |
| `prepare_dataset.py` | converts the Zepto Kaggle dataset into `stock.csv` |
| `generate_dataset.py` | creates a sample `stock.csv` if you have no dataset |

## Dataset
Zepto inventory dataset from Kaggle (`zepto_v1.xlsx`), converted to `stock.csv` with columns `id, name, category, price, qty`.

## Run it
```
pip install -r requirements.txt
python prepare_dataset.py zepto_v1.xlsx --rows 800 --price-divisor 100
python -m streamlit run app.py
```
Skip the second command to use the included `stock.csv`, or run `python generate_dataset.py` for sample data.

## Requirements
- Python 3.10 or newer (developed and tested on Python 3.14)
- Packages: `streamlit`, `pandas`, `openpyxl` (installed from `requirements.txt`)

## Important
Run the app from inside the project folder, because it loads `stock.csv` from the current directory:

    cd retail-billing-stock-app
    python -m streamlit run app.py
    ## Live demo
https://retail-billing-stock-app.streamlit.app
