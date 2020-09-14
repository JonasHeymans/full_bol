import requests
import logging

from microservice_edc_pull.constants.constants import BASE_URL, API_KEY

logger = logging.getLogger('microservice_edc_pull.edc')

'''
Timings of each request:


- Full: weekly. To fill db initially, update prices / product properties and check for discontinued products.
- New: Every Friday night. To add new products
- Stock: Every hour. To keep stock up to date.
- Discounts: weekly. To change awarded discounts. 

'''


# Todo: there was a mistake in the stock link. I think the right one is http://api.edc.nl/xml/eg_xml_feed_stock.xml.
#  For now I just removed the stock request.

# TODO probably better to download the zip-file and unpack it locally.


class EdcClient():
    url = f'{BASE_URL}b2b_feed.php?key={API_KEY}&sort=xml&type=xml&lang=nl&version=2015'

    def __save_to_feeds(self, file, filename, filetype='xml'):
        logger.info(f'Starting saving of {filetype}')
        with open(f'files/feeds/{filename}.{filetype}', 'w') as f:
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
        response = requests.get(f'https://www.erotischegroothandel.nl/download/discountoverview.csv?apikey={API_KEY}')
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
            response = requests.get(f'https://www.erotischegroothandel.nl/download/{d[getter]}.csv?apikey={API_KEY}')
            self.__save_to_feeds(response.text, f'price_{getter}', filetype='csv')
