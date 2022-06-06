import pygame
from obrazarna_klient.screen import init_screen, close_screen
from obrazarna_klient.pictures import load_pictures
from obrazarna_klient.dimensions import load_dimensions
from obrazarna_klient.config import FRAMERATE, FONT_PATH, FONT_SIZE
from obrazarna_klient.gallery import Gallery
from obrazarna_klient.cache import init_cache

init_cache()

# init data ze serveru
dimensions = load_dimensions()
screen = init_screen(dimensions['screen']['width'], dimensions['screen']['height'])
pictures = load_pictures()

# inicializace pygame
clock = pygame.time.Clock()
font = pygame.font.Font(FONT_PATH, FONT_SIZE)
pygame.mouse.set_visible(False)

# inicializace hlavni tridy ktera vsemu sefuje
gallery = Gallery(dimensions, screen, pictures, font)

# hlavni smycka
running = True
context = {'pressed': False}

while running:
    # udalosti (zavreni okna, tlacitka)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_SPACE:
                context['pressed'] = True
                pygame.mixer.music.play()
        elif event.type == pygame.KEYUP:
            context['pressed'] = False

    # osetreni stavu
    gallery.process(context)

    # vykresleni obrazovky
    clock.tick(FRAMERATE)

# ukonceni pygame
close_screen()
