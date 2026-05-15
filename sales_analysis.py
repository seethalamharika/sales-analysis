import pandas as pd
import numpy as np
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Set aesthetic parameters in one step
sns.set_theme(style="whitegrid")

def setup_database():
    """Sets up an SQLite database and loads data from CSV files."""
    print("Setting up SQLite Database...")
    conn = sqlite3.connect('sales_system.db')
    cursor = conn.cursor()

    # Load Data via Pandas
    try:
        customers = pd.read_csv("customers.csv")
        products = pd.read_csv("products.csv")
        sales = pd.read_csv("sales.csv")
    except FileNotFoundError:
        print("Error: CSV files not found. Please run generate_data.py first.")
        return None

    # Push to SQL Database
    customers.to_sql('Customers', conn, if_exists='replace', index=False)
    products.to_sql('Products', conn, if_exists='replace', index=False)
    sales.to_sql('Sales', conn, if_exists='replace', index=False)
    
    print("Data loaded into SQLite database successfully.\n")
    return conn

def execute_sql_queries(conn):
    """Executes sample SQL queries as per the PRD."""
    print("--- 1. SQL Queries ---")
    
    # Query 1: Total Sales
    query_total_sales = "SELECT SUM(revenue) AS total_revenue FROM Sales;"
    total_sales = pd.read_sql_query(query_total_sales, conn)
    print(f"Total Revenue (SQL):\n${total_sales['total_revenue'].iloc[0]:,.2f}\n")
    
    # Query 2: Top 5 Products
    query_top_products = """
    SELECT product_id, SUM(revenue) AS total
    FROM Sales
    GROUP BY product_id
    ORDER BY total DESC
    LIMIT 5;
    """
    top_products = pd.read_sql_query(query_top_products, conn)
    print("Top 5 Products by Revenue (SQL):")
    print(top_products)
    print("\n")

def pandas_numpy_analysis():
    """Performs data analysis using Pandas and NumPy."""
    print("--- 2. Pandas & NumPy Analysis ---")
    
    # Load data
    sales = pd.read_csv("sales.csv")
    customers = pd.read_csv("customers.csv")
    products = pd.read_csv("products.csv")
    
    # Data Cleaning & Preprocessing
    sales['sale_date'] = pd.to_datetime(sales['sale_date'])
    sales.drop_duplicates(inplace=True)
    
    # 1. Total Revenue
    total_revenue = sales['revenue'].sum()
    print(f"Total Revenue (Pandas): ${total_revenue:,.2f}")
    
    # 2. Monthly Sales Trend
    sales['month'] = sales['sale_date'].dt.to_period('M')
    monthly_sales = sales.groupby('month')['revenue'].sum()
    print("\nMonthly Sales Trend:")
    print(monthly_sales)
    
    # 3. Top Products
    top_products = sales.groupby('product_id')['revenue'].sum().sort_values(ascending=False).head(5)
    print("\nTop 5 Products (Pandas):")
    print(top_products)
    
    # 4. Customer Segmentation
    merged_sales = sales.merge(customers, on='customer_id')
    segment_sales = merged_sales.groupby('segment')['revenue'].sum()
    print("\nRevenue by Customer Segment:")
    print(segment_sales)
    
    # 5. Growth Rate (NumPy)
    monthly_sales_array = monthly_sales.values
    growth_rate = np.diff(monthly_sales_array) / monthly_sales_array[:-1] * 100
    print("\nMonthly Growth Rate (Percentage):")
    # Aligning growth rate with months
    months = monthly_sales.index[1:] # Drop first month since it has no prior month to compare
    growth_df = pd.DataFrame({'Month': months, 'Growth Rate (%)': np.round(growth_rate, 2)})
    print(growth_df)
    print("\n")
    
    return sales, merged_sales, products, monthly_sales

def generate_visualizations(sales, merged_sales, products, monthly_sales):
    """Generates and saves visualizations."""
    print("--- 3. Generating Visualizations ---")
    
    # Create an output directory for visuals
    os.makedirs('dashboard_visuals', exist_ok=True)
    
    # 1. Line Chart -> Sales over time
    plt.figure(figsize=(10, 5))
    monthly_sales.plot(kind='line', marker='o', color='b')
    plt.title("Monthly Sales Trend")
    plt.xlabel("Month")
    plt.ylabel("Revenue ($)")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig('dashboard_visuals/monthly_sales_trend.png')
    plt.close()
    
    # 2. Bar Chart -> Top 10 products
    top_10 = sales.groupby('product_id')['revenue'].sum().sort_values(ascending=False).head(10)
    top_10_named = top_10.reset_index().merge(products[['product_id', 'product_name']], on='product_id')
    
    plt.figure(figsize=(10, 5))
    sns.barplot(x='revenue', y='product_name', data=top_10_named, hue='product_name', palette='viridis', legend=False)
    plt.title("Top 10 Products by Revenue")
    plt.xlabel("Revenue ($)")
    plt.ylabel("Product")
    plt.tight_layout()
    plt.savefig('dashboard_visuals/top_10_products.png')
    plt.close()
    
    # 3. Pie Chart -> Category distribution
    merged_with_cats = sales.merge(products, on='product_id')
    category_sales = merged_with_cats.groupby('category')['revenue'].sum()
    
    plt.figure(figsize=(8, 8))
    plt.pie(category_sales, labels=category_sales.index, autopct='%1.1f%%', startangle=140, colors=sns.color_palette("pastel"))
    plt.title("Revenue Distribution by Category")
    plt.savefig('dashboard_visuals/category_distribution.png')
    plt.close()
    
    print("Visualizations saved in 'dashboard_visuals' folder.")

if __name__ == "__main__":
    print("=== Starting Sales Analysis ===\n")
    
    # Phase 1: Database Setup and SQL querying
    conn = setup_database()
    if conn:
        execute_sql_queries(conn)
        conn.close()
        
    # Phase 2 & 3: Pandas/NumPy Analysis and Visualization
    sales_data, merged_sales_data, products_data, monthly_sales_data = pandas_numpy_analysis()
    generate_visualizations(sales_data, merged_sales_data, products_data, monthly_sales_data)
    
    print("\n=== Analysis Complete ===")
