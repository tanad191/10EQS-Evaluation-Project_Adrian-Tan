# Overview
This study serves as a comparison between pricing data obtained from our local coffee shop and global pricing data for goods the shop would require. The business insight to be gleaned from this therefore concerns whether the earnings made per year by the shop would be enough to recoup the expenses required to have coffee and tea delivered, shipped, and/or imported to the shop to serve as inventory stock.
# Data quality issues and wrangling
The products.csv file used for this study is stored in the /data directory of this project, and was read into the Python script using Pandas read_csv() function. 
# Data summary

# External data integration
Our external source is FAOstats free agricultural production dataset. This will allow us to obtain productivity for both coffee and tea in USD per metric ton, which we can convert to USD per pound. We will select data for just one year, in this case 2022.
Webscraping attempts with BeautifulSoup resulted in the HTML showing no tables at all due to the tables being represented as widgets for the sake of user-input filtering, so the CSV format of the data had to be manually downloaded. The CSVs were stored in the /data directory of this project, and as with the products.csv file they were read into the Python script using Pandas read_csv() function.
The price per year for both coffee and tea is assumed to be static from year to year, and that we purchase all coffee and tea products at the same price, which is the global price per year.
- Price URL: https://www.fao.org/faostat/en/#data/QV?regions=5000&elements=57&items=656,667&years=2022&output_type=table&file_type=csv&submit=true
- Quantity URL: https://www.fao.org/faostat/en/#data/QV?regions=5000&elements=57&items=656,667&years=2022&output_type=table&file_type=csv&submit=true
# Business insights
For our economic insight, we compared the total per-pound price of coffee, tea, etc. for this store per year with the global price per pound per year. This allowed us to determine the difference between the yearly earnings by our shop and the global supply price per year, which could indicate whether a profit is being made by our shop based on the amount of goods it needs per year.
## Inventory earnings per year
For calculation simplicity, the restock threshold is assumed to indicate how much of each product will be purchased per month, and we will also assume that every single unit we receive is sold before the end of the year.
To obtain the pound-weight for each item, the numerical quantity per unit is extracted from each product name (column "product_name"). If this number is absent, the product is assumed to be sold at a rate of 1 pound per package.
Should quantity per unit be present in the product name, it will be converted into pounds per unit; the program checks what unit the item is sold in, and if the amount of an item per package is in pounds then that amount will be used in subsequent calculations as-is. If the item is sold in ounces, the number of ounces per package is divided by 16 to obtain the pounds per package. For tea bags, a pound of tea leaves is assumed to be equivalent to 200 bags, so the amount of bags is divided by 200 to obtain the pound weight. Once the pound-weights per unit for all items are obtained, we multiply the price for each item by its restock threshold to get price per monthly restock, and the pound-weight for each item by its restock threshold to get quantity per monthly restock.
We then extract the sum of all prices per monthly restock for items in the "coffee" category and multiply this by twelve months to get the total supply price per year for all coffee items. Then we do the same with all items in the "tea" category. Thus, we have:
- Coffee earnings per year: $16,848.60
- Tea earnings per year: $13,965.96
## Restock expenses per year
From the FAOSTAT data CSVs, we extract QV and multiply it by 1000 for each item type (coffee and tea) to obtain the total global production value (which is in thousands of USD), and extract QCL and multiply it by 2204.62 to obtain global production amount (converting from metric tons to pounds). Dividing global production value by global production amount for each item type gives us the price per pound for that item, assuming all varieties of that item cost the same to buy regardless of where they came from.
We then extract the sum of all weights per monthly restock for items in each category and multiply this by both twelve months and to get the total supply price per year for all items of that category. Thus, we have:
- Coffee expenses per year: $924.41
- Tea expenses per year: $491.27
# Future recommendations

