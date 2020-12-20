# -*- coding: utf8 -*-
# Standard library imports
import json
import re
import pathlib
import math
import time
import datetime
from pathlib import Path

# Third party imports
from bs4 import BeautifulSoup
import requests

urls_to_srape = [
    # apartement te koop
    # tienen
    """https://www.immoweb.be/en/search/apartment/for-sale/tienen/3300?buildingConditions=AS_NEW,JUST_RENOVATED&countries=BE&maxBedroomCount=3&maxPrice=230000&minBedroomCount=1&minPrice=100000&priceType=PRICE&propertySubtypes=KOT,FLAT_STUDIO,DUPLEX,SERVICE_FLAT,LOFT&orderBy=newest"""
    # bxl
    """https://www.immoweb.be/en/search/apartment/for-sale/brussels/district?buildingConditions=AS_NEW,JUST_RENOVATED&countries=BE&maxBedroomCount=3&maxPrice=230000&minBedroomCount=1&minPrice=100000&priceType=PRICE&propertySubtypes=KOT,FLAT_STUDIO,DUPLEX,SERVICE_FLAT,LOFT&orderBy=newest"""
    # leuven
    """https://www.immoweb.be/en/search/apartment/for-sale/leuven/district?buildingConditions=AS_NEW,JUST_RENOVATED&countries=BE&maxBedroomCount=3&maxPrice=230000&minBedroomCount=1&minPrice=100000&priceType=PRICE&propertySubtypes=KOT,FLAT_STUDIO,DUPLEX,SERVICE_FLAT,LOFT&orderBy=newest"""

    # apartement te huur
    # tienen
    """https://www.immoweb.be/en/search/apartment/for-rent/tienen/3300?countries=BE&maxBedroomCount=3&maxPrice=1000&minBedroomCount=1&minPrice=600&priceType=MONTHLY_RENTAL_PRICE&orderBy=newest"""
    # bxl
    """https://www.immoweb.be/en/search/apartment/for-rent/brussels/district?countries=BE&maxBedroomCount=3&maxPrice=1000&minBedroomCount=1&minPrice=600&priceType=MONTHLY_RENTAL_PRICE&orderBy=newest"""
    # leuven
    """https://www.immoweb.be/en/search/apartment/for-rent/leuven/district?countries=BE&maxBedroomCount=3&maxPrice=1000&minBedroomCount=1&minPrice=600&priceType=MONTHLY_RENTAL_PRICE&orderBy=newest"""

]
def handler(event, context):
    for url in urls_to_srape:
        # we only collect the first page
        search_page = requests.get(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:75.0) Gecko/20100101 Firefox/75.0'})
        search_soup = BeautifulSoup(search_page.content, "html.parser")
        pretty_page = search_soup.prettify()
        pretty_page

if __name__ == '__main__':
    handler(None, None)