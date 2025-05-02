import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# The Crumble Lab Logo-Based Brand Colors
COLOR_BROWN = "#402217"
COLOR_TAN = "#c19a6b"
COLOR_GOLD = "#8b5a2b"
COLOR_CREAM = "#f3e9dc"

st.set_page_config(page_title="Crumble Lab Sales Dashboard", layout="wide")
st.markdown("<h1 style='text-align: center;'>🍪 The Crumble Lab Sales Analytics Dashboard</h1>", unsafe_allow_html=True)

# Global Style for Dashboard
st.markdown("""
    <style>
        body {
            background-color: #f3e9dc;
        }
        h1, h2, h3, .stMetric, .css-qri22k, .css-1v0mbdj {
            color: #402217 !important;
        }
        section[data-testid="stSidebar"] {
            background-color: #f3e9dc;
        }
        .stMetric {
            background-color: #f3e9dc;
            border: 1px solid #c19a6b;
            border-radius: 10px;
            padding: 10px;
        }
        .stTabs [role="tab"] {
            background-color: #f3e9dc;
            color: #402217;
            font-weight: bold;
        }
        .stTabs [aria-selected="true"] {
            background-color: #c19a6b;
            color: white;
        }
    </style>
""", unsafe_allow_html=True)


# Load and Clean Data
df = pd.read_csv("CrumbleLabData.csv")
df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
df['date'] = pd.to_datetime(df['date'], errors='coerce')
df['product'] = df['product'].str.title().str.strip()
df.dropna(subset=['date'], inplace=True)

# Sidebar Filters
st.sidebar.header("Filter")

# Date filter
date_range = st.sidebar.date_input("Select Date Range", [df['date'].min(), df['date'].max()])

# Product filter with 'Select All'
all_products = df['product'].unique().tolist()
product_filter = st.sidebar.multiselect(
    "Filter by Product",
    options=["Select All"] + all_products,
    default=["Select All"]
)
if "Select All" in product_filter:
    product_filter = all_products

# Payment mode filter with 'Select All'
all_payments = df['mode_of_payment'].unique().tolist()
payment_filter = st.sidebar.multiselect(
    "Filter by Mode of Payment",
    options=["Select All"] + all_payments,
    default=["Select All"]
)
if "Select All" in payment_filter:
    payment_filter = all_payments

# Apply Filters
mask = (
    (df['date'].dt.date >= date_range[0]) &
    (df['date'].dt.date <= date_range[1]) &
    (df['product'].isin(product_filter)) &
    (df['mode_of_payment'].isin(payment_filter))
)
filtered_df = df[mask]

# Tabs
summary_tab, product_tab, customer_tab, order_tab = st.tabs(["Summary", "Product Insights", "Customer Insights", "Order Preferences"])

with summary_tab:
    st.subheader("📊 Summary")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Revenue", f"₱{filtered_df['amount'].sum():,.2f}")
    col2.metric("Avg. Order Value", f"₱{filtered_df.groupby('transaction_id')['amount'].sum().mean():,.2f}")
    col3.metric("Total Orders", filtered_df['transaction_id'].nunique())
    col4.metric("Top Product", filtered_df.groupby('product')['amount'].sum().idxmax())

