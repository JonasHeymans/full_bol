import requests
import logging

from decouple import config

from app.microservice_edc_pull import BASE_URL, BASE_PATH

logger = logging.getLogger('microservice_edc_pull.edc')



class EdcClient():
    api_key = config('EDC_API_KEY')

    url = f'{BASE_URL}b2b_feed.php?key={api_key}&sort=xml&type=xml&lang=nl&version=2015'

    def __save_to_feeds(self, file, filename, filetype='xml'):
        logger.info(f'Starting saving of {filetype}')
        with open(f'{BASE_PATH}/files/feeds/{filename}.{filetype}', 'w') as f:
            f.write(file)
            logger.info(f"Successfully saved {filename}.{filetype}")

    # Please note, this can take a few minutes (around 5 I would say). Maybe async this later?

    def __send_request(self, arg):
        logger.info(f'Sending request for {arg}')
        d = {'full': '',
             'new': '&new=1',
             }
        return requests.get(f"{self.url}{d[arg]}").text

    def download_products(self, *args):
        getters = ['full', 'new'] if args == () else args
        for getter in getters:
            response = self.__send_request(getter)
            self.__save_to_feeds(response, getter)

    def download_discounts(self):
        # Yikes, hardcoded! (todo)
        response = requests.get(f'https://www.erotischegroothandel.nl/download/discountoverview.csv?apikey={self.api_key}')
        self.__save_to_feeds(response.text, 'discounts', filetype='csv')

    def download_stock(self):
        response = requests.get(f'{BASE_URL}xml/eg_xml_feed_stock.xml')
        self.__save_to_feeds(response.text, 'stock', filetype='xml')

    def download_prices(self, *args):
        # Yikes, hardcoded! (todo)
        getters = ['update'] if args == () else args
        d = {
            'full': 'priceoverview',
            'update': 'pricechange'
        }
        for getter in getters:
            response = requests.get(f'https://www.erotischegroothandel.nl/download/{d[getter]}.csv?apikey={self.api_key}')
            self.__save_to_feeds(response.text, f'price_{getter}', filetype='csv')
