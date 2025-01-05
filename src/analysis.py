import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import requests
from bs4 import BeautifulSoup
import re
import unicodedata
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler,PolynomialFeatures
from sklearn.linear_model import LinearRegression
from utils import extract_column_from_header

# Read the CSV file from the data folder
script_dir = os.path.dirname(__file__)  # Script directory
file_path = os.path.join(script_dir, '../data/products.csv')
inventory_df = pd.read_csv(file_path)

# Refine our_price: Remove any non-numerical signs, then set any non-number value to the currently existing minimum numerical value
inventory_df['our_price'] = inventory_df['our_price'].str.replace('$', '')
inventory_df['our_price'] = pd.to_numeric(inventory_df['our_price'], downcast='integer', errors='coerce')
our_price_min = inventory_df['our_price'].min()
inventory_df['our_price'].replace(np.nan,our_price_min, inplace=True)

# Refine current_stock: Set any non-number value to 0
inventory_df['current_stock'] = pd.to_numeric(inventory_df['current_stock'], downcast='integer', errors='coerce')
inventory_df['current_stock'].replace(np.nan,0, inplace=True)

# Refine restock_threshold: Set any non-number value to the currently existing minimum numerical value
restock_threshold_min = inventory_df['restock_threshold'].min()
inventory_df['restock_threshold'].replace(np.nan,restock_threshold_min, inplace=True)

# Refine restock_date: Convert to datetime and remove any rows with a NaN here
inventory_df['restock_date'] = pd.to_datetime(inventory_df['restock_date'])
inventory_df.dropna(subset=['restock_date'])

# Refine category: This depends on product_name. Check if product_name contains certain words, then replace the category
inventory_df['category'] = inventory_df['category'].str.lower()

coffee_list = ['coffee', 'bean', 'brew']
coffee_pattern = '|'.join(coffee_list)
inventory_df.loc[inventory_df['product_name'].str.contains(coffee_pattern, case=False), 'category'] = 'coffee'

tea_list = ['tea', 'matcha', 'chai']
tea_pattern = '|'.join(tea_list)
inventory_df.loc[inventory_df['product_name'].str.contains(tea_pattern, case=False), 'category'] = 'tea'

# Output the first five rows of the DataFrame for checking purposes
print(inventory_df)

#For our economic insight, we will be comparing the total per-pound price of coffee, tea, etc. for this store with the global price per pound.

#First, obtain the global prices per pound and extract the coffee and tea prices.
# Wikipedia's page on the most valuable crops and livestock products has a table with global production in USD per metric ton, which we can convert to USD per pound, as well as rows for both coffee (green) and tea.
static_url = "https://en.wikipedia.org/wiki/List_of_most_valuable_crops_and_livestock_products"
wikipedia_data  = requests.get(static_url).text

# Use BeautifulSoup() to create a BeautifulSoup object from a response text content, then verify if the parse ran correctly
wikipedia_soup = BeautifulSoup(wikipedia_data, 'html.parser')
# print(wikipedia_soup.title) # To verify whether this works

# Use the find_all function in the BeautifulSoup object with the element type of 'table', then assign the result to a list called 'html_tables'
html_tables = wikipedia_soup.find_all('table')
products_table = html_tables[0]

column_names = []

# Apply the find_all() function with 'th' element on products_table
# Iterate each th element and apply the provided extract_column_from_header() to get a column name
# Append the Non-empty column name (`if name is not None and len(name) > 0`) into a list called column_names
column_headers = products_table.find_all('th')
for row in column_headers:
    name = extract_column_from_header(row)
    if name is not None and len(name) > 0:
        column_names.append(name)

#print(column_names)

# We will create an empty dictionary with keys from the extracted column names. We can then convert this into a Pandas dataframe
products_dict= dict.fromkeys(column_names)

# Initialize the products_dict with each value to be an empty list
products_dict['Crop or Livestock'] = []
products_dict['Global gross production value in billion US$'] = []
products_dict['Global production in metric tons'] = []
products_dict['Global production in US$/metric ton'] = []
products_dict['Country with highest gross production value in billion USD'] = []

extracted_row = 0
#Extract each table 
for table_number,table in enumerate(wikipedia_soup.find_all('table',"wikitable sortable")):
   # get table row 
    for rows in table.find_all("tr"):
        if rows.th:
            flag = False
        else:
            flag = True
        row=rows.find_all('td')
        # print(row)
        
        if flag:
            crop=row[0].get_text().replace('\n', '')
            # print(crop)
            products_dict['Crop or Livestock'].append(crop)
            
            global_gpv=row[1].get_text()
            # print(global_gpv)
            global_gpv_num = global_gpv.strip('$').replace(',','').replace('\n', '')
            products_dict['Global gross production value in billion US$'].append(float(global_gpv_num))
            
            global_prod = row[2].get_text()
            # print(global_prod)
            global_prod_num = global_prod.replace(',','').replace('\n', '')
            products_dict['Global production in metric tons'].append(float(global_prod_num))
            
            dollars_per_ton = row[3].get_text()
            # print(dollars_per_ton)
            dollars_per_ton_num = dollars_per_ton.strip('$').replace(',','').replace('\n', '')
            products_dict['Global production in US$/metric ton'].append(float(dollars_per_ton_num))
            
            highest_gross_country = row[4].get_text().replace('\n', '')
            # print(highest_gross_country)
            products_dict['Country with highest gross production value in billion USD'].append(highest_gross_country)

products_df= pd.DataFrame({ key:pd.Series(value) for key, value in products_dict.items() })
# print(products_df.describe)

# Now, get the global production in USD/metric ton for coffee and tea, and for each, convert it to USD/pound.
coffee_production = products_df[products_df['Crop or Livestock'].str.contains('Coffee')]['Global production in US$/metric ton'].item()
tea_production = products_df[products_df['Crop or Livestock'].str.contains('Tea')]['Global production in US$/metric ton'].item()

coffee_production_per_pound = coffee_production/2204.62
tea_production_per_pound = tea_production/2204.62

print(coffee_production_per_pound)
print(tea_production_per_pound)

# TODO: Extract weight per unit from each product_name, then add a new pounds_per_unit column
inventory_df['pounds_per_unit'] = np.nan


# Multiply our_price by current_stock to get total_price. Then multiply each pounds_per_unit by current_stock to get total_quantity
inventory_df['total_price'] = np.nan
inventory_df['total_quantity'] = np.nan

# Extract the sum of all total_price and total_quantity where category = coffee, then divide coffee_total_price by coffee_total_quantity to get coffee_price_per_pound
coffee_total_price = inventory_df[inventory_df['category']=='coffee']['total_price'].item().sum()
coffee_total_quantity = inventory_df[inventory_df['category']=='coffee']['total_quantity'].item().sum()
coffee_price_per_pound = coffee_total_price/coffee_total_quantity

# Do the same thing with all items in the tea category
tea_total_price = inventory_df[inventory_df['category']=='tea']['total_price'].item().sum()
tea_total_quantity = inventory_df[inventory_df['category']=='tea']['total_quantity'].item().sum()
tea_price_per_pound = tea_total_price/tea_total_quantity

# Finally, generate the report comparing our prices per pound for both coffee and tea with the global price per pound for each
