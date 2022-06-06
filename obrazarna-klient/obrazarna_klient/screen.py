"""
Inicializace/ukonceni pygame (hlavne obrazovky).
"""

import pygame


def init_screen(width, height, color=None):
    """
    Inicializuje obrazovku Pygame.
    """
    pygame.init()
    screen = pygame.display.set_mode([width, height], pygame.FULLSCREEN)
    if not color:
        color = (0, 0, 0)
    screen.fill(color)
    return screen


def close_screen():
    """
    Ukonci Pygame.
    """
    pygame.quit()
