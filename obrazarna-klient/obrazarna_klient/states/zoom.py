import pygame
from obrazarna_klient.easing2 import EasyInOut


STEPS = 30
INTERNAL = 0


class Zoom:
    flip = True

    def __init__(self, screen, dimensions, pictures, font, intro_dcell_padding, fadeout_picture, fadeout_background, intro_spot_grid_pos2, accompaniment_id):
        self.accompaniment_id = accompaniment_id
        self.screen = screen
        self.fadeout_background = fadeout_background
        self.dimensions = dimensions

        self.picture = fadeout_picture

        _x, _y = intro_spot_grid_pos2

        _x = intro_dcell_padding['width'] * _x + ((intro_dcell_padding['width'] - fadeout_picture.grid_width) // 2)
        _y = intro_dcell_padding['height'] * _y + ((intro_dcell_padding['height'] - fadeout_picture.grid_height) // 2)

        self.screen.blit(self.fadeout_background, (0, 0))

        pos1 = (_x, _y)
        pos2 = self.new_pos()
        self.easing_pos = EasyInOut(pos1, pos2, STEPS)
        self.easing_size = EasyInOut((0, 0), (100, 100), STEPS)
        self.zoom_x = _x
        self.zoom_y = _y
        self.zoom_size = 0
        self.old_x = None
        self.old_y = None
        self._w = self.picture.grid_width
        self._h = self.picture.grid_height

        self.done = False
        self.internal = INTERNAL

    def process(self, tick, context):

        if self.internal > 0:
            self.internal -= 1
            return
        self.internal = INTERNAL

        (self.old_x, self.old_y, self.old_w, self.old_h) = (self.zoom_x, self.zoom_y, self._w, self._h)
        (self.zoom_x, self.zoom_y) = self.easing_pos.step()
        (self.zoom_size, _) = self.easing_size.step()

        ratio = self.zoom_size / 100
        self._w = int(round(self.picture.grid_width + ((self.picture.original_width - self.picture.grid_width) * ratio)))
        self._h = int(round(self.picture.grid_height + ((self.picture.original_height - self.picture.grid_height) * ratio)))

        # TODO: tohle je neefektivni
        # - melo by stacit vykreslit uzke prouzky okolo nove velikosti
        # - prouzky se vezmou v background a prekresli se pres screen
        # - (aby zmizla predchozi velikost obrazku)

        self.screen.blit(self.fadeout_background, (self.old_x, self.old_y), (self.old_x, self.old_y, self.old_w, self.old_h))
        _picture = pygame.transform.scale(self.picture.surf, (self._w, self._h))

        if self.easing_size.done():
            self.screen.fill((0, 0, 0), (0, 0, self.dimensions['screen']['width'], self.dimensions['screen']['height']))

        self.screen.blit(_picture, (self.zoom_x, self.zoom_y))
        pygame.display.flip()

        if self.easing_size.done():
            return 'preview'  # TODO:

    def new_pos(self):
        x = (self.screen.get_width() - self.picture.original_width) // 2
        y = (self.screen.get_height() - self.picture.original_height) // 2
        return (x, y)

    def export(self):
        return {
            'picture': self.picture,
            'accompaniment_id': self.accompaniment_id,
        }
