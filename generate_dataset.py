import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Dataset configuration matching OLAP schema requirements
num_records = 10000
start_date = datetime(2022, 1, 1)
end_date = datetime(2024, 12, 31)

regions = ['North America', 'Europe', 'Asia Pacific', 'Latin America']
categories = {
    'Electronics': ['Smartphones', 'Laptops', 'Tablets'],
    'Furniture': ['Chairs', 'Tables', 'Beds'],
    'Office Supplies': ['Paper', 'Pens', 'Binders'],
    'Clothing': ['Shirts', 'Pants', 'Shoes']
}
segments = ['Consumer', 'Corporate', 'Home Office']

data = []
for i in range(num_records):
    date = start_date + timedelta(days=np.random.randint(0, (end_date - start_date).days))
    region = np.random.choice(regions)
    cat = np.random.choice(list(categories.keys()))
    subcat = np.random.choice(categories[cat])

    qty = np.random.randint(1, 10)
    price = np.random.uniform(10, 500)
    revenue = qty * price
    cost = revenue * np.random.uniform(0.5, 0.8)
    profit = revenue - cost

    data.append({
        'order_date': date.strftime('%Y-%m-%d'),
        'year': date.year,
        'quarter': (date.month - 1) // 3 + 1,
        'month': date.month,
        'month_name': date.strftime('%B'),
        'region': region,
        'country': f"Country_{np.random.randint(1, 10)}",
        'category': cat,
        'subcategory': subcat,
        'customer_segment': np.random.choice(segments),
        'quantity': qty,
        'unit_price': round(price, 2),
        'revenue': round(revenue, 2),
        'cost': round(cost, 2),
        'profit': round(profit, 2),
        'profit_margin': round(profit / revenue, 4)
    })

df = pd.DataFrame(data)

# Ensure data/ folder exists before saving
import os
if not os.path.exists('data'):
    os.makedirs('data')

df.to_csv('data/global_retail_sales.csv', index=False)
print("✓ Dataset successfully created with 10,000 rows at data/global_retail_sales.csv")