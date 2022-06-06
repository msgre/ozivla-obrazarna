"""
Obrazy jako pygame sprites.
"""

import os
import pygame
import requests

from PIL import Image, ImageDraw

from obrazarna_klient.config import API_DOMAIN, CACHE_DIR


class Picture(pygame.sprite.Sprite):
    """
    Popis jednoho obrazu.
    """
    def __init__(self, path, mask, width, height, grid_width, grid_height, id):
        super().__init__()
        self.original_width = width
        self.original_height = height
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.id = id
        self.surf = pygame.image.load(path).convert_alpha()
        self.grid_surf = self.scale_to_grid()
        self.rect = self.surf.get_rect()
        self.mask = self.prepare_camera_overlay(mask)

    def scale_to_grid(self):
        return pygame.transform.scale(self.surf, (self.grid_width, self.grid_height))

    def prepare_camera_overlay(self, path):
        img = Image.open(path)
        img_recording = img.copy()
        draw = ImageDraw.Draw(img_recording)
        draw.ellipse((20, 20, 100, 100), fill=(255, 0, 0), width=2)
        return img.tobytes(), img.size, img_recording.tobytes(), img_recording.size


def load_pictures():
    """
    Stahne ze serveru vsechny obrazy a ulozi do interniho slovniku jako pygame sprity.
    """
    out = {}

    r = requests.get(f'{API_DOMAIN}/api/pictures/')
    paths = {}
    for picture in r.json()['results']:
        for key in ['file', 'mask']:
            url = picture[key]
            picture_name = url.split('/')[-1]
            paths[key] = os.path.join(os.path.expanduser(CACHE_DIR), picture_name)
            if not os.path.exists(paths[key]):
                with open(paths[key], "wb") as fp:
                    # ulozime soubor do cache
                    fp.write(requests.get(url).content)

        # ulozime obrazek s metadaty do interniho slovniku
        out[picture["id"]] = Picture(
            path=paths['file'],
            mask=paths['mask'],
            width=picture["width"],
            height=picture["height"],
            grid_width=picture["grid_width"],
            grid_height=picture["grid_height"],
            id=picture["id"],
        )

    return out
