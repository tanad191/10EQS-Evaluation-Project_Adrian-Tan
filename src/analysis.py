from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import requests
import sys
from utils import extract_column_from_header

dataPath = sys.argv[1]

# Read the CSV file from the data folder
script_dir = os.path.dirname(__file__)  # Script directory
file_path = os.path.join(script_dir, '../' + dataPath)
inventory_df = pd.read_csv(file_path)

# Refine our_price: Remove any non-numerical signs, then set any non-number value to the currently existing minimum numerical value
inventory_df['our_price'] = inventory_df['our_price'].str.replace('$', '')
inventory_df['our_price'] = pd.to_numeric(inventory_df['our_price'], downcast='integer', errors='coerce')
our_price_min = inventory_df['our_price'].min()
inventory_df['our_price'] = inventory_df['our_price'].replace(np.nan,our_price_min)

# Refine current_stock: Set any non-number value to 0
inventory_df['current_stock'] = pd.to_numeric(inventory_df['current_stock'], downcast='integer', errors='coerce')
inventory_df['current_stock'] = inventory_df['current_stock'].replace(np.nan,0)

# Refine restock_threshold: Set any non-number value to the currently existing minimum numerical value
restock_threshold_min = inventory_df['restock_threshold'].min()
inventory_df['restock_threshold'] = inventory_df['restock_threshold'].replace(np.nan,restock_threshold_min)

# Refine restock_date: Convert to datetime
inventory_df['restock_date'] = pd.to_datetime(inventory_df['restock_date'],format='mixed').dt.strftime('%Y-%m-%d')

# Refine category: This depends on product_name. Check if product_name contains certain words, then replace the category
inventory_df['category'] = inventory_df['category'].str.capitalize()

coffee_list = ['coffee', 'bean', 'brew']
coffee_pattern = '|'.join(coffee_list)
inventory_df.loc[inventory_df['product_name'].str.contains(coffee_pattern, case=False), 'category'] = 'Coffee'

tea_list = ['tea', 'matcha', 'chai']
tea_pattern = '|'.join(tea_list)
inventory_df.loc[inventory_df['product_name'].str.contains(tea_pattern, case=False), 'category'] = 'Tea'

# For our economic insight, we will be comparing the total per-pound price of beverage materials including coffee and tea for this store per year with the average price per pound per year for both beverage types.
# This will allow us to determine the deviation between the yearly earnings by our shop and the average expenses per year.
# Assume that the restock threshold indicates how much of each product will be purchased per month.

# Extract weight per unit from each product_name. If the unit is absent, assume the product is sold in batches of 1 pound.
inventory_df['unit_number'] = inventory_df['product_name'].str.extract('(\d+)')
inventory_df['unit_number'].fillna(1)

# First, convert the unit number into pounds per unit
inventory_df['pounds_per_unit'] = np.nan

# Then, multiply each our_price by restock_threshold to get price_per_restock, and each pounds_per_unit by current_stock to get weight_per_restock
inventory_df['price_per_restock'] = np.nan
inventory_df['weight_per_restock'] = np.nan

for index, row in inventory_df.iterrows():
    r1 = row['unit_number']
    price = row['our_price']
    stock = row['restock_threshold']
    r2 = 1.0
    if r1: # Change r2 from the default pounds per unit only if the unit number is defined in the product name
        if 'lb' in row['product_name']:
            r2 = float(r1)
        elif 'oz' in row['product_name']:
            r2 = float(r1)/16
        elif 'bags' in row['product_name']:
            r2 = float(r1)/200
    
    inventory_df.at[index, 'pounds_per_unit'] = r2
    inventory_df.at[index, 'price_per_restock'] = price * stock
    inventory_df.at[index, 'weight_per_restock'] = r2 * stock

# Output the DataFrame for checking purposes
# print(inventory_df)

# For data anlysis, get the number of products for each type, along with the total price, quantity, and price per pound of each type
categories = inventory_df['category'].unique()
keys = ['Category','Number of Products','Total Price','Total Quantity','Price Per Pound']
inventory_categories_dict= dict(zip(keys, ([] for _ in keys)))
for category in categories:
    category_total_price = inventory_df[inventory_df['category']==str(category)]['our_price'].sum()
    category_total_pounds = inventory_df[inventory_df['category']==str(category)]['weight_per_restock'].sum()
    inventory_categories_dict['Category'].append(category)
    inventory_categories_dict['Number of Products'].append(inventory_df['category'].value_counts().get(str(category), 0))
    inventory_categories_dict['Total Price'].append(category_total_price)
    inventory_categories_dict['Total Quantity'].append(category_total_pounds)
    inventory_categories_dict['Price Per Pound'].append(category_total_price/category_total_pounds)

inventory_categories_df = pd.DataFrame({ key:pd.Series(value) for key, value in inventory_categories_dict.items() })

