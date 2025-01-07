# Overview

This study serves as a comparison between pricing data obtained from our local coffee shop and average pricing data for restaurant-sold coffee in the U.S.. The business insight to be gleaned from this therefore concerns how much the earnings made per year by the shop deviates from the nationwide average per year, which can be used to determine if prices are too high or too low compared to this average as a factor into critical business decisions.

# Data quality issues and wrangling

The products.csv file used for this study is stored in the /data directory of this project, and was read into the Python script and stored via Pandas, using its read_csv() function to convert it into a DataFrame object. 

Wrangling the data involved reformatting it via the following steps:

- Refine our_price: Remove any non-numerical signs, then set any non-number value to the currently existing minimum numerical value.

- Refine current_stock: Set any non-number value to 0.

- Refine restock_threshold: Set any non-number value to the currently existing minimum numerical value.

- Refine restock_date: Convert to datetime and remove any rows with a NaN value.

- Refine category: This depends on product_name. Check if product_name contains certain words, then replace the category. The category is set to "coffee" for words such as "coffee", "bean", and "brew", and to "tea" for words such as "tea", "matcha", and "chai".

# Data summary

The processed data post-wrangling is shown:

| Product Name | Our Price | Category | Current Stock | Restock Threshold | Restock Date | Price Per Restock | Weight Per Restock (lbs) |
| ----------: | ----------: | ----------: | ----------: | ----------: | ----------: | ----------: | ----------: |
| Organic Coffee Beans (1lb) | $14.99 | Coffee | 45.0 | 25.0 | 2024-11-15 | $374.75 | 25.0 |
| Premium Green Tea (50 bags) | $8.99 | Tea | 32.0 | 20.0 | 2024-11-10 | $179.80 | 5.0 |
| Masala Chai Mix (12oz) | $9.99 | Tea | 18.0 | 15.0 | 2024-11-18 | $149.85 | 11.25 |
| Yerba Mate Loose Leaf (1lb) | $12.99 | Beverages | 5.0 | 10.0 | 2024-11-01 | $129.90 | 10.0 |
| Hot Chocolate Mix (1lb) | $7.99 | Beverages | 50.0 | 30.0 | 2024-11-12 | $239.70 | 30.0 |
| Earl Grey Tea (100 bags) | $11.99 | Tea | 28.0 | 25.0 | 2024-11-14 | $299.75 | 12.5 |
| Espresso Beans (1lb) | $16.99 | Coffee | 22.0 | 20.0 | 2024-11-16 | $339.80 | 20.0 |
| Chamomile Tea (30 bags) | $6.99 | Tea | 12.0 | 15.0 | 2024-11-05 | $104.85 | 2.25 |
| Matcha Green Tea Powder (4oz) | $19.99 | Tea | 8.0 | 10.0 | 2024-11-17 | $199.90 | 2.5 |
| Decaf Coffee Beans (1lb) | $15.99 | Coffee | 15.0 | 15.0 | 2024-11-13 | $239.85 | 15.0 |
| Mint Tea (25 bags) | $7.49 | Tea | 0.0 | 12.0 | 2024-10-30 | $89.88 | 1.5 |
| Instant Coffee (8oz) | $11.99 | Coffee | 25.0 | 20.0 | 2024-11-19 | $239.80 | 10.0 |
| Rooibos Tea (40 bags) | $6.99 | Tea | 30.0 | 20.0 | 2024-11-08 | $139.80 | 4.0 |
| cold brew concentrate | $13.99 | Coffee | 19.0 | 15.0 | 2024-11-20 | $209.85 | 15.0 |

The different categories of beverage and the number of products sold under each are as follows:

| Category | Number of Products | Cumulative Price (U.S.D.) Per Pound |
| ----------: | ----------: | ----------: |
| Coffee | 5 | $0.87 |
| Tea | 7 | $1.86 |
| Beverages | 2 | $0.52 |

# External data integration

Our external source is in2013dollars.com, and specifically their free dataset of national average prices across all U.S. cities for <i>beverage materials including coffee and tea</i> from 1997 to 2024. This will allow us to obtain the average annual price in U.S.D. for beverages overall. The site is also one of the few such databases that can be freely webscraped and since it cites the U.S. Bureau of Labor Statistics as the source for its data, it can be assumed that said data is reasonably accurate. We will select data for the most recent year, in this case 2024 (the most recent full year as of this study).

Webscraping was done with BeautifulSoup, which enabled extraction of the HTML table and refinement of the external data to remove HTML formatting and preserve the numerical values for the Year, U.S.D. Value, and Inflation Rate.

