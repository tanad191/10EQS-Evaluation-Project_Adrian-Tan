# Overview
This study serves as a comparison between pricing data obtained from our local coffee shop and average pricing data for restaurant-sold coffee in the US. The business insight to be gleaned from this therefore concerns how much the earnings made per year by the shop deviates from the nationwide average per year, which can be used to determine if prices are too high or too low compared to this average as a factor into critical business decisions.
# Data quality issues and wrangling
The products.csv file used for this study is stored in the /data directory of this project, and was read into the Python script using Pandas read_csv() function. 
# Data summary

# External data integration
Our external source is in2013dollars.coms free dataset prices of <i>beverage materials including coffee and tea</i> from 1997 to 2024. This will allow us to obtain average annually coffee price in USD per pound. We will select data for the most recent year, in this case 2024 (the most recent full year as of this study).
Webscraping was done with BeautifulSoup, which enabled extraction of the HTML table and refinement of the external data to remove HTML formatting and preserve the numerical values for the year, Value (both normal and adjusted for inflation), and Inflation Rate.
The price per year for coffee is assumed to be static from year to year.
Source URL: https://www.in2013dollars.com/inflation/coffee-prices-by-year-and-adjust-for-inflation/
# Business insights
For our economic insight, we compared the total per-pound price of both coffee and tea for this store per year with the average price per pound per year. This allowed us to determine the difference between the yearly earnings by coffee sold at our shop and the average price per year for both types, which could indicate whether we are above or below the national average and to what extent. This can be important to know when it comes to determining how to increase customer inflow; if we are above average, customers may not be willing to buy from us as often as with other stores.
## Inventory earnings per year
For calculation simplicity, the restock threshold is assumed to indicate how much of each product will be purchased per month, and we will also assume that every single unit we receive is sold before the end of the year.
To obtain the pound-weight for each item, the numerical quantity per unit is extracted from each product name (column "product_name"). If this number is absent, the product is assumed to be sold at a rate of 1 pound per package.
Should quantity per unit be present in the product name, it will be converted into pounds per unit; the program checks what unit the item is sold in, and if the amount of an item per package is in pounds then that amount will be used in subsequent calculations as-is. If the item is sold in ounces, the number of ounces per package is divided by 16 to obtain the pounds per package. For tea bags, a pound of tea leaves is assumed to be equivalent to 200 bags, so the amount of bags is divided by 200 to obtain the pound weight. Once the pound-weights per unit for all items are obtained, we multiply the price for each item by its restock threshold to get price per monthly restock, and the pound-weight for each item by its restock threshold to get quantity per monthly restock.
We then extract the sum of all prices per monthly restock for items in the "coffee" or "tea" categories and multiply this by twelve months to get the total supply price per year for all coffee and tea items put together. Thus, we have:
Total local beverage earnings per year: <b>$35,249.76</b>
## Average coffee price per year
From the webscraped in2013dollars.com dataset, we extract the average coffee and tea price from the year 2024. We then extract the sum of all weights per monthly restock for items in each category and multiply this by both twelve months and to get the total supply price per year for all items of that category. Thus, we have:
Total national average price per year: <b>$56,048.64</b>
# Future recommendations

