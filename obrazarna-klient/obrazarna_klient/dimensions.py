"""
Informace o zakladnich rozmerech (obrazovky, gridu).
"""

import requests
from obrazarna_klient.config import API_DOMAIN


def load_dimensions():
    """
    Stahne ze serveru informace o rozmerech (obrazovky, gridu, ...).
    """
    r = requests.get(f'{API_DOMAIN}/api/dimensions/')
    return r.json()
