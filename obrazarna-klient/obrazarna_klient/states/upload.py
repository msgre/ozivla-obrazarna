import time
import uuid
import os
import picamera
import pygame
import requests

from PIL import Image

from obrazarna_klient.config import CAMERA_RESOLUTION, CAMERA_FRAMERATE, CAMERA_HFLIP, CAMERA_VFLIP, CACHE_DIR, API_DOMAIN


class Upload:
    flip = True

    def __init__(self, screen, dimensions, pictures, font, video_path, image_path, picture_id, accompaniment_id):

        self.accompaniment_id = accompaniment_id
        self.video_path = video_path
        self.picture_id = picture_id
        self.screen = screen
        self.dscreen = dimensions['screen']  # rozmer obrazovky [px]
        self.background = pygame.Surface((self.dscreen['width'], self.dscreen['height']), pygame.SRCALPHA)
        
        self.title = font.render('Hotovo!', True, (255, 255, 255))
        title_rect = self.title.get_rect()
        width = 1280
        height = 720
        self.x = (width - title_rect.width) // 2
        self.y = (height - title_rect.height) // 2

        self.background.blit(self.title, (self.x, self.y))
        self.screen.blit(self.background, (0,0))
        self.upload = True
        self.start_tick = None
        self.end_tick = None

    def process(self, tick, context):
        if self.upload:
            self.start_tick = tick
            self.end_tick = tick + (2 * CAMERA_FRAMERATE)
            data = {
                'picture_id': self.picture_id,
                'accompaniment_id': self.accompaniment_id,
            }
            files = {'raw_footage': open(self.video_path, "rb")}
            r = requests.post(f'{API_DOMAIN}/api/performance/', data=data, files=files)
            print(r)
            os.remove(self.video_path)
            self.upload = False
        if tick >= self.end_tick:
            return 'intro'

    def export(self):
        return {}