with product_tab:
    st.subheader("📈 Revenue by Product")
    chart_type = st.selectbox("Choose chart type:", ["Bar Chart", "Pie Chart"])
    product_sales = filtered_df.groupby('product')['amount'].sum().sort_values(ascending=False)

    if chart_type == "Bar Chart":
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.barplot(x=product_sales.values, y=product_sales.index, ax=ax, color=COLOR_TAN)
        ax.set_title("Total Revenue by Product", color=COLOR_BROWN)
        ax.set_xlabel("Revenue (₱)", color=COLOR_BROWN)
        ax.set_ylabel("Product", color=COLOR_BROWN)
        ax.tick_params(colors=COLOR_BROWN)
        st.pyplot(fig)
    else:
        top5 = product_sales.head(5)
        fig, ax = plt.subplots(figsize=(6, 6))
        ax.pie(top5, labels=top5.index, autopct='%1.1f%%', startangle=140,
               colors=[COLOR_BROWN, COLOR_TAN, COLOR_GOLD, "#a9745f", "#c89f7f"])
        ax.set_title("Revenue Share by Product", color=COLOR_BROWN)
        st.pyplot(fig)

    st.subheader("📅 Daily Sales Trend")
    daily_sales = filtered_df.groupby(filtered_df['date'].dt.date)['amount'].sum()
    fig, ax = plt.subplots(figsize=(10, 5))
    daily_sales.plot(marker='o', ax=ax, color=COLOR_BROWN)
    ax.set_title("Daily Sales Revenue", color=COLOR_BROWN)
    ax.set_xlabel("Date", color=COLOR_BROWN)
    ax.set_ylabel("Revenue (₱)", color=COLOR_BROWN)
    ax.grid(True, color=COLOR_TAN)
    ax.tick_params(colors=COLOR_BROWN)
    st.pyplot(fig)

    st.subheader("🥧 All-Time Top 5 Products")
    top5_all_time = df.groupby('product')['amount'].sum().sort_values(ascending=False).head(5)
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pie(top5_all_time, labels=top5_all_time.index, autopct='%1.1f%%', startangle=140,
           colors=[COLOR_BROWN, COLOR_TAN, COLOR_GOLD, "#a9745f", "#c89f7f"])
    ax.set_title("All-Time Top 5 Products", color=COLOR_BROWN)
    st.pyplot(fig)

with customer_tab:
    st.subheader("👥 Top 5 Customers by Order Frequency")
    top5_customers = df.groupby('customer')['transaction_id'].nunique().sort_values(ascending=False).head(5)
    top5_customers_df = top5_customers.reset_index().rename(columns={'transaction_id': 'Order Count'})

    view_option = st.selectbox("View customer table?", ["Hide", "Show"])
    if view_option == "Show":
        st.dataframe(top5_customers_df)

    fig, ax = plt.subplots(figsize=(8, 4))
    top5_customers.plot(kind='barh', ax=ax, color=COLOR_TAN)
    ax.set_title("Top 5 Customers by Number of Orders", color=COLOR_BROWN)
    ax.set_xlabel("Number of Orders", color=COLOR_BROWN)
    ax.tick_params(colors=COLOR_BROWN)
    ax.invert_yaxis()
    st.pyplot(fig)

    st.subheader("🔁 New vs Returning Customers")
    customer_orders = df.groupby('customer')['transaction_id'].nunique()
    new = customer_orders[customer_orders == 1].count()
    returning = customer_orders[customer_orders > 1].count()
    col_n, col_r = st.columns(2)
    col_n.metric("New Customers", new)
    col_r.metric("Returning Customers", returning)

    pie_size_customer = st.slider("Customer Pie Chart Size", 4, 12, 6, 1, key='customer_pie')
    fig, ax = plt.subplots(figsize=(pie_size_customer, pie_size_customer))
    ax.pie([new, returning], labels=["New", "Returning"], autopct='%1.1f%%', startangle=90,
           colors=[COLOR_TAN, COLOR_BROWN], wedgeprops={'edgecolor': 'white'})
    ax.set_title("New vs Returning Customers", color=COLOR_BROWN, pad=20)
    ax.axis('equal')
    plt.tight_layout()
    st.pyplot(fig)

with order_tab:
    st.subheader("🚚 Order Method Preference")
    pickup_counts = df['pickup/delivery'].value_counts()

    pie_size_order = st.slider("Order Method Pie Chart Size", 4, 12, 6, 1, key='order_pie')
    fig, ax = plt.subplots(figsize=(pie_size_order, pie_size_order))
    pickup_counts.plot.pie(autopct='%1.1f%%', labels=pickup_counts.index, ax=ax, startangle=90,
                           colors=[COLOR_TAN, COLOR_BROWN], wedgeprops={'edgecolor': 'white'})
    ax.set_ylabel("")
    ax.set_title("Pickup vs Delivery Share", color=COLOR_BROWN, pad=20)
    ax.axis('equal')
    plt.tight_layout()
    st.pyplot(fig)
