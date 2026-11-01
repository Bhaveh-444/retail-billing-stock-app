"""app.py - Streamlit front end for the Retail Billing & Stock System.
Run with:  streamlit run app.py
Streamlit re-runs this whole script on every click, so data that must survive
(stock, bills, cart) lives in st.session_state.
"""
import pandas as pd
import streamlit as st  # type: ignore[import-not-found]

import billing  # type: ignore[import-not-found]
import inventory as inv
import storage

st.set_page_config(page_title="Retail Billing & Stock", page_icon="🛒", layout="wide")

# ---------- load data once per session ----------
if "stock" not in st.session_state:
    st.session_state.stock = storage.load_stock()
    st.session_state.bills = storage.load_bills()
    st.session_state.cart = []
    st.session_state.last_bill = None

stock = st.session_state.stock
bills = st.session_state.bills
cart = st.session_state.cart

st.sidebar.title("🛒 Retail Billing")
page = st.sidebar.radio("Menu", ["Dashboard", "View Stock", "Add Item",
                                 "Update / Delete", "New Bill", "Sales Report"])
low_limit = st.sidebar.slider("Low-stock limit", 1, 50, 10)
st.sidebar.caption(f"{len(stock)} items in stock")


def show(result):
    ok, msg = result
    (st.success if ok else st.error)(msg)
    return ok


# ---------- pages ----------
if page == "Dashboard":
    st.title("Warehouse Dashboard")
    low = inv.low_stock(stock, low_limit)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Items", len(stock))
    c2.metric("Units in stock", sum(it["qty"] for it in stock))
    c3.metric("Stock value (Rs.)", f"{inv.total_value(stock):,.0f}")
    c4.metric("Low-stock items", len(low))
    if stock:
        df = pd.DataFrame(stock)
        df["value"] = df["price"] * df["qty"]
        st.subheader("Stock value by category")
        st.bar_chart(df.groupby("category")["value"].sum())
    st.subheader(f"Low stock (qty <= {low_limit})")
    if low:
        st.dataframe(pd.DataFrame(low), width="stretch", hide_index=True)
    else:
        st.info("All items are sufficiently stocked.")

elif page == "View Stock":
    st.title("Stock")
    col1, col2 = st.columns([2, 1])
    keyword = col1.text_input("Search by name")
    chosen = col2.multiselect("Category", inv.categories(stock))
    rows = inv.search_item(stock, keyword) if keyword else stock
    if chosen:
        rows = [it for it in rows if it["category"] in chosen]
    st.caption(f"{len(rows)} items")
    st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)

elif page == "Add Item":
    st.title("Add Item")
    with st.form("add_form", clear_on_submit=True):
        item_id = st.number_input("ID", min_value=1, value=inv.next_id(stock), step=1)
        name = st.text_input("Name")
        existing = st.selectbox("Category", inv.categories(stock) or ["General"])
        new_cat = st.text_input("...or type a new category")
        price = st.number_input("Price (Rs.)", min_value=0.0, step=1.0)
        qty = st.number_input("Quantity", min_value=0, step=1)
        if st.form_submit_button("Add item"):
            if show(inv.add_item(stock, int(item_id), name, new_cat or existing,
                                 price, int(qty))):
                storage.save_stock(stock)

elif page == "Update / Delete":
    st.title("Update / Delete Item")
    if not stock:
        st.info("No items in stock.")
    else:
        item = st.selectbox("Select item", stock,
                            format_func=lambda it: f"{it['id']} - {it['name']}")
        price = st.number_input("Price (Rs.)", min_value=0.0, value=item["price"],
                                step=1.0, key=f"p{item['id']}")
        qty = st.number_input("Quantity", min_value=0, value=item["qty"],
                              step=1, key=f"q{item['id']}")
        c1, c2 = st.columns(2)
        if c1.button("Update"):
            if show(inv.update_item(stock, item["id"], price, int(qty))):
                storage.save_stock(stock)
        if c2.button("Delete"):
            if show(inv.delete_item(stock, item["id"])):
                storage.save_stock(stock)

elif page == "New Bill":
    st.title("New Bill")
    customer = st.text_input("Customer name")
    in_stock = [it for it in stock if it["qty"] > 0]
    if in_stock:
        item = st.selectbox("Item", in_stock, format_func=lambda it:
                            f"{it['id']} - {it['name']}  (Rs.{it['price']:.2f}, {it['qty']} left)")
        available = item["qty"] - billing.qty_in_cart(cart, item["id"])
        if available > 0:
            qty = st.number_input("Quantity", min_value=1, max_value=available, step=1)
            if st.button("Add to cart"):
                show(billing.add_to_cart(cart, item, int(qty)))
        else:
            st.warning("Everything in stock for this item is already in the cart.")

    st.subheader("Cart")
    if cart:
        st.dataframe(pd.DataFrame(cart), width="stretch", hide_index=True)
        t = billing.calculate_totals(cart)
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Subtotal", f"{t['subtotal']:.2f}")
        m2.metric(f"Discount ({t['discount_pct']}%)", f"-{t['discount']:.2f}")
        m3.metric("GST (18%)", f"{t['gst']:.2f}")
        m4.metric("Grand total", f"{t['total']:.2f}")
        b1, b2 = st.columns(2)
        if b1.button("Generate bill", type="primary"):
            try:
                bill = billing.checkout(stock, cart, customer, bills)
                text = billing.format_bill(bill)
                storage.save_stock(stock)
                storage.save_bills(bills)
                storage.append_bill_text(text)
                cart.clear()
                st.session_state.last_bill = text
                st.rerun()
            except ValueError as err:
                st.error(str(err))
        if b2.button("Clear cart"):
            cart.clear()
            st.rerun()
    else:
        st.info("Cart is empty.")

    if st.session_state.last_bill:
        st.success("Bill generated and stock updated.")
        st.code(st.session_state.last_bill)
        st.download_button("Download bill", st.session_state.last_bill,
                           file_name="bill.txt")

elif page == "Sales Report":
    st.title("Sales Report")
    if not bills:
        st.info("No sales yet. Generate a bill first.")
    else:
        c1, c2 = st.columns(2)
        c1.metric("Bills generated", len(bills))
        c2.metric("Total revenue (Rs.)", f"{billing.total_revenue(bills):,.2f}")
        units = billing.units_sold(bills)
        top = dict(sorted(units.items(), key=lambda x: x[1], reverse=True)[:10])
        st.subheader("Top items by units sold")
        st.bar_chart(pd.Series(top))
        st.subheader("Past bills")
        pick = st.selectbox("Open bill", bills, format_func=lambda b:
                            f"#{b['bill_no']} - {b['customer']} - Rs.{b['totals']['total']:.2f}")
        st.code(billing.format_bill(pick))