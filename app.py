import streamlit as st
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns

# Page configuration
st.set_page_config(page_title="Sales Analysis Dashboard", page_icon="📊", layout="wide")

# Theme style
sns.set_theme(style="whitegrid")

@st.cache_data
def load_data():
    try:
        conn = sqlite3.connect('sales_system.db')
        sales = pd.read_sql_query("SELECT * FROM Sales", conn)
        products = pd.read_sql_query("SELECT * FROM Products", conn)
        customers = pd.read_sql_query("SELECT * FROM Customers", conn)
        conn.close()
        
        # Preprocessing
        sales['sale_date'] = pd.to_datetime(sales['sale_date'])
        sales['month'] = sales['sale_date'].dt.to_period('M').astype(str)
        
        # Convert Dollars to Rupees (1 USD ~ 83.5 INR)
        sales['revenue'] = sales['revenue'] * 83.5
        products['price'] = products['price'] * 83.5
        
        return sales, products, customers
    except Exception as e:
        st.error("Database not found! Please run `python generate_data.py` and `python sales_analysis.py` first.")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

sales, products, customers = load_data()

if not sales.empty:
    st.title("📊 Sales Analysis Dashboard")
    st.markdown("Interactive frontend for the Sales Analysis System built with Streamlit.")

    # --- KPIs ---
    st.header("Key Performance Indicators")
    total_revenue = sales['revenue'].sum()
    total_orders = len(sales)
    avg_order_value = sales['revenue'].mean()
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Revenue", f"₹{total_revenue:,.2f}")
    col2.metric("Total Orders", f"{total_orders:,}")
    col3.metric("Average Order Value", f"${avg_order_value / 83.5:,.2f}")
    
    st.divider()

    # --- Visualizations ---
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📈 Monthly Sales Trend")
        monthly_sales = sales.groupby('month')['revenue'].sum().reset_index()
        fig, ax = plt.subplots(figsize=(8, 4))
        sns.lineplot(data=monthly_sales, x='month', y='revenue', marker='o', ax=ax, color='b')
        plt.xticks(rotation=45)
        ax.set_ylabel("Revenue (₹)")
        ax.set_xlabel("Month")
        st.pyplot(fig)

    with col2:
        st.subheader("🏆 Top 10 Products by Revenue")
        top_products = sales.groupby('product_id')['revenue'].sum().reset_index()
        top_products = top_products.merge(products[['product_id', 'product_name']], on='product_id')
        top_products = top_products.sort_values(by='revenue', ascending=False).head(10)
        
        fig, ax = plt.subplots(figsize=(8, 4))
        sns.barplot(data=top_products, x='revenue', y='product_name', palette='viridis', hue='product_name', legend=False, ax=ax)
        ax.set_xlabel("Revenue (₹)")
        ax.set_ylabel("")
        st.pyplot(fig)
        
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🍰 Revenue by Category")
        merged_cat = sales.merge(products[['product_id', 'category']], on='product_id')
        category_sales = merged_cat.groupby('category')['revenue'].sum()
        fig, ax = plt.subplots(figsize=(6, 6))
        ax.pie(category_sales, labels=category_sales.index, autopct='%1.1f%%', startangle=140, colors=sns.color_palette("pastel"))
        st.pyplot(fig)

    with col2:
        st.subheader("👥 Revenue by Customer Segment")
        merged_cust = sales.merge(customers[['customer_id', 'segment']], on='customer_id')
        segment_sales = merged_cust.groupby('segment')['revenue'].sum().reset_index()
        
        fig, ax = plt.subplots(figsize=(8, 4))
        sns.barplot(data=segment_sales, x='segment', y='revenue', palette='magma', hue='segment', legend=False, ax=ax)
        ax.set_xlabel("Customer Segment")
        ax.set_ylabel("Revenue (₹)")
        st.pyplot(fig)
        
    st.divider()
    
    st.subheader("📋 Recent Sales Data")
    st.dataframe(sales.sort_values(by='sale_date', ascending=False).head(20))

else:
    st.warning("No data available.")
