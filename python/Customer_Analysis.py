
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# ==================================================
# 1. LOAD DATA
# ==================================================

DATA_DIR = Path.home() / "Downloads" / "Customer_Revenue_Analytics_CSV"
OUTPUT_DIR = Path("Outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

customers = pd.read_csv(DATA_DIR / "customers.csv")
products = pd.read_csv(DATA_DIR / "products.csv")
employees = pd.read_csv(DATA_DIR / "employees.csv")
orders = pd.read_csv(DATA_DIR / "orders.csv")

orders["order_date"] = pd.to_datetime(orders["order_date"])

print("CUSTOMERS:", customers.shape)
print("PRODUCTS:", products.shape)
print("EMPLOYEES:", employees.shape)
print("ORDERS:", orders.shape)


# ==================================================
# 2. DATA VALIDATION
# ==================================================

print("\n--- DATA QUALITY CHECKS ---")

for name, df in {
    "customers": customers,
    "products": products,
    "employees": employees,
    "orders": orders
}.items():
    print(f"\n{name}")
    print("Missing values:", df.isnull().sum().sum())
    print("Duplicate rows:", df.duplicated().sum())

print("\nDuplicate order IDs:", orders["order_id"].duplicated().sum())
print("Invalid quantities:", (orders["quantity"] <= 0).sum())


# ==================================================
# 3. MERGE ORDERS WITH PRODUCTS
# ==================================================

sales = orders.merge(
    products,
    on="product_id",
    how="inner",
    validate="many_to_one"
)

sales["total_revenue"] = (
    sales["quantity"] * sales["selling_price"]
)

sales["total_cost"] = sales["quantity"] * sales["cost"]

sales["total_profit"] = (
    sales["total_revenue"] - sales["total_cost"]
)

sales["month"] = sales["order_date"].dt.to_period("M")

print("\n--- SALES OVERVIEW ---")
print(sales.head())


# ==================================================
# 4. PRODUCT ANALYSIS
# ==================================================

product_summary = sales.groupby("product_name").agg(
    total_revenue=("total_revenue", "sum"),
    total_profit=("total_profit", "sum"),
    total_quantity=("quantity", "sum"),
    order_count=("order_id", "count")
)

product_summary["profit_margin_pct"] = (
    product_summary["total_profit"]
    / product_summary["total_revenue"] * 100
)

product_summary = product_summary.sort_values(
    "total_revenue", ascending=False
)

print("\n--- PRODUCT SUMMARY ---")
print(product_summary)

print("\nTop 3 products by revenue:")
print(product_summary.head(3))

print("\nTop 3 products by profit:")
print(product_summary.sort_values(
    "total_profit", ascending=False
).head(3))

print("\nProfit by category:")
print(
    sales.groupby("category")["total_profit"]
    .sum()
    .sort_values(ascending=False)
)


# ==================================================
# 5. CUSTOMER ANALYSIS
# ==================================================

customer_sales = sales.merge(
    customers,
    on="customer_id",
    how="inner",
    validate="many_to_one"
)

customer_summary = customer_sales.groupby("customer_name").agg(
    total_revenue=("total_revenue", "sum"),
    total_profit=("total_profit", "sum"),
    order_count=("order_id", "count"),
    total_quantity=("quantity", "sum")
)

customer_summary["AOV"] = (
    customer_summary["total_revenue"]
    / customer_summary["order_count"]
)

customer_summary = customer_summary.sort_values(
    "total_revenue", ascending=False
)

print("\n--- CUSTOMER SUMMARY ---")
print(customer_summary)

print("\nRepeat customers (at least 2 orders):")
print(
    customer_summary[customer_summary["order_count"] >= 2]
)

print("\nTop 3 customers by revenue:")
print(customer_summary.head(3))

print("\nRevenue by customer segment:")
print(
    customer_sales.groupby("segment")["total_revenue"]
    .sum()
    .sort_values(ascending=False)
)

print("\nRevenue by customer city:")
print(
    customer_sales.groupby("city")["total_revenue"]
    .sum()
    .sort_values(ascending=False)
)


# ==================================================
# 6. SALES CHANNEL ANALYSIS
# ==================================================

channel_summary = customer_sales.groupby("sales_channel").agg(
    total_revenue=("total_revenue", "sum"),
    total_profit=("total_profit", "sum"),
    order_count=("order_id", "count"),
    total_quantity=("quantity", "sum")
)

channel_summary["AOV"] = (
    channel_summary["total_revenue"]
    / channel_summary["order_count"]
)

channel_summary["revenue_share_pct"] = (
    channel_summary["total_revenue"]
    / channel_summary["total_revenue"].sum() * 100
)

channel_summary = channel_summary.sort_values(
    "total_revenue", ascending=False
)

print("\n--- CHANNEL SUMMARY ---")
print(channel_summary)


# ==================================================
# 7. EMPLOYEE ANALYSIS
# ==================================================

employee_sales = sales.merge(
    employees,
    on="employee_id",
    how="inner",
    validate="many_to_one"
)

employee_summary = employee_sales.groupby("employee_name").agg(
    total_revenue=("total_revenue", "sum"),
    total_profit=("total_profit", "sum"),
    order_count=("order_id", "count"),
    total_quantity=("quantity", "sum")
)

employee_summary = employee_summary.sort_values(
    "total_revenue", ascending=False
)

print("\n--- EMPLOYEE SUMMARY ---")
print(employee_summary)


# ==================================================
# 8. MONTHLY ANALYSIS
# ==================================================

monthly_summary = sales.groupby("month").agg(
    total_revenue=("total_revenue", "sum"),
    total_profit=("total_profit", "sum"),
    order_count=("order_id", "count"),
    total_quantity=("quantity", "sum")
).sort_index()

monthly_summary["profit_margin_pct"] = (
    monthly_summary["total_profit"]
    / monthly_summary["total_revenue"] * 100
)

monthly_summary["revenue_change"] = (
    monthly_summary["total_revenue"].diff()
)

monthly_summary["revenue_growth_pct"] = (
    monthly_summary["total_revenue"].pct_change(
        fill_method=None
    ) * 100
)

print("\n--- MONTHLY SUMMARY ---")
print(monthly_summary)

print("\nHighest-revenue month:")
print(monthly_summary["total_revenue"].idxmax())
print(monthly_summary["total_revenue"].max())

print("\nHighest-profit month:")
print(monthly_summary["total_profit"].idxmax())
print(monthly_summary["total_profit"].max())

print("\nHighest-margin month:")
print(monthly_summary["profit_margin_pct"].idxmax())
print(monthly_summary["profit_margin_pct"].max())

print("\nRevenue by month and channel:")
monthly_channel_revenue = sales.groupby(
    ["month", "sales_channel"]
)["total_revenue"].sum()

print(monthly_channel_revenue)

print("\nBest-revenue channel per month:")
channel_table = monthly_channel_revenue.unstack(fill_value=0)
print(channel_table.idxmax(axis=1))


# ==================================================
# 9. CATEGORY REVENUE CONTRIBUTION
# ==================================================

category_summary = sales.groupby("category").agg(
    total_revenue=("total_revenue", "sum"),
    total_profit=("total_profit", "sum")
)

category_summary["revenue_share_pct"] = (
    category_summary["total_revenue"]
    / category_summary["total_revenue"].sum() * 100
)

print("\n--- CATEGORY SUMMARY ---")
print(category_summary.sort_values(
    "total_revenue", ascending=False
))


# ==================================================
# 10. RECENT ORDERS
# ==================================================

print("\n--- FIVE MOST RECENT ORDERS ---")
print(
    sales.sort_values("order_date", ascending=False)[
        ["order_id", "order_date", "product_id", "total_revenue"]
    ].head(5)
)


# ==================================================
# 11. SAVE SUMMARY TABLES
# ==================================================

product_summary.to_csv(OUTPUT_DIR / "product_summary.csv")
customer_summary.to_csv(OUTPUT_DIR / "customer_summary.csv")
channel_summary.to_csv(OUTPUT_DIR / "channel_summary.csv")
employee_summary.to_csv(OUTPUT_DIR / "employee_summary.csv")
monthly_summary.to_csv(OUTPUT_DIR / "monthly_summary.csv")
category_summary.to_csv(OUTPUT_DIR / "category_summary.csv")

print("\nSummary CSV files saved in:", OUTPUT_DIR.resolve())


# ==================================================
# 12. VISUALIZATIONS
# ==================================================

# Chart 1: Monthly revenue trend
monthly_chart = monthly_summary.copy()
monthly_chart.index = monthly_chart.index.to_timestamp()

plt.figure(figsize=(10, 5))
plt.plot(
    monthly_chart.index,
    monthly_chart["total_revenue"],
    marker="o"
)
plt.title("Monthly Revenue Trend")
plt.xlabel("Month")
plt.ylabel("Total Revenue")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "monthly_revenue.png")
plt.show()
plt.close()


