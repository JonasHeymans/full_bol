# User Accesible methods

## EDC_Client
- EDC_Client.get_xml(): connect to the EDC and store the data into a local XML file
- EDC_Client.get_discounts()
- EDC_Client.get_stock()


## Converter
- Use Converter.initial_convert() to convert the XML file to a pkl file and fix the date format


## Database
- Database.push_discounts_to_db() is also needed so price calculations will be accurate
- Use Database.push_products_to_db() to push this pickle-file to the db
- Use Database.update_stock() to update the stock
- Database.update_prices() (Manual calculation is wrong)
