"""generate_dataset.py - builds a sample stock.csv (about 600 grocery/retail items).
Use this only if you have not downloaded a real dataset. Run: python generate_dataset.py
"""
import csv
import random

random.seed(42)
CATALOG = {
    "Groceries": ([("Atta", 55), ("Basmati Rice", 90), ("Toor Dal", 140), ("Sugar", 45),
                   ("Salt", 20), ("Sunflower Oil", 150), ("Poha", 50), ("Besan", 80),
                   ("Moong Dal", 130), ("Rava", 45)],
                  ["Aashirvaad", "Fortune", "Tata", "Pillsbury", "24 Mantra", "India Gate"],
                  [("500g", 0.5), ("1kg", 1), ("5kg", 4.5)]),
    "Dairy": ([("Milk", 30), ("Curd", 35), ("Paneer", 90), ("Butter", 55), ("Cheese Slices", 120)],
              ["Amul", "Mother Dairy", "Nandini", "Gokul"],
              [("200g", 0.5), ("500g", 1), ("1L", 1.6)]),
    "Snacks": ([("Potato Chips", 20), ("Namkeen", 30), ("Biscuits", 25), ("Cookies", 40),
                ("Popcorn", 35), ("Instant Noodles", 14)],
               ["Lays", "Haldiram's", "Parle", "Britannia", "Maggi", "Bingo"],
               [("50g", 1), ("100g", 1.8), ("200g", 3)]),
    "Beverages": ([("Tea", 100), ("Coffee", 180), ("Cola", 40), ("Fruit Juice", 90), ("Energy Drink", 110)],
                  ["Tata Tea", "Nescafe", "Bru", "Real", "Pepsi", "Coca-Cola"],
                  [("250ml", 0.6), ("500ml", 1), ("1L", 1.7)]),
    "Personal Care": ([("Shampoo", 120), ("Soap", 35), ("Toothpaste", 70), ("Face Wash", 130), ("Deodorant", 180)],
                      ["Dove", "Dettol", "Colgate", "Himalaya", "Nivea", "Pepsodent"],
                      [("100ml", 1), ("200ml", 1.8), ("400ml", 3.2)]),
    "Household": ([("Detergent Powder", 110), ("Dishwash Liquid", 95), ("Floor Cleaner", 120), ("Toilet Cleaner", 100)],
                  ["Surf Excel", "Vim", "Lizol", "Harpic", "Ariel", "Domex"],
                  [("500ml", 1), ("1L", 1.8), ("2L", 3.3)]),
    "Stationery": ([("Notebook", 50), ("Ball Pen Pack", 40), ("Pencil Box", 60), ("Marker Set", 90), ("Geometry Box", 110)],
                   ["Classmate", "Camlin", "Cello", "Reynolds", "Apsara", "Faber-Castell"],
                   [("Small", 1), ("Medium", 1.5), ("Large", 2.2)]),
}

rows, seen = [], set()
for category, (products, brands, sizes) in CATALOG.items():
    for product, base in products:
        for brand in brands:
            for size, mult in sizes:
                name = f"{brand} {product} {size}"
                if name in seen:
                    continue
                seen.add(name)
                price = round(base * mult * random.uniform(0.9, 1.2))
                qty = random.choice([0, random.randint(1, 10), random.randint(11, 200),
                                     random.randint(50, 300), random.randint(20, 150)])
                rows.append([name, category, price, qty])

random.shuffle(rows)
with open("stock.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["id", "name", "category", "price", "qty"])
    for i, (name, category, price, qty) in enumerate(rows, start=1001):
        writer.writerow([i, name, category, price, qty])
print(f"Created stock.csv with {len(rows)} items")