| Year | U.S.D. Value | Inflation Rate |
| ----: | ----------: | ----------: |
| 1997 | $20.00 | 0.00% |
| 1998 | $19.73 | -1.36% |
| 1999 | $19.35 | -1.90% |
| 2000 | $19.59 | 1.21% |
| 2001 | $19.40 | -0.97% |
| 2002 | $19.26 | -0.70% |
| 2003 | $19.47 | 1.09% |
| 2004 | $19.51 | 0.20% |
| 2005 | $20.48 | 4.99% |
| 2006 | $20.82 | 1.61% |
| 2007 | $21.64 | 3.98% |
| 2008 | $22.56 | 4.21% |
| 2009 | $22.65 | 0.42% |
| 2010 | $22.79 | 0.63% |
| 2011 | $24.49 | 7.45% |
| 2012 | $24.73 | 0.98% |
| 2013 | $23.96 | -3.12% |
| 2014 | $23.77 | -0.79% |
| 2015 | $24.07 | 1.28% |
| 2016 | $23.67 | -1.68% |
| 2017 | $23.66 | -0.05% |
| 2018 | $23.34 | -1.34% |
| 2019 | $23.31 | -0.12% |
| 2020 | $23.55 | 1.02% |
| 2021 | $24.10 | 2.32% |
| 2022 | $26.96 | 11.88% |
| 2023 | $28.37 | 5.21% |
| 2024 | $28.48 | 0.39% |


Source URL: https://www.in2013dollars.com/Beverage-materials-including-coffee-and-tea/price-inflation

# Business insights

For our economic insight, we compared the total per-pound price of all beverages for this store with the prices per pound per year. This allowed us to determine the difference between the yearly earnings by beverages sold at our shop and the yearly beverage prices per pound. This can be important to know when it comes to determining how to increase customer inflow; if we are above average, customers may not be willing to buy from us as often as with other stores.

## Inventory earnings per year

For calculation simplicity, the restock threshold is assumed to indicate how much of each product will be purchased per month, and we will also assume that every single unit we receive is sold before the end of the year.

To obtain the pound-weight for each item, the numerical quantity per unit is extracted from each product name (column "product_name"). If this number is absent, the product is assumed to be sold at a rate of 1 pound per package.

Should quantity per unit be present in the product name, it will be converted into pounds per unit; the program checks what unit the item is sold in, and if the amount of an item per package is in pounds then that amount will be used in subsequent calculations as-is. If the item is sold in ounces, the number of ounces per package is divided by 16 to obtain the pounds per package. For tea bags, a pound of tea leaves is assumed to be equivalent to 200 bags, so the amount of bags is divided by 200 to obtain the pound weight. Once the pound-weights per unit for all items are obtained, we multiply the price for each item by its restock threshold to get price per monthly restock, and the pound-weight for each item by its restock threshold to get quantity per monthly restock.

We then extract the sum of all prices per monthly restock for all items and multiply this by twelve months to get the total supply price per year for all beverage items put together. Thus, we have:

Local beverage earnings per pound: <b>$17.91</b>

Finally, we multiply the monthly beverage earnings by twelve months to get the earnings per year, assuming all stock is sold before the end of the year:

Local beverage earnings per year: <b>$35,249.76</b>

## Average U.S. beverage price per year

For these calculations, assume that the national average is for each pound-unit of any beverage ingredient sold in any U.S. city. From the webscraped in2013dollars.com dataset, we extract the average beverage price from the year 2024 to get:

National average price per pound (2024): <b>$28.48</b>

Multiplying this by the total beverage weight and by twelve months, we obtain the expenses per year if we buy all our beverage ingredients at national average price:

Total expenses based on average ingredient price: <b>$56,048.64</b>

The price at which our goods are sold is thus, on average, below the average price of all beverages in all U.S. cities. However, this would also mean that if we were to buy our inventory at the average national price as per the current rate, we would be at a deficit because even the lowest average beverage price within the last two decades, at $19.26 in 2002, is still over a dollar above our average beverage price.

# Future recommendations

As noted above, on average we sell our beverages at a price below the national average, which has the benefit of attracting customers who would be more interested in saving money by purchasing from a seller whose price offerings are lower, but assuming that we buy inventory strictly at the national average rate, and assuming that rate is per pound of beverage ingredient, we will be facing a deficit of <b>$20,798.88</b> per year (based on the national average in 2024). However, prices for individual beverage ingredients vary in the same way as those of our goods do depending on the type of beverage being purchased. To better match expenses to earnings and potentially turn a profit, we would need to find a choice or selection of vendors for each drink type that offer ingredients at the lowest price possible while still maintaining sufficient ingredient quality (since a higher-quality product will also be good for sales).

The other recommendation for profit increase, assuming lower-price vendors are unavailable and/or quality cannot be sacrificed, would be to offer our goods at higher prices, bringing the average earning price per pound of ingredient closer to the national average. This is more risky if the lower prices are the primary reason for customers wanting to buy from us in the first place, but if we can find higher-quality vendors for ingredients to improve the goods themselves, then the price increase may be worth the additional investment due to better public standing improving business as much as lower prices. However, selecting higher-quality vendors may also run the risk of the expenses being increased in turn due to having to spend more to afford the ingredients they have on offer.

As such, the recommendations are largely dependent on whether or not we can find vendors that offer the same quality of product at a lower cost to us:

- If vendors that sell ingredients of an acceptable quality at lower prices exist, change the vendors to the option that reduces expenses, and potentially increase the restock threshold to offer more of the product to customers.

- If there are no vendors that can provide ingredients below the national average, instead raise the prices of the goods we sell, but also look for vendors that provide higher-quality versions of these items. In this way, we can make a trade-off between attracting customers with our current lower prices and bolstering our PR among the consumer base with higher-quality purchases.

(c) Adrian Tan, 2025

