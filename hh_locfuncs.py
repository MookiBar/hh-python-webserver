#!/usr/bin/env python3

import requests
import urllib.parse
import re
from collections import namedtuple

GeoLoc = namedtuple('GeoLoc', ('lat','lon','range'))

ZIP_CODES = {}

def get_addr_results_from_api(address):
    url = 'https://nominatim.openstreetmap.org/search/{address}?format=json'.format(
            urllib.parse.quote(address)
            )
    response = requests.get(url).json()
    return response


def get_lat_lon_range_of_addr(addr_string):
    addr_string = addr_string.strip()
    if re.match(r'\b[0-9]{5}\b', addr_string):
        ## is a zip code, check ZIP_CODES
        if addr_string in ZIP_CODES:
            return ZIP_CODES[addr_string]

