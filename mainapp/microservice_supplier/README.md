# General notes

- "update" only updates if the record exists in the db, else it skips
- "merge" overwrites if the record already exists, and else it adds it
- "fill' errors if the record already exists, and else it adds it

# User Accesible methods

## EDC_Client

- download_products(): connect to the EDC and store the data into a local XML file
- download_discounts()
- download_stock()
- download_prices()

## Converter

- Use initial_convert() to convert the XML file to a pkl file and fix the date format

## Database

- add_discounts() is also needed so price calculations will be accurate
- Use add_products() to push this pickle-file to the db
- Use add_stock() to update the stock
- add_full_prices() initial setup
- add_new_prices() (Manual calculation is wrong)
