import os

from obrazarna_klient.config import CACHE_DIR


def init_cache():
    path = os.path.expanduser(CACHE_DIR)
    if os.path.exists(path):
        return
    os.makedirs(path)
