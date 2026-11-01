"""billing.py - cart, calculations, bill generation and sales report.
cart = list of dicts {"id","name","price","qty","amount"}
bill = dict {"bill_no","date","customer","items","totals"}
"""
from datetime import datetime
import inventory as inv

GST_RATE = 0.18
# Tuple of (minimum subtotal, discount %) - checked from highest to lowest
DISCOUNT_SLABS = ((5000, 10), (2000, 5), (0, 0))


def discount_percent(subtotal):
    for limit, percent in DISCOUNT_SLABS:
        if subtotal >= limit:
            return percent
    return 0


def qty_in_cart(cart, item_id):
    for line in cart:
        if line["id"] == item_id:
            return line["qty"]
    return 0


def add_to_cart(cart, item, qty):
    """Add qty of item to the cart after checking stock. Returns (ok, message)."""
    if qty <= 0:
        return False, "Quantity must be at least 1."
    available = item["qty"] - qty_in_cart(cart, item["id"])
    if qty > available:
        return False, f"Only {available} of '{item['name']}' available."
    for line in cart:
        if line["id"] == item["id"]:
            line["qty"] += qty
            line["amount"] = line["qty"] * line["price"]
            return True, f"Added {qty} more '{item['name']}'."
    cart.append({"id": item["id"], "name": item["name"], "price": item["price"],
                 "qty": qty, "amount": qty * item["price"]})
    return True, f"Added {qty} x '{item['name']}'."


def calculate_totals(cart):
    subtotal = sum(line["amount"] for line in cart)
    pct = discount_percent(subtotal)
    discount = subtotal * pct / 100
    gst = (subtotal - discount) * GST_RATE
    return {"subtotal": round(subtotal, 2), "discount_pct": pct,
            "discount": round(discount, 2), "gst": round(gst, 2),
            "total": round(subtotal - discount + gst, 2)}


def checkout(stock, cart, customer, bills):
    """Create the bill and reduce stock. Raises ValueError on bad input."""
    if not customer.strip():
        raise ValueError("Customer name is required.")
    if not cart:
        raise ValueError("Cart is empty.")
    for line in cart:                                   # final stock check
        item = inv.find_by_id(stock, line["id"])
        if item is None or item["qty"] < line["qty"]:
            raise ValueError(f"Not enough stock for '{line['name']}'.")
    for line in cart:                                   # reduce stock
        inv.find_by_id(stock, line["id"])["qty"] -= line["qty"]
    bill = {"bill_no": len(bills) + 1,
            "date": datetime.now().strftime("%d-%m-%Y %H:%M"),
            "customer": customer.strip(),
            "items": [dict(line) for line in cart],
            "totals": calculate_totals(cart)}
    bills.append(bill)
    return bill


def format_bill(bill):
    t = bill["totals"]
    lines = ["=" * 56,
             f"BILL NO: {bill['bill_no']}      DATE: {bill['date']}",
             f"CUSTOMER: {bill['customer']}",
             "-" * 56,
             f"{'Item':<26}{'Price':>9}{'Qty':>6}{'Amount':>13}",
             "-" * 56]
    for l in bill["items"]:
        lines.append(f"{l['name'][:25]:<26}{l['price']:>9.2f}{l['qty']:>6}{l['amount']:>13.2f}")
    lines += ["-" * 56,
              f"{'Subtotal':<39}{t['subtotal']:>17.2f}",
              f"{'Discount (' + str(t['discount_pct']) + '%)':<39}{-t['discount']:>17.2f}",
              f"{'GST (18%)':<39}{t['gst']:>17.2f}",
              f"{'GRAND TOTAL':<39}{t['total']:>17.2f}",
              "=" * 56]
    return "\n".join(lines)


def units_sold(bills):
    """Dictionary: item name -> total units sold."""
    units = {}
    for b in bills:
        for l in b["items"]:
            units[l["name"]] = units.get(l["name"], 0) + l["qty"]
    return units


def total_revenue(bills):
    return round(sum(b["totals"]["total"] for b in bills), 2)