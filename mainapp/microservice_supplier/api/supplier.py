import logging
import time
import json
import os
import shutil
import re

import requests
from decouple import config

from mainapp.microservice_supplier import EDC_BASE_URL, BB_BASE_URL, BASE_PATH

logger = logging.getLogger('microservice_supplier.edc')


class BaseClient:
    def __init__(self, supplier, api_key=None):
        self.supplier = supplier
        self.api_key = api_key

    def send_request(self, name, url, params):
        logger.info(f'Sending request for {name}')

        if self.supplier == 'bigbuy':
            request = requests.get(url,
                                   headers={"Authorization": f"Bearer {self.api_key}"},
                                   params=params)

        elif self.supplier == 'edc':
            request = requests.get(url)

        return request.text, request.status_code

    def save_to_feeds(self, file, name, page='', filetype='xml'):
        if file:
            filename = f'{name}_{page}.{filetype}'
            logger.info(f'Starting saving of {filetype}')
            with open(f'{BASE_PATH}/files/{self.supplier}/feeds/{name}/{filename}', 'w') as f:
                f.write(file)
                logger.info(f"Successfully saved {filename}")

    # def merge_json(self, json1, json2):
    #     if json1:
    #         lstA = json.loads(json1)
    #         lstB = json.loads(json2)
    #         merged_lst = lstA + lstB
    #         return json.dumps(merged_lst)
    #     else:
    #         return json2

    def get_file(self, name, url, params, response=''):
        if params is None:
            response, status_code = self.send_request(name, url, params=params)

        elif 'page' in params:
            response = response if response else ''
            status_code = 200
            while status_code == 200:
                partial_response, status_code = self.send_request(name, url, params=params)
                if status_code == 200:
                    params['page'] += 1
                    self.save_to_feeds(partial_response, name, params["page"], filetype='json')
                    logger.info(f'Got {name} page {params["page"]}')
                elif status_code == 404:
                    status_code = 200
                    response = str(response)
                    break
        else:
            logger.warning(f'Failed to get {name}')
            raise Exception(f'Failed to get {name}')

        return response, status_code, params


    def empty_directory(self, name):
        dir = f'{BASE_PATH}/files/{self.supplier}/feeds/{name}'
        shutil.rmtree(dir, ignore_errors=False, onerror=None)
        os.mkdir(dir)
        open(f'{dir}/.gitkeep', 'a').close()

    # Please note, this can take a few minutes (around 5 I would say). Maybe async this later?
    def download(self, downloads):
        for row in downloads:
            name = row[0]
            url = row[1]
            filetype = row[2]
            params = row[3] if len(row) > 3 else None

            self.empty_directory(name)

            response, status_code, params = self.get_file(name, url, params)

            if status_code == 200:
                self.save_to_feeds(response, name, filetype=filetype)
            elif status_code == 429:
                logger.info("Sleeping because of timeout")
                time.sleep(60 * 61)
                logger.info("Woke up")
                response, status_code, params = self.get_file(name, url, params, response)
                self.save_to_feeds(response, name, filetype=filetype)
            else:
                logger.warning(f'Status code {status_code}')

            logger.info(f'Merging {name}')


class EdcClient(BaseClient):
    def __init__(self):
        self.supplier = 'edc'
        self.api_key = config('EDC_API_KEY')
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
        self.api_key = config('BB_API_KEY')
        self.downloads = {
            'products': [f'{BB_BASE_URL}rest/catalog/products.json?isoCode=NL',
                         'json',
                         {'pageSize': 10000,
                          'page': 0}],
            'variants': [f'{BB_BASE_URL}rest/catalog/productsvariations.json?isoCode=NL',
                         'json',
                         {'pageSize': 10000,
                          'page': 0}],
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
                      None],
            'categories': [f'{BB_BASE_URL}rest/catalog/categories.json?isoCode=nl', 'json', None],

        }
        super().__init__(self.supplier, self.api_key)

    def download(self, *args):
        args = self.downloads.keys() if args == () else args
        downloads = [[arg] + self.downloads[arg] for arg in args]
        super().download(downloads)