# Chart 2: Top 5 products by revenue
top_products = product_summary.head(5).sort_values(
    "total_revenue"
)

plt.figure(figsize=(9, 5))
plt.barh(
    top_products.index,
    top_products["total_revenue"]
)
plt.title("Top 5 Products by Revenue")
plt.xlabel("Total Revenue")
plt.ylabel("Product")
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "top_products_revenue.png")
plt.show()
plt.close()


# Chart 3: Revenue by sales channel
channel_chart = channel_summary.sort_values("total_revenue")

plt.figure(figsize=(8, 5))
plt.bar(
    channel_chart.index,
    channel_chart["total_revenue"]
)
plt.title("Revenue by Sales Channel")
plt.xlabel("Sales Channel")
plt.ylabel("Total Revenue")
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "channel_revenue.png")
plt.show()
plt.close()


# ==================================================
# 13. FINAL RECONCILIATION
# ==================================================

print("\n--- FINAL VALIDATION ---")
print("Orders loaded:", len(orders))
print("Sales rows after product merge:", len(sales))
print("Customer-sales rows:", len(customer_sales))
print("Employee-sales rows:", len(employee_sales))
print("Total revenue:", sales["total_revenue"].sum())
print("Total cost:", sales["total_cost"].sum())
print("Total profit:", sales["total_profit"].sum())

print("\nPython analysis completed.")
