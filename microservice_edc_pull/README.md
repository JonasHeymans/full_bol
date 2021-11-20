# User Accesible methods

## EDC_Client

- download_products(): connect to the EDC and store the data into a local XML file
- download_discounts()
- download_stock()
- download_prices()


## Converter
- Use initial_convert() to convert the XML file to a pkl file and fix the date format


## Database
- push_discounts_to_db() is also needed so price calculations will be accurate
- Use push_products_to_db() to push this pickle-file to the db
- Use push_stock_to_db() to update the stock
- push_prices_to_db() (Manual calculation is wrong)
