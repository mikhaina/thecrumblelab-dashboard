import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="Crumble Lab Sales Dashboard", layout="wide")
st.title("🍪 Crumble Lab Sales Analytics Dashboard")

# Load and clean data
df = pd.read_csv("CrumbleLabData.csv")
df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
df['date'] = pd.to_datetime(df['date'], errors='coerce')
df['product'] = df['product'].str.title().str.strip()
df.dropna(subset=['date'], inplace=True)

# Sidebar filters
st.sidebar.header("Filter")
date_range = st.sidebar.date_input("Select Date Range", [df['date'].min(), df['date'].max()])
product_filter = st.sidebar.multiselect("Filter by Product", df['product'].unique(), default=df['product'].unique())
payment_filter = st.sidebar.multiselect("Filter by Mode of Payment", df['mode_of_payment'].unique(), default=df['mode_of_payment'].unique())

# Apply filters
mask = (
    (df['date'].dt.date >= date_range[0]) &
    (df['date'].dt.date <= date_range[1]) &
    (df['product'].isin(product_filter)) &
    (df['mode_of_payment'].isin(payment_filter))
)
filtered_df = df[mask]

# Summary KPIs
st.subheader("📊 Summary")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Revenue", f"₱{filtered_df['amount'].sum():,.2f}")
col2.metric("Avg. Order Value", f"₱{filtered_df.groupby('transaction_id')['amount'].sum().mean():,.2f}")
col3.metric("Total Orders", filtered_df['transaction_id'].nunique())
col4.metric("Top Product", filtered_df.groupby('product')['amount'].sum().idxmax())

# Revenue by Product
st.subheader("📈 Revenue by Product")

chart_type = st.selectbox("Choose chart type:", ["Bar Chart", "Pie Chart"])

product_sales = filtered_df.groupby('product')['amount'].sum().sort_values(ascending=False)

if chart_type == "Bar Chart":
    fig1, ax1 = plt.subplots(figsize=(10,6))
    sns.barplot(x=product_sales.values, y=product_sales.index, ax=ax1)
    ax1.set_title("Total Revenue by Product")
    ax1.set_xlabel("Revenue (₱)")
    ax1.set_ylabel("Product")
    st.pyplot(fig1)

elif chart_type == "Pie Chart":
    top5 = product_sales.head(5)
    fig2, ax2 = plt.subplots(figsize=(6,6))
    ax2.pie(top5, labels=top5.index, autopct='%1.1f%%', startangle=140)
    ax2.set_title("Revenue Share by Product")
    st.pyplot(fig2)

# Daily Sales Trend
st.subheader("📅 Daily Sales Trend")
daily_sales = filtered_df.groupby(filtered_df['date'].dt.date)['amount'].sum()
fig2, ax2 = plt.subplots(figsize=(10,5))
daily_sales.plot(marker='o', ax=ax2)
ax2.set_title("Daily Sales Revenue")
ax2.set_xlabel("Date")
ax2.set_ylabel("Revenue (₱)")
ax2.grid(True)
st.pyplot(fig2)

# Pie Chart: Top 5 Products
st.subheader("🥧 All-Time Top 5 Products - Revenue Share")
top5_all_time = df.groupby('product')['amount'].sum().sort_values(ascending=False).head(5)
fig_static, ax_static = plt.subplots(figsize=(6,6))
ax_static.pie(top5_all_time, labels=top5_all_time.index, autopct='%1.1f%%', startangle=140)
ax_static.set_title("All-Time Top 5 Products")
st.pyplot(fig_static)


# 👥 Top 5 Customers by Order Frequency
st.subheader("👥 Top 5 Customers by Order Frequency")

top5_customers = df.groupby('customer')['transaction_id'].nunique().sort_values(ascending=False).head(5)

# Show as table
st.dataframe(top5_customers.reset_index().rename(columns={'transaction_id': 'Order Count'}))

# 🚚 Preferred Order Method (Pickup vs Delivery)
st.subheader("🚚 Order Method Preference")

pickup_counts = df['pickup/delivery'].value_counts()

fig_pickup, ax_pickup = plt.subplots()
pickup_counts.plot.pie(autopct='%1.1f%%', labels=pickup_counts.index, ax=ax_pickup, startangle=90)
ax_pickup.set_ylabel("")
ax_pickup.set_title("Pickup vs Delivery Share")
st.pyplot(fig_pickup)

# 🔁 New vs Returning Customers
st.subheader("🔁 Customer Type Distribution")

# Count number of orders per customer
customer_orders = df.groupby('customer')['transaction_id'].nunique()

# Define new vs returning
new = customer_orders[customer_orders == 1].count()
returning = customer_orders[customer_orders > 1].count()

fig_cust, ax_cust = plt.subplots()
ax_cust.pie([new, returning], labels=["New", "Returning"], autopct='%1.1f%%', startangle=90)
ax_cust.set_title("New vs Returning Customers")
st.pyplot(fig_cust)
