from bs4 import BeautifulSoup
import markdown
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import requests
import seaborn as sns
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

# Extract the sum of all price_per_restock, then multiply by 12 months to get the total cost per year.
#coffee_earnings = inventory_df[inventory_df['category']=='coffee']['price_per_restock'].sum()
#tea_earnings = inventory_df[inventory_df['category']=='coffee']['price_per_restock'].sum()
#beverage_earnings = (coffee_earnings + tea_earnings) * 12
bvg_earnings_per_month = inventory_df['price_per_restock'].sum()
beverage_earnings = bvg_earnings_per_month * 12

print('Local beverage earnings per year: ${:,.2f}'.format(beverage_earnings))

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

print(in2013dollars_df)

# Now, extract the average adjusted price in USD/pound for the year 2024.
beverage_average_price = float(in2013dollars_df.loc[in2013dollars_df['Year']==2024, 'USD Value'])

# Extract the sum of all weight_per_restock from inventory_df, and multiply this by 12 months and then by beverage_average_price to get the annual expenses.
# coffee_quantity = inventory_df[inventory_df['category']=='coffee']['weight_per_restock'].sum()
# tea_quantity = inventory_df[inventory_df['category']=='coffee']['weight_per_restock'].sum()
# beverage_expenses = (coffee_quantity + tea_quantity) * 12 * beverage_average_price
beverage_quantity = inventory_df['weight_per_restock'].sum()
beverage_average = beverage_quantity * 12 * beverage_average_price

print('Total beverage price per year: ${:,.2f}'.format(beverage_average))

# Finally, print the report.md file. Remove any previous report.md file first to clear the way for generating a new one.
if os.path.exists('report.md'):
    os.remove('report.md')
  
with open('report.md', 'a+') as f:
    f.write('# Overview\n')
    f.write('This study serves as a comparison between pricing data obtained from our local coffee shop and average pricing data for restaurant-sold coffee in the US. The business insight to be gleaned from this therefore concerns how much the earnings made per year by the shop deviates from the nationwide average per year, which can be used to determine if prices are too high or too low compared to this average as a factor into critical business decisions.\n')
    f.write('# Data quality issues and wrangling\n')
    f.write('The products.csv file used for this study is stored in the /data directory of this project, and was read into the Python script using Pandas'' read_csv() function. \n')
    f.write('# Data summary\n')
    f.write('\n')
    f.write('# External data integration\n')
    f.write('Our external source is in2013dollars.com''s free dataset prices of <i>beverage materials including coffee and tea</i> from 1997 to 2024. This will allow us to obtain average annually coffee price in USD per pound. We will select data for the most recent year, in this case 2024 (the most recent full year as of this study).\n')
    f.write('Webscraping was done with BeautifulSoup, which enabled extraction of the HTML table and refinement of the external data to remove HTML formatting and preserve the numerical values for the year, Value (both normal and adjusted for inflation), and Inflation Rate.\n')
    f.write('The price per year for coffee is assumed to be static from year to year.\n')
    f.write('Source URL: https://www.in2013dollars.com/inflation/coffee-prices-by-year-and-adjust-for-inflation/\n')
    f.write('# Business insights\n')
    f.write('For our economic insight, we compared the total per-pound price of both coffee and tea for this store per year with the average price per pound per year. This allowed us to determine the difference between the yearly earnings by coffee sold at our shop and the average price per year for both types, which could indicate whether we are above or below the national average and to what extent. This can be important to know when it comes to determining how to increase customer inflow; if we are above average, customers may not be willing to buy from us as often as with other stores.\n')
    f.write('## Inventory earnings per year\n')
    f.write('For calculation simplicity, the restock threshold is assumed to indicate how much of each product will be purchased per month, and we will also assume that every single unit we receive is sold before the end of the year.\n')
    f.write('To obtain the pound-weight for each item, the numerical quantity per unit is extracted from each product name (column "product_name"). If this number is absent, the product is assumed to be sold at a rate of 1 pound per package.\n')
    f.write('Should quantity per unit be present in the product name, it will be converted into pounds per unit; the program checks what unit the item is sold in, and if the amount of an item per package is in pounds then that amount will be used in subsequent calculations as-is. If the item is sold in ounces, the number of ounces per package is divided by 16 to obtain the pounds per package. For tea bags, a pound of tea leaves is assumed to be equivalent to 200 bags, so the amount of bags is divided by 200 to obtain the pound weight. Once the pound-weights per unit for all items are obtained, we multiply the price for each item by its restock threshold to get price per monthly restock, and the pound-weight for each item by its restock threshold to get quantity per monthly restock.\n')
    f.write('We then extract the sum of all prices per monthly restock for items in the "coffee" or "tea" categories and multiply this by twelve months to get the total supply price per year for all coffee and tea items put together. Thus, we have:\n')
    f.write('Total local beverage earnings per year: <b>${:,.2f}</b>\n'.format(beverage_earnings))
    f.write('## Average coffee price per year\n')
    f.write('From the webscraped in2013dollars.com dataset, we extract the average coffee and tea price from the year 2024. We then extract the sum of all weights per monthly restock for items in each category and multiply this by both twelve months and to get the total supply price per year for all items of that category. Thus, we have:\n')
    f.write('Total national average price per year: <b>${:,.2f}</b>\n'.format(beverage_average))
    f.write('# Future recommendations\n')
    f.write('\n')
    # markdown.markdownFromFile(input=f, output=dir+'/out.html')
