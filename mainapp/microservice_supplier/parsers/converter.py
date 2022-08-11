import logging
import os
import pickle
import time
import json
from collections import OrderedDict
from datetime import datetime
from typing import List
import pandas as pd
from datetime import datetime as dt
import xmltodict

from mainapp.microservice_supplier import BASE_PATH

logger = logging.getLogger('microservice_supplier.converter')


class Converter:
    def save_pickle(self, file, file_path):
        with open(file_path, 'wb') as f:
            pickle.dump(file, f)
            logger.info(f"Saved file to {file_path}")

    def read_pickle(self, file_path):
        return pickle.load(open(file_path, "rb"))

    def get_all_filenames(self):
        path = f'{BASE_PATH}/files/{self.supplier}/merged/'
        return [filename for filename in os.listdir(path)]


class EdcConverter(Converter):
    def __init__(self, supplier):
        self.supplier = supplier
        self.filenames = super().get_all_filenames()

    def __convert_xml_to_list(self, file_name, xml_attribs=True) -> List:
        with open(f"{BASE_PATH}/files/{self.supplier}/merged/{file_name}.xml", "rb") as f:
            logger.debug('Starting conversion from XML to cleaned')
            start = time.time()
            my_dictionary = xmltodict.parse(f, xml_attribs=xml_attribs)
            logger.debug(f'Conversion from XML to cleaned Successful. Took {(time.time() - start) / 60:.2f} minutes')

            # Check that my_dictionary is not empty
            if bool(my_dictionary['products']):
                return my_dictionary['products']['product']
            else:
                with open(f"{BASE_PATH}/files/various/empty.xml", "rb") as f:
                    return xmltodict.parse(f, xml_attribs=xml_attribs)

    def __convert_json_to_list(self, file_name) -> List:
        path = f"{BASE_PATH}/files/{self.supplier}/merged/{file_name}.json"
        logger.debug('Starting conversion from Json to cleaned')
        start = time.time()
        my_dictionary = json.load(open(path), object_pairs_hook=OrderedDict)
        logger.debug(f'Conversion from JSON to cleaned Successful. Took {(time.time() - start) / 60:.2f} minutes')
        return my_dictionary

    '''Ok, this is like quite dirty... But I needed to do it because for example there can be 1 or 
    more variants for each product, and we don't know beforehand if- and how many variants 
    the product will have. So we just extract the variant OrderedDicts from the products
    OrderedDict and put them into a new list which we later use to parse to a Variant object. 
    '''

    '''
    Do NOT (NOTNOTNOT) use these functions to convert the output from the API to an XML, pickle can't handle this. I
    created these functions to save my cleaned to a file so we wouldn't have to this conversion for every class in parser.
    '''

    # TODO : further expand the convert function so it also can parse the 'values' property of properties.
    # TODO : Maybe the convert and loop-through function need to be merged? I don't see the difference between them.

    def convert(self, file, tablename: str) -> List:
        logger.debug(f'Starting conversion of {tablename}')
        d = {'variants': ['id', 'type', 'subartnr', 'ean', 'stock', 'stockestimate', 'weeknr', 'nova', 'title',
                          'remaining', 'remaining_quantity'],
             'categories': ['id', 'title'],
             'properties': ['propid', 'property', 'valueid', 'value', 'values'],
             'pics': ['pic'],
             'bulletpoints': ['bp']
             }

        if tablename in d.keys():
            keys = d[tablename]

        else:
            logger.warning('invalid name entered in covert function')
            raise Exception("Invalid name entered")

        converted_file = self.__loop_through_products(file, tablename, keys)

        if tablename == 'pics':
            return self.__convert_pics(converted_file)

        if tablename == 'bulletpoints':
            return self.__convert_bulletpoints(converted_file)

        if tablename == 'properties':
            return self.__convert_properties(converted_file)

        logger.debug(f'Converted {tablename}')

        return converted_file

    def __productid_generator(self, file):
        for x in file:
            yield x['id']

    def __loop_through_products(self, file, name, keys) -> List:
        lst = []
        productid_generator = self.__productid_generator(file)
        for x in file:
            d = {}
            d['product_id'] = int(productid_generator.__next__())
            logger.debug(f"Looping through {name} of {d['product_id']}")
            try:
                # Could make this a lot easier by putting it into a cleaned?
                if name == 'variants':
                    x = x['variants']['variant']
                elif name == 'categories':
                    # name = name (Commenting this out since this does not seem to do anything.)
                    x = x['categories']['category']['cat']
                elif name == 'properties':
                    x = x['properties']['prop']
                elif name == 'pics':
                    x = x['pics']
                elif name == 'bulletpoints':
                    x = x['bulletpoints']

            except TypeError as e:
                if str(e) == 'list indices must be integers or slices, not str':
                    logger.warning(f"Could not add {name} of {d['product_id']}, skipping")
                    continue
                else:
                    logger.critical("Something went very wrong in the convert function!")
                    break

            try:
                for key in keys:
                    d[key] = x.pop(key, None)
                lst.append(d)

            except TypeError as e:
                # The first string can probably safly be removed.
                if str(e) == 'pop() takes at most 1 argument (2 given)' or str(
                        e) == "pop expected at most 1 argument, got 2":
                    for y in range(len(x)):
                        f = {}
                        f['product_id'] = d['product_id']
                        try:
                            for key in keys:
                                value = x[y].pop(key, None)
                                f[key] = value
                            lst.append(f)
                        except IndexError:
                            break
                        except TypeError:
                            break
                else:
                    logger.critical("Something went very wrong in the convert function!")
            except AttributeError as e:
                if str(e) == "NoneType' object has no attribute 'pop'":
                    logger.warning(f"Could not add {name} of {d['product_id']}, skipping")
                    continue

        return lst

    def __convert_date_format(self, file):
        logger.info('Converting date format')
        lst = []

        # if we only have one product in new, this function otherwise bigs out
        if not type(file) == list:
            file = [file]
        for x in file:
            d = {}
            for y in x:
                d[y] = x[y]
                if y in ['date', 'modifydate']:
                    if x['date'] == '00-00-0000':
                        x['date'] = '01-01-1900'

                    d[y] = datetime.strptime(x['date'], "%d-%m-%Y").strftime("%Y-%m-%d")

            lst.append(d)
        return lst

    def __convert_bulletpoints(self, file):
        lst = []
        for x in file:
            for y in x['bp']:
                d = {}
                d['product_id'] = x['product_id']
                d['bp'] = y
                lst.append(d)
        return lst

    def __convert_pics(self, file):
        lst = []
        for e in file:
            product_id = e['product_id']
            if e['pic'][0].endswith('.jpg'):
                for x in e["pic"]:
                    d = {}
                    d['product_id'] = product_id
                    d['id'] = e['pic'][0].strip('.jpg')
                    d['pic'] = x
                    lst.append(d)
            else:
                d = {}
                d['id'] = e['pic'].strip('.jpg')
                d['pic'] = e['pic']
        return lst

    # TODO: Still a bug in this function: some values get parsed by character instead of by string, resulting in
    #  single character values for bp. Issue seems to be limited to 32 products though
    #  (select product_id from bulletpoints where length(bp)<2 group by product_id  ;).
    #  But might be the symptom of a larger issue.

    def __convert_properties(self, file):
        lst = []
        for e in file:
            values = e['values']['value']
            if type(values) == list:
                for x in e['values']['value']:
                    d = {}
                    d['product_id'] = e['product_id']
                    d['propid'] = e['propid']
                    d['property'] = e['property']
                    d['valueid'] = e['valueid']
                    d['value'] = e['value']
                    if "id" in x.keys():
                        d['id'] = x['id']
                        d['title'] = x['title']
                    elif "unit" in x.keys():
                        d['unit'] = x['unit']
                        d['magnitude'] = x['magnitude']
                    lst.append(d)
            else:
                d = {}
                d['product_id'] = e['product_id']
                d['propid'] = e['propid']
                d['property'] = e['property']
                d['valueid'] = e['valueid']
                d['value'] = e['value']
                if 'id' in values.keys():
                    d['id'] = values['id']
                    d['title'] = values['title']
                elif 'unit' in values.keys():
                    d['unit'] = values['unit']
                    d['magnitude'] = values['magnitude']
                lst.append(d)
        return lst

    def convert_stock(self, file):
        d1 = {'productid': 'product_id',
              'variantid': 'id',
              'productnr': 'subartnr',
              'ean': 'ean',
              'stock': 'stock',
              'qty': 'stockestimate',
              'week': 'weeknr'}

        lst = []
        for x in range(len(file)):
            x = dict(file[x])

            new = dict((d1[key], value) for (key, value) in x.items())
            new['stock'] = new['stock'].replace('J', 'Y')
            lst.append(new)

        return lst

    # Maybe also add date of change to the cleaned?
    # def convert_prices_setup(self, file):
    #     lst = []
    #     for x in file:
    #         x = cleaned(x)
    #         x = {key: x[key] for key in x.keys() &
    #              {'productid', 'b2b', 'b2c', 'discount', 'your_price', 'artnr'}}
    #         d1 = {'productid': 'product_id', 'b2b': 'b2b', 'b2c': 'b2c', 'artnr': 'artnr',
    #               'discount': 'discount_percentage', 'your_price': 'buy_price'}
    #         new = cleaned((d1[key], value) for (key, value) in x.items())
    #         lst.append(new)
    #
    #     return lst

    def convert_prices(self, file, type):
        lst = []
        for price in file:
            price_dict = dict(price)
            excluded = ['brandname', 'artname', 'type']

            d1 = {'productid': 'id',
                  'artnr': 'artnr',
                  'b2c': 'b2c',
                  'b2b': 'b2b',
                  'discount': 'discount',
                  'your_price': 'b2b',
                  'ean': 'ean',
                  'discount_percentage': 'discount_percentage',
                  'brandid': 'brand_id',
                  'subartnr': 'subartnr',
                  'date': 'update_date',
                  }

            if type == 'update':
                d1['new_price'] = price_dict['type']

            if type == 'setup':
                price_dict['discount_percentage'] = price_dict['discount']
                price_dict['discount'] = 'Y' if price_dict['discount'] else 'N'

            new = dict((d1[key], value) for (key, value) in price_dict.items() if key not in excluded)
            new['price'] = {}
            new['brand'] = {}

            for x in ['discount', 'b2c', 'b2b', 'brand_id', ]:
                if x in new.keys():
                    if x == 'brand_id':
                        new['brand'][x] = new.pop(x)
                    else:
                        new['price'][x] = new.pop(x)
                        if x == 'b2b':
                            new['price']['b2bsale'] = new['price']['b2b']

            lst.append(new)

        return lst

    def initial_convert(self, *args):
        filenames = self.filenames if args == () else args
        for filename in filenames:
            name, extention = filename.split('.')
            # kinda dirty, might want to clean this up later
            if extention == 'csv':
                continue
            elif name == 'stock':
                with open(f"{BASE_PATH}/files/{self.supplier}/merged/{name}.xml", "rb") as f:
                    file = xmltodict.parse(f, xml_attribs=True)
            elif extention == 'xml':
                file = self.__convert_xml_to_list(name)
                file = self.__convert_date_format(file)
            elif extention == 'json':
                file = self.__convert_json_to_list(name)
                file = self.__convert_date_format(file)
            else:
                raise Exception("Extension not known")

            super().save_pickle(file, f"{BASE_PATH}/files/{self.supplier}/cleaned/{name}.pkl")