# Extract the sum of all price_per_restock, then divide by the sum of all weight_per_restock to get the total cost per pound.
bvg_earnings_per_month = inventory_df['price_per_restock'].sum()
beverage_quantity = inventory_df['weight_per_restock'].sum()
beverage_earnings_per_pound = bvg_earnings_per_month / beverage_quantity

print('Total local beverage earnings per pound: ${:,.2f}'.format(beverage_earnings_per_pound))

# Now we obtain the global prices per pound (the supply) and extract the coffee prices.

# First, obtain the average prices per pound and extract the coffee prices.
# We're using in2013dollars.com's historical chart data for coffee prices per pound by year.
static_url = "https://www.in2013dollars.com/Beverage-materials-including-coffee-and-tea/price-inflation"
in2013dollars_data  = requests.get(static_url).text

# Alternative data source to check if webscraping is possible: https://www.in2013dollars.com/Other-beverage-materials-including-tea/price-inflation

# Use BeautifulSoup() to create a BeautifulSoup object from a response text content, then verify if the parse ran correctly
in2013dollars_soup = BeautifulSoup(in2013dollars_data, 'html.parser')
print(in2013dollars_soup.title) # To verify whether this works

# Use the find_all function in the BeautifulSoup object with the element type of 'table', then assign the result to a list called 'html_tables'
html_tables = in2013dollars_soup.find_all('table')
in2013dollars_table = html_tables[0]
print(in2013dollars_table.title)

column_names = []

# Apply the find_all() function with 'th' element on products_table
# Iterate each th element and apply the provided extract_column_from_header() to get a column name
# Append the Non-empty column name (`if name is not None and len(name) > 0`) into a list called column_names
column_headers = in2013dollars_table.find_all('th')
for row in column_headers:
    name = extract_column_from_header(row)
    if name is not None and len(name) > 0:
        column_names.append(name)

# print(column_names)

# We will create an empty dictionary with keys from the extracted column names. We can then convert this into a Pandas dataframe
in2013dollars_dict= dict.fromkeys(column_names)

# Initialize the in2013dollars_dict with each value to be an empty list
in2013dollars_dict['Year'] = []
in2013dollars_dict['USD Value'] = []
in2013dollars_dict['Inflation Rate'] = []

for rows in in2013dollars_table.find_all("tr"):
    if rows.th:
        flag = False
    else:
        flag = True
    row=rows.find_all('td')
    # print(row)
    
    if flag:
        year=row[0].get_text()
        # print(crop)
        in2013dollars_dict['Year'].append(int(year))
        
        value=row[1].get_text()
        # print(global_gpv)
        value_num = value.strip('$')
        in2013dollars_dict['USD Value'].append(float(value_num))
        
        inflation_rate = row[2].get_text()
        # print(global_prod)
        inflation_rate_num = inflation_rate.replace('%','').replace('*','')
        if any(chr.isdigit() for chr in inflation_rate_num):
            in2013dollars_dict['Inflation Rate'].append(float(inflation_rate_num))
        else: #To cover the null value for this column in 1997
            in2013dollars_dict['Inflation Rate'].append(0.0)

in2013dollars_df= pd.DataFrame({ key:pd.Series(value) for key, value in in2013dollars_dict.items() })

# print(in2013dollars_df)

# Now, extract the average adjusted price in USD/pound for the year 2024.
beverage_average_price = float(in2013dollars_df.loc[in2013dollars_df['Year']==2024, 'USD Value'])

print('Average beverage price per pound: ${:,.2f}'.format(beverage_average_price))

# Finally, print the report.md file. Remove any previous report.md file first to clear the way for generating a new one.
if os.path.exists('report.md'):
    os.remove('report.md')

