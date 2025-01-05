import markdown
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
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

# For our economic insight, we will be comparing the total per-pound price of coffee, tea, etc. for this store per year with the global price per pound per year.
# This will allow us to determine the difference between the yearly earnings by our shop and the global expenses per year,
# which could indicate whether a profit is being made by our shop based on the amount of goods it needs per year.
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

# Extract the sum of all price_per_restock where category = coffee, then multiply by 12 months to get the total cost per year. Then do the same with category = tea.
coffee_earnings = inventory_df[inventory_df['category']=='coffee']['price_per_restock'].sum() * 12
tea_earnings = inventory_df[inventory_df['category']=='tea']['price_per_restock'].sum() * 12

print('Coffee earnings per year: ${:,.2f}'.format(coffee_earnings))
print('Tea earnings per year: ${:,.2f}'.format(tea_earnings))

# Now we obtain the global prices per pound (the supply) and extract the coffee and tea prices.

# Read the CSV file from the data folder
file_path_qv = os.path.join(script_dir, '../data/FAOSTAT_data_en_QV_2022.csv')
file_path_qcl = os.path.join(script_dir, '../data/FAOSTAT_data_en_QCL_2022.csv')
qv_df = pd.read_csv(file_path_qv)
qcl_df = pd.read_csv(file_path_qcl)

# Now, get the global production in USD/metric ton for coffee and tea, and for each, convert it to USD/pound.
coffee_production_price = float(qv_df.loc[qv_df['Item'].str.contains('coffee', case=False), 'Value']) * 1000
coffee_production_quantity = float(qcl_df.loc[qcl_df['Item'].str.contains('coffee', case=False), 'Value']) * 2204.62

tea_production_price = float(qv_df.loc[qv_df['Item'].str.contains('tea', case=False), 'Value']) * 1000
tea_production_quantity = float(qcl_df.loc[qcl_df['Item'].str.contains('tea', case=False), 'Value']) * 2204.62

coffee_production_per_pound = coffee_production_price/coffee_production_quantity
tea_production_per_pound = tea_production_price/tea_production_quantity

# Extract the sum of all weight_per_restock where category = coffee and multiply this by coffee_production_per_pound to get the expenses.
# Then do the same with category = tea.
coffee_expenses = inventory_df[inventory_df['category']=='coffee']['weight_per_restock'].sum() * 12 * coffee_production_per_pound
tea_expenses = inventory_df[inventory_df['category']=='tea']['weight_per_restock'].sum() * 12 * tea_production_per_pound

print('Coffee expenses per year: ${:,.2f}'.format(coffee_expenses))
print('Tea expenses per year: ${:,.2f}'.format(tea_expenses))

# Finally, print the report.md file. Remove any previous report.md file first to clear the way for generating a new one.
if os.path.exists('report.md'):
    os.remove('report.md')
  
with open('report.md', 'a+') as f:
    f.write('# Overview\n')
    f.write('This study serves as a comparison between pricing data obtained from our local coffee shop and global pricing data for goods the shop would require. The business insight to be gleaned from this therefore concerns whether the earnings made per year by the shop would be enough to recoup the expenses required to have coffee and tea delivered, shipped, and/or imported to the shop to serve as inventory stock.\n')
    f.write('# Data quality issues and wrangling\n')
    f.write('The products.csv file used for this study is stored in the /data directory of this project, and was read into the Python script using Pandas'' read_csv() function. \n')
    f.write('# Data summary\n')
    f.write('\n')
    f.write('# External data integration\n')
    f.write('Our external source is FAOstat''s free agricultural production dataset. This will allow us to obtain productivity for both coffee and tea in USD per metric ton, which we can convert to USD per pound. We will select data for just one year, in this case 2022.\n')
    f.write('Webscraping attempts with BeautifulSoup resulted in the HTML showing no tables at all due to the tables being represented as widgets for the sake of user-input filtering, so the CSV format of the data had to be manually downloaded. The CSVs were stored in the /data directory of this project, and as with the products.csv file they were read into the Python script using Pandas'' read_csv() function.\n')
    f.write('The price per year for both coffee and tea is assumed to be static from year to year, and that we purchase all coffee and tea products at the same price, which is the global price per year.\n')
    f.write('- Price URL: https://www.fao.org/faostat/en/#data/QV?regions=5000&elements=57&items=656,667&years=2022&output_type=table&file_type=csv&submit=true\n')
    f.write('- Quantity URL: https://www.fao.org/faostat/en/#data/QV?regions=5000&elements=57&items=656,667&years=2022&output_type=table&file_type=csv&submit=true\n')
    f.write('# Business insights\n')
    f.write('For our economic insight, we compared the total per-pound price of coffee, tea, etc. for this store per year with the global price per pound per year. This allowed us to determine the difference between the yearly earnings by our shop and the global supply price per year, which could indicate whether a profit is being made by our shop based on the amount of goods it needs per year.\n')
    f.write('## Inventory earnings per year\n')
    f.write('For calculation simplicity, the restock threshold is assumed to indicate how much of each product will be purchased per month, and we will also assume that every single unit we receive is sold before the end of the year.\n')
    f.write('To obtain the pound-weight for each item, the numerical quantity per unit is extracted from each product name (column "product_name"). If this number is absent, the product is assumed to be sold at a rate of 1 pound per package.\n')
    f.write('Should quantity per unit be present in the product name, it will be converted into pounds per unit; the program checks what unit the item is sold in, and if the amount of an item per package is in pounds then that amount will be used in subsequent calculations as-is. If the item is sold in ounces, the number of ounces per package is divided by 16 to obtain the pounds per package. For tea bags, a pound of tea leaves is assumed to be equivalent to 200 bags, so the amount of bags is divided by 200 to obtain the pound weight. Once the pound-weights per unit for all items are obtained, we multiply the price for each item by its restock threshold to get price per monthly restock, and the pound-weight for each item by its restock threshold to get quantity per monthly restock.\n')
    f.write('We then extract the sum of all prices per monthly restock for items in the "coffee" category and multiply this by twelve months to get the total supply price per year for all coffee items. Then we do the same with all items in the "tea" category. Thus, we have:\n')
    f.write('- Coffee earnings per year: <b>${:,.2f}</b>\n'.format(coffee_earnings))
    f.write('- Tea earnings per year: <b>${:,.2f}</b>\n'.format(tea_earnings))
    f.write('## Restock expenses per year\n')
    f.write('From the FAOSTAT data CSVs, we extract QV and multiply it by 1000 for each item type (coffee and tea) to obtain the total global production value (which is in thousands of USD), and extract QCL and multiply it by 2204.62 to obtain global production amount (converting from metric tons to pounds). Dividing global production value by global production amount for each item type gives us the price per pound for that item, assuming all varieties of that item cost the same to buy regardless of where they came from.\n')
    f.write('We then extract the sum of all weights per monthly restock for items in each category and multiply this by both twelve months and to get the total supply price per year for all items of that category. Thus, we have:\n')
    f.write('- Coffee expenses per year: <b>${:,.2f}</b>\n'.format(coffee_expenses))
    f.write('- Tea expenses per year: <b>${:,.2f}</b>\n'.format(tea_expenses))
    f.write('# Future recommendations\n')
    f.write('\n')
    # markdown.markdownFromFile(input=f, output=dir+'/out.html')