class BigbuyConverter(Converter):

    def __init__(self):
        self.supplier = 'bigbuy'
        self.filenames = super().get_all_filenames()

    def get_df(self, name, extention):
        path = f"{BASE_PATH}/files/{self.supplier}/merged/{name}.{extention}"
        df = pd.read_json(path)

        if name == 'products':
            descriptions_path = f"{BASE_PATH}/files/{self.supplier}/merged/productdescriptions.json"
            categories_path = f"{BASE_PATH}/files/{self.supplier}/merged/categories.json"

            desc_df = pd.read_json(descriptions_path)[['sku', 'name']]
            cat_df = pd.read_json(categories_path)[['id', 'name']]

            cat_df.rename(columns={'id': 'category_id', 'name': 'category'}, inplace=True)
            df.rename(columns={'category': 'category_id'}, inplace=True)

            df = pd.merge(desc_df, df, on='sku')
            df = pd.merge(cat_df, df,on='category_id')

        if name == 'variants':
            stock_path = f"{BASE_PATH}/files/{self.supplier}/merged/stock.json"
            stock_df = pd.read_json(stock_path)

            stock_df['stock'] = [x[0]['quantity'] for x in stock_df['stocks']]
            stock_df['update_date_stock'] = dt.now()

            df = pd.merge(stock_df, df, on=['sku', 'id'])

        return df

    def convert(self, df, filename: str):
        if filename == 'products':
            return self.convert_products(df)
        elif filename == 'variants':
            return self.convert_variants(df)

    def convert_products(self, df):

        # renaming some cols
        df = df.rename(columns={'sku': 'artnr'})

        # Dropping irrelevant cols
        df = df[['id', 'artnr', 'name', 'category']]

        return df.to_dict('records')

    def convert_variants(self, df):

        # renaming some cols
        df = df.rename(columns={'sku': 'artnr',
                                'ean13': 'ean',
                                'product': 'product_id',
                                'wholesalePrice': 'purchaseprice',
                                })

        # Dropping irrelevant cols
        df = df[['id', 'artnr', 'ean', 'product_id', 'purchaseprice', 'stock', 'update_date_stock']]

        return df.to_dict('records')

    def initial_convert(self, *args):
        filenames = self.filenames if args == () else args
        for filename in filenames:
            name, extention = filename.split('.')

            df = self.get_df(name, extention)

            file = self.convert(df, name)

            super().save_pickle(file, f"{BASE_PATH}/files/{self.supplier}/cleaned/{name}.pkl")