with open('report.md', 'a+') as f:
    f.write('# Overview\n\n')
    f.write('This study serves as a comparison between pricing data obtained from our local coffee shop and average pricing data for restaurant-sold coffee in the US. The business insight to be gleaned from this therefore concerns how much the earnings made per year by the shop deviates from the nationwide average per year, which can be used to determine if prices are too high or too low compared to this average as a factor into critical business decisions.\n\n')
    f.write('# Data quality issues and wrangling\n\n')
    f.write('The products.csv file used for this study is stored in the /data directory of this project, and was read into the Python script using Pandas\' read_csv() function. \n\n')
    f.write('Wrangling the data involved reformatting it via the following steps:\n\n')
    f.write('- Refine our_price: Remove any non-numerical signs, then set any non-number value to the currently existing minimum numerical value.\n\n')
    f.write('- Refine current_stock: Set any non-number value to 0.\n\n')
    f.write('- Refine restock_threshold: Set any non-number value to the currently existing minimum numerical value.\n\n')
    f.write('- Refine restock_date: Convert to datetime and remove any rows with a NaN value.\n\n')
    f.write('- Refine category: This depends on product_name. Check if product_name contains certain words, then replace the category. The category is set to \'coffee\' for words such as \'coffee\', \'bean\', and \'brew\', and to \'tea\' for words such as \'tea\', \'matcha\', and \'chai\'.\n\n')
    f.write('# Data summary\n\n')
    f.write('The processed data post-wrangling is shown:\n\n')
    f.write("| Product Name | Our Price | Category | Current Stock | Restock Threshold | Restock Date | Price Per Restock | Weight Per Restock (lbs) |\n")
    f.write("| ----------: | ----------: | ----------: | ----------: | ----------: | ----------: | ----------: | ----------: |\n")
    for index, row in inventory_df.iterrows():
        f.write(f"| {row['product_name']} | {'${:,.2f}'.format(row['our_price'])} | {row['category']} | {row['current_stock']} | {row['restock_threshold']} | {row['restock_date']} | {'${:,.2f}'.format(row['price_per_restock'])} | {row['weight_per_restock']} |\n")
    f.write("\n")
    f.write('The different categories of beverage and the number of products sold under each are as follows:\n\n')
    f.write("| Category | Number of Products | Cumulative Price (USD) Per Pound |\n")
    f.write("| ----------: | ----------: | ----------: |\n")
    for index, row in inventory_categories_df.iterrows():
        f.write(f"| {row['Category']} | {row['Number of Products']} | {'${:,.2f}'.format(row['Price Per Pound'])} |\n")
    f.write("\n")
    f.write('# External data integration\n\n')
    f.write('Our external source is in2013dollars.com\'s free dataset prices of <i>beverage materials including coffee and tea</i> from 1997 to 2024. This will allow us to obtain average annually coffee price in USD per pound. We will select data for the most recent year, in this case 2024 (the most recent full year as of this study).\n\n')
    f.write('Webscraping was done with BeautifulSoup, which enabled extraction of the HTML table and refinement of the external data to remove HTML formatting and preserve the numerical values for the Year, USD Value, and Inflation Rate.\n\n')
    f.write("| Year | USD Value | Inflation Rate |\n")
    f.write("| ----: | ----------: | ----------: |\n")
    for index, row in in2013dollars_df.iterrows():
        f.write(f"| {int(row['Year'])} | {'${:,.2f}'.format(row['USD Value'])} | {'{:,.2f}%'.format(row['Inflation Rate'])} |\n")
    f.write('\n\n')
    f.write('Source URL: https://www.in2013dollars.com/inflation/coffee-prices-by-year-and-adjust-for-inflation/\n\n')
    f.write('# Business insights\n\n')
    f.write('For our economic insight, we compared the total per-pound price of all beverages for this store with the prices per pound per year. This allowed us to determine the difference between the yearly earnings by beverages sold at our shop and the yearly beverage prices per pound. This can be important to know when it comes to determining how to increase customer inflow; if we are above average, customers may not be willing to buy from us as often as with other stores.\n\n')
    f.write('## Inventory earnings per year\n\n')
    f.write('For calculation simplicity, the restock threshold is assumed to indicate how much of each product will be purchased per month, and we will also assume that every single unit we receive is sold before the end of the year.\n\n')
    f.write('To obtain the pound-weight for each item, the numerical quantity per unit is extracted from each product name (column "product_name"). If this number is absent, the product is assumed to be sold at a rate of 1 pound per package.\n\n')
    f.write('Should quantity per unit be present in the product name, it will be converted into pounds per unit; the program checks what unit the item is sold in, and if the amount of an item per package is in pounds then that amount will be used in subsequent calculations as-is. If the item is sold in ounces, the number of ounces per package is divided by 16 to obtain the pounds per package. For tea bags, a pound of tea leaves is assumed to be equivalent to 200 bags, so the amount of bags is divided by 200 to obtain the pound weight. Once the pound-weights per unit for all items are obtained, we multiply the price for each item by its restock threshold to get price per monthly restock, and the pound-weight for each item by its restock threshold to get quantity per monthly restock.\n\n')
    f.write('We then extract the sum of all prices per monthly restock for items in the "coffee" or "tea" categories and multiply this by twelve months to get the total supply price per year for all coffee and tea items put together. Thus, we have:\n\n')
    f.write('Local beverage earnings per pound: <b>${:,.2f}</b>\n\n'.format(beverage_earnings_per_pound))
    f.write('## Average US beverage price per year\n\n')
    f.write('From the webscraped in2013dollars.com dataset, we extract the average coffee and tea price from the year 2024. We then extract the sum of all weights per monthly restock for items in each category and multiply this by both twelve months and to get the total supply price per year for all items of that category. Thus, we have:\n\n')
    f.write('National average price per pound: <b>${:,.2f}</b>\n\n'.format(beverage_average_price))
    f.write('# Future recommendations\n\n')
    f.write('\n\n')
    # markdown.markdownFromFile(input=f, output=dir+'/out.html')
