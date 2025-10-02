import logging
import os
import shutil
import time
import re

import requests

from mainapp.microservice_supplier import EDC_BASE_URL, BB_BASE_URL, BASE_PATH

logger = logging.getLogger('microservice_supplier.edc')


class BaseClient:
    def __init__(self, supplier, api_key=None):
        self.supplier = supplier
        self.api_key = api_key

    def send_request(self, name, url, params):
        logger.debug(f'Sending request for {name}')

        if self.supplier == 'bigbuy':
            request = requests.get(url,
                                   headers={"Authorization": f"Bearer {self.api_key}"},
                                   params=params)

        elif self.supplier == 'edc':
            request = requests.get(url)

        else:
            raise Exception(f'Unknown supplier {self.supplier}')

        return request.text, request.status_code

    def save_to_feeds(self, file, name, page, filetype='xml'):
        if file:
            filename = f'{name}_{str(page).zfill(2)}'
            raw_filename = f'{filename}.{filetype}'
            logger.debug(f'Starting saving of {filetype}')
            path = f'{BASE_PATH}/files/{self.supplier}/feeds/{name}/{raw_filename}'
            with open(path, 'w') as f:
                f.write(file)
                logger.info(f"Successfully saved {filename}")

    def get_file(self, name, url, params):
        if params is None:
            response, status_code = self.send_request(name, url, params=params)


        elif ('pageSize' in params):

            response, status_code = self.send_request(name, url, params=params)

            params['page'] += 1

        else:
            logger.warning(f'Failed to get {name}')
            raise Exception(f'Failed to get {name}')

        return response, status_code, params

    # Please note, this can take a few minutes (around 5 I would say). Maybe async this later?
    def download(self, downloads):
        for row in downloads:
            name = row[0]
            url = row[1]
            filetype = row[2]

            # If row has more than 3 arguments, it's a list of params to pass to the request
            params = row[3] if len(row) > 3 else None


            # - I might be able to write this loop cleaner.
            # - 'status_code = 200'Has to be here instead of as an argument to def download(),
            #  else we persist the status code over the various filenames
            status_code = 200
            while status_code == 200:
                page = params['page'] if params else ''
                response, status_code, params = self.get_file(name, url, params)

                if status_code == 200:
                    self.save_to_feeds(response, name, page, filetype=filetype)

                if params is None:
                    break

            else:
                logger.warning(f'Status code {status_code}')


class EdcClient(BaseClient):
    def __init__(self):
        self.supplier = 'edc'
        self.api_key = os.getenv('EDC_API_KEY')
        self.downloads = {
            'full': [f'{EDC_BASE_URL}b2b_feed.php?key={self.api_key}&sort=xml&type=xml&lang=en&version=2015',
                     'xml'],
            'new': [f'{EDC_BASE_URL}b2b_feed.php?key={self.api_key}&sort=xml&type=xml&lang=en&version=2015&new=1',
                    'xml'],
            'discounts': [f'https://www.erotischegroothandel.nl/download/discountoverview.csv?apikey={self.api_key}',
                          'csv'],
            'stock': [f'{EDC_BASE_URL}xml/eg_xml_feed_stock.xml',
                      'xml'],
            'full_price': [f'https://www.erotischegroothandel.nl/download/priceoverview.csv?apikey={self.api_key}',
                           'csv'],
            'update_price': [f'https://www.erotischegroothandel.nl/download/pricechange.csv?apikey={self.api_key}',
                             'csv']
        }

        super().__init__(self.supplier)

    def download(self, *args):
        args = self.downloads.keys() if args == () else args
        downloads = [[arg] + self.downloads[arg] for arg in args]
        super().download(downloads)


class BigbuyClient(BaseClient):
    def __init__(self):
        self.supplier = 'bigbuy'
        self.api_key = os.getenv('BB_API_KEY')
        self.downloads = {
            'products': [f'{BB_BASE_URL}rest/catalog/products.json?isoCode=NL',
                         'json',
                         {'page': 0, 'pageSize': 9900000}],
            'variants': [f'{BB_BASE_URL}rest/catalog/productsvariations.json?isoCode=NL',
                         'json',
                         {'page': 0,
                          'pageSize': 10000}],
            'productstock': [f'{BB_BASE_URL}rest/catalog/productsstock.json',
                             'json',
                             {'page': 0, 'pageSize': 9900000}],
            'productdescriptions': [f'{BB_BASE_URL}rest/catalog/productsinformation.json?isoCode=NL',
                                    'json',
                                    None],
            'variations': [f'{BB_BASE_URL}rest/catalog/variations.json?isoCode=NL',
                           'json',
                           None],
            'attributes': [f'{BB_BASE_URL}rest/catalog/attributes.json?isoCode=NL',
                           'json',
                           None],
            'attributegroups': [f'{BB_BASE_URL}rest/catalog/attributegroups.json?isoCode=NL',
                                'json',
                                None],
            'stock': [f'{BB_BASE_URL}rest/catalog/productsvariationsstock.json?isoCode=NL',
                      'json',
                      {'page': 0, 'pageSize': 9900000}],
            'categories': [f'{BB_BASE_URL}rest/catalog/categories.json?isoCode=nl', 'json', None],

        }
        super().__init__(self.supplier, self.api_key)

    def download(self, *args):
        args = self.downloads.keys() if args == () else args
        downloads = [[arg] + self.downloads[arg] for arg in args]
        super().download(downloads)
