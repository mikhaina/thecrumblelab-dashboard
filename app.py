import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Page Setup
st.set_page_config(page_title="Crumble Lab Sales Dashboard", layout="wide")
st.markdown("<h1 style='text-align: center;'>🍪 The Crumble Lab: Sales Analytics Dashboard</h1>", unsafe_allow_html=True)

# Load and Clean Data
df = pd.read_csv("CrumbleLabData.csv")
df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
df['date'] = pd.to_datetime(df['date'], errors='coerce')
df['product'] = df['product'].str.title().str.strip()
df.dropna(subset=['date'], inplace=True)

# Sidebar Filters
st.sidebar.header("Filter")
date_range = st.sidebar.date_input("Select Date Range", [df['date'].min(), df['date'].max()])
product_filter = st.sidebar.multiselect("Filter by Product", df['product'].unique(), default=df['product'].unique())
payment_filter = st.sidebar.multiselect("Filter by Mode of Payment", df['mode_of_payment'].unique(), default=df['mode_of_payment'].unique())

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
        sns.barplot(x=product_sales.values, y=product_sales.index, ax=ax)
        ax.set_title("Total Revenue by Product")
        ax.set_xlabel("Revenue (₱)")
        ax.set_ylabel("Product")
        st.pyplot(fig)
    else:
        top5 = product_sales.head(5)
        fig, ax = plt.subplots(figsize=(6, 6))
        ax.pie(top5, labels=top5.index, autopct='%1.1f%%', startangle=140)
        ax.set_title("Revenue Share by Product")
        st.pyplot(fig)

    st.subheader("📅 Daily Sales Trend")
    daily_sales = filtered_df.groupby(filtered_df['date'].dt.date)['amount'].sum()
    fig, ax = plt.subplots(figsize=(10, 5))
    daily_sales.plot(marker='o', ax=ax)
    ax.set_title("Daily Sales Revenue")
    ax.set_xlabel("Date")
    ax.set_ylabel("Revenue (₱)")
    ax.grid(True)
    st.pyplot(fig)

    st.subheader("🥧 All-Time Top 5 Products")
    top5_all_time = df.groupby('product')['amount'].sum().sort_values(ascending=False).head(5)
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pie(top5_all_time, labels=top5_all_time.index, autopct='%1.1f%%', startangle=140)
    ax.set_title("All-Time Top 5 Products")
    st.pyplot(fig)

with customer_tab:
    st.subheader("👥 Top 5 Customers by Order Frequency")

    top5_customers = df.groupby('customer')['transaction_id'].nunique().sort_values(ascending=False).head(5)
    top5_customers_df = top5_customers.reset_index().rename(columns={'transaction_id': 'Order Count'})
    
    view_option = st.selectbox("View customer table?", ["Hide", "Show"])
    
    if view_option == "Show":
        st.dataframe(top5_customers_df)

    fig, ax = plt.subplots(figsize=(8, 4))
    top5_customers.plot(kind='barh', ax=ax, color='lightcoral')
    ax.set_title("Top 5 Customers by Number of Orders")
    ax.set_xlabel("Number of Orders")
    ax.invert_yaxis()
    st.pyplot(fig)

    st.subheader("🔁 New vs Returning Customers")
    customer_orders = df.groupby('customer')['transaction_id'].nunique()
    new = customer_orders[customer_orders == 1].count()
    returning = customer_orders[customer_orders > 1].count()
    col_n, col_r = st.columns(2)
    col_n.metric("New Customers", new)
    col_r.metric("Returning Customers", returning)

    fig, ax = plt.subplots()
    ax.pie([new, returning], labels=["New", "Returning"], autopct='%1.1f%%', startangle=90)
    ax.set_title("New vs Returning Customers")
    st.pyplot(fig)

with order_tab:
    st.subheader("🚚 Order Method Preference")
    pickup_counts = df['pickup/delivery'].value_counts()
    fig, ax = plt.subplots()
    pickup_counts.plot.pie(autopct='%1.1f%%', labels=pickup_counts.index, ax=ax, startangle=90)
    ax.set_ylabel("")
    ax.set_title("Pickup vs Delivery Share")
    st.pyplot(fig)
