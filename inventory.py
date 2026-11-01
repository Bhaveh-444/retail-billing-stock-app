"""inventory.py - stock operations.
stock = list of dictionaries: {"id", "name", "category", "price", "qty"}
Every function returns (success, message) so the UI decides how to show it.
"""


def find_by_id(stock, item_id):
    for item in stock:
        if item["id"] == item_id:
            return item
    return None


def next_id(stock):
    return max((it["id"] for it in stock), default=1000) + 1


def categories(stock):
    return sorted({it["category"] for it in stock})


def add_item(stock, item_id, name, category, price, qty):
    name, category = name.strip(), category.strip()
    if not name or not category:
        return False, "Name and category cannot be empty."
    if price < 0 or qty < 0:
        return False, "Price and quantity cannot be negative."
    if find_by_id(stock, item_id):
        return False, f"ID {item_id} already exists."
    stock.append({"id": item_id, "name": name, "category": category,
                  "price": float(price), "qty": int(qty)})
    return True, f"'{name}' added."


def update_item(stock, item_id, price, qty):
    item = find_by_id(stock, item_id)
    if not item:
        return False, "Item not found."
    if price < 0 or qty < 0:
        return False, "Price and quantity cannot be negative."
    item["price"], item["qty"] = float(price), int(qty)
    return True, f"'{item['name']}' updated."


def delete_item(stock, item_id):
    item = find_by_id(stock, item_id)
    if not item:
        return False, "Item not found."
    stock.remove(item)
    return True, f"'{item['name']}' deleted."


def search_item(stock, keyword):
    keyword = keyword.lower()
    return [it for it in stock if keyword in it["name"].lower()]


def low_stock(stock, limit):
    return [it for it in stock if it["qty"] <= limit]


def total_value(stock):
    return sum(it["price"] * it["qty"] for it in stock)