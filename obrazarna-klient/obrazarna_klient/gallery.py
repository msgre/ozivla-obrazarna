import pygame

from obrazarna_klient.states import Intro, Fadeout, Zoom
from obrazarna_klient.states import STATE_INTRO, STATES, STATE_UPLOAD


class Gallery:
    def __init__(self, dimensions, screen, pictures, font):
        # obecna initial data, ktera se hodi vsem
        self.dimensions = dimensions
        self.screen = screen
        self.pictures = pictures
        self.font = font

        # initial stav
        self.state = STATES[STATE_INTRO](screen, dimensions, pictures, font)
        self.tick = 0
        self.context = {}

    def process(self, context=None):
        # priprava kontextu
        ctx = self.context.copy()
        if context:
            ctx.update(context)

        # proces uvnitr konkretniho stavu
        response = self.state.process(self.tick, ctx)
        self.tick += 1
        if not response:
            if self.state.flip:
                pygame.display.flip()
            return

        # presun do noveho stavu
        self.tick = 0
        params = self.state.export()
        self.state = STATES[response](self.screen, self.dimensions, self.pictures, self.font, **params)
        if self.state.flip:
            pygame.display.flip()
