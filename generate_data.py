import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

def generate_data():
    # 1. Generate Customers
    np.random.seed(42)
    customer_ids = range(1, 51) # 50 customers
    names = [f"Customer_{i}" for i in customer_ids]
    cities = ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix', 'Philadelphia', 'San Antonio', 'San Diego', 'Dallas', 'San Jose']
    segments = ['Consumer', 'Corporate', 'Home Office']
    
    customers = pd.DataFrame({
        'customer_id': customer_ids,
        'name': names,
        'city': np.random.choice(cities, len(customer_ids)),
        'segment': np.random.choice(segments, len(customer_ids))
    })
    
    # 2. Generate Products
    product_ids = range(101, 121) # 20 products
    categories = ['Electronics', 'Furniture', 'Office Supplies']
    
    products = pd.DataFrame({
        'product_id': product_ids,
        'product_name': [f"Product_{i}" for i in product_ids],
        'category': np.random.choice(categories, len(product_ids)),
        'price': np.round(np.random.uniform(10.0, 500.0, len(product_ids)), 2)
    })
    
    # 3. Generate Sales
    num_sales = 500
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2023, 12, 31)
    
    sales_dates = [start_date + timedelta(days=random.randint(0, (end_date - start_date).days)) for _ in range(num_sales)]
    sales_customer_ids = np.random.choice(customer_ids, num_sales)
    sales_product_ids = np.random.choice(product_ids, num_sales)
    quantities = np.random.randint(1, 10, num_sales)
    
    sales = pd.DataFrame({
        'sale_id': range(1, num_sales + 1),
        'customer_id': sales_customer_ids,
        'product_id': sales_product_ids,
        'quantity': quantities,
        'sale_date': sales_dates
    })
    
    # Merge to calculate revenue
    sales = sales.merge(products[['product_id', 'price']], on='product_id', how='left')
    sales['revenue'] = sales['quantity'] * sales['price']
    sales.drop(columns=['price'], inplace=True)
    
    # Format date
    sales['sale_date'] = sales['sale_date'].dt.strftime('%Y-%m-%d')
    
    # Save to CSV
    customers.to_csv('customers.csv', index=False)
    products.to_csv('products.csv', index=False)
    sales.to_csv('sales.csv', index=False)
    
    print("Sample datasets created successfully: customers.csv, products.csv, sales.csv")

if __name__ == "__main__":
    generate_data()
