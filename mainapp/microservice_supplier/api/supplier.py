import logging
import time

import requests
from decouple import config

from mainapp.microservice_supplier import EDC_BASE_URL, BB_BASE_URL, BASE_PATH

logger = logging.getLogger('microservice_supplier.edc')


class BaseClient:
    def __init__(self, supplier, api_key=None):
        self.supplier = supplier
        self.api_key = api_key


    def send_request(self, name, url):
        logger.info(f'Sending request for {name}')

        if self.supplier == 'bigbuy':
            request = requests.get(url, headers={"Authorization": f"Bearer {self.api_key}"})

        elif self.supplier == 'edc':
            request = requests.get(url)

        return request.text, request.status_code

    def save_to_feeds(self, file, filename, filetype='xml'):
        logger.info(f'Starting saving of {filetype}')
        with open(f'{BASE_PATH}/files/{self.supplier}/feeds/{filename}.{filetype}', 'w') as f:
            f.write(file)
            logger.info(f"Successfully saved {filename}.{filetype}")

    # Please note, this can take a few minutes (around 5 I would say). Maybe async this later?
    def download(self, downloads):
        for name, url, filetype, output_type in downloads:
            response, status_code = self.send_request(name, url)

            if status_code == 200:
                self.save_to_feeds(response, name, filetype=filetype)
            elif status_code == 429:
                logger.info("Sleeping because of timeout")
                time.sleep(300)
                response, status_code = self.send_request(name, url)
                self.save_to_feeds(response, name, filetype=filetype)
            else:
                logger.warning(f'Status code {status_code}')

class EdcClient(BaseClient):
    def __init__(self):
        self.supplier = 'edc'
        self.api_key = config('EDC_API_KEY')
        self.downloads = {
            'full': [f'{EDC_BASE_URL}b2b_feed.php?key={self.api_key}&sort=xml&type=xml&lang=en&version=2015',
                     'xml', 'raw'],
            'new': [f'{EDC_BASE_URL}b2b_feed.php?key={self.api_key}&sort=xml&type=xml&lang=en&version=2015&new=1',
                    'xml', 'raw'],
            'discounts': [f'https://www.erotischegroothandel.nl/download/discountoverview.csv?apikey={self.api_key}',
                          'csv', 'raw'],
            'stock': [f'{EDC_BASE_URL}xml/eg_xml_feed_stock.xml',
                      'xml', 'text'],
            'full_price': [f'https://www.erotischegroothandel.nl/download/priceoverview.csv?apikey={self.api_key}',
                           'csv', 'text'],
            'update_price': [f'https://www.erotischegroothandel.nl/download/pricechange.csv?apikey={self.api_key}',
                             'csv', 'text']
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
            'full': [f'{BB_BASE_URL}rest/catalog/products.json?isoCode=NL',
                     'json', 'raw']
            }
        super().__init__(self.supplier, self.api_key)

    def download(self, *args):
        args = self.downloads.keys() if args == () else args
        downloads = [[arg] + self.downloads[arg] for arg in args]
        super().download(downloads)
