import logging
from datetime import datetime
import time
import xmltodict
import pickle
from typing import List

from microservice_edc_pull.constants.save_locations import RAW_PATH,CONVERTED_FILE_PATH


logger = logging.getLogger('microservice_edc_pull.converter')


class Converter:

    @classmethod
    def __convert_xml_to_list(cls, xml_file_name, xml_attribs=True) -> List:
        with open(f"{RAW_PATH}{xml_file_name}.xml", "rb") as f:
            logger.debug('Starting conversion from XML to dict')
            start = time.time()
            my_dictionary = xmltodict.parse(f, xml_attribs=xml_attribs)
            logger.debug(f'Conversion from XML to dict Successful. Took {time.time() - start:.2f} seconds')
            return my_dictionary['products']['product']

    '''Ok, this is like quite dirty... But I needed to do it because for example there can be 1 or 
    more variants for each product, and we don't know beforehand if- and how many variants 
    the product will have. So we just extract the variant OrderedDicts from the products
    OrderedDict and put them into a new list which we later use to parse to a Variant object. 
    '''

    '''
    Do NOT (NOTNOTNOT) use these functions to convert the output from the API to an XML, pickle can't handle this. I
    created these functions to save my dict to a file so we wouldn't have to this conversion for every class in parser.
    '''

    @classmethod
    def __save_pickle(cls,file, file_path):
        with open(file_path, 'wb') as f:
            pickle.dump(file, f)
            logger.info(f"Saved file to {file_path}")

        # with open(file_path, 'w') as f:
        #     f.write(str(file))



    # TODO : further expand the convert function so it also can parse the 'values' property of properties.
    # TODO : Maybe the convert and loop-through function need to be merged? I don't see the difference between them.

    @classmethod
    def convert(cls, file, tablename:str) -> List:
        logger.debug(f'Starting conversion of {tablename}')
        d = {'variants': ['id', 'type', 'subartnr', 'ean', 'stock', 'stockestimate','weeknr','nova', 'title','remaining','remaining_quantity'],
             'categories': ['id', 'title'],
             'properties': ['propid', 'property', 'valueid','value', 'values'],
             'pics': ['pic'],
             'bulletpoints': ['bp']
             }

        if tablename in d.keys():
            keys = d[tablename]

        else:
            logger.warning('invalid name entered in covert function')
            raise Exception("Invalid name entered")

        converted_file = cls.__loop_through_products(file, tablename, keys)

        if tablename == 'pics':
            return cls.__convert_pics(converted_file)

        if tablename =='bulletpoints':
            return cls.__convert_bulletpoints(converted_file)

        if tablename =='properties':
            return cls.__convert_properties(converted_file)


        logger.debug(f'Converted {tablename}')


        return converted_file

    @classmethod
    def __productid_generator(cls, file):
        for x in file:
            yield x['id']
            yield x['id']

    @classmethod
    def __loop_through_products(cls, file, name, keys) -> List:
        lst = []
        productid_generator = cls.__productid_generator(file)
        for x in file:
            d = {}
            d['product_id'] = int(productid_generator.__next__())
            logger.debug(f"Looping through {name} of {d['product_id']}")
            try:
                if name == 'variants':
                    x = x['variants']['variant']
                elif name == 'categories':
                    name = name
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
                if str(e) == 'pop() takes at most 1 argument (2 given)':
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

    @classmethod
    def __convert_date_format(cls, file):
        logger.info('Converting date format')
        lst = []
        for x in file:
            d = {}
            for y in x:
                d[y] = x[y]
                if y in ['date', 'modifydate']:
                    d[y] = datetime.strptime(x['date'], "%d-%m-%Y").strftime("%Y-%m-%d")
            lst.append(d)
        return lst

    @classmethod
    def __convert_bulletpoints(cls, file):
        lst = []
        for x in file:
            for y in x['bp']:
                d = {}
                d['product_id'] = x['product_id']
                d['bp'] = y
                lst.append(d)
        return lst

    @classmethod
    def __convert_pics(cls,file):
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
    
    @classmethod
    def __convert_properties(cls,file):
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
                    d['id']= values['id']
                    d['title']= values['title']
                elif 'unit' in values.keys():
                    d['unit'] = values['unit']
                    d['magnitude'] = values['magnitude']
                lst.append(d)
        return lst


    @classmethod
    def convert_stock(cls,file):
        lst = []
        for x in range(len(file)):
            x = dict(file[x])
            d1 = {'productid': 'product_id', 'variantid': 'variant_id', 'productnr': 'subartnr', 'ean': 'ean',
                  'stock': 'stock', 'qty': 'stockestimate','week':'weeknr'}
            new = dict((d1[key], value) for (key, value) in x.items())
            new['stock'] = new['stock'].replace('J', 'Y')
            lst.append(new)

        return lst

    # Maybe also add date of change to the dict?
    @classmethod
    def convert_prices_setup(cls, file):
        lst = []
        for x in file:
            x = dict(x)
            x = {key: x[key] for key in x.keys() &
                 {'productid', 'b2b', 'b2c','discount','your_price','artnr'}}
            d1 = {'productid': 'product_id', 'b2b':'b2b','b2c':'b2c', 'artnr':'artnr',
                  'discount':'discount_percentage', 'your_price':'buy_price'}
            new = dict((d1[key], value) for (key, value) in x.items())
            lst.append(new)

        return lst

    @classmethod
    def convert_prices(cls, file):
        lst = []
        for x in file:
            x = dict(x)
            x = {key: x[key] for key in x.keys() &
                 {'artnr', 'date', 'new_price','discount'}}
            d1 = {'artnr': 'artnr', 'date':'update_date',
                  'discount':'discount', 'new_price':'buy_price'}
            new = dict((d1[key], value) for (key, value) in x.items())
            lst.append(new)

        return lst


    @classmethod
    def initial_convert(cls, filename):

        #kinda dirty, might want to clean this up later
        if filename == 'stock':
            with open(f"{RAW_PATH}{filename}.xml", "rb") as f:
                file = xmltodict.parse(f, xml_attribs=True)
        else:
            file = cls.__convert_xml_to_list(filename)
            file = Converter.__convert_date_format(file)

        cls.__save_pickle(file, f"{CONVERTED_FILE_PATH}{filename}.pkl")
        return file