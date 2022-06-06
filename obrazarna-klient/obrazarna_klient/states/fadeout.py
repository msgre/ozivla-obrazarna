import pygame


class Fadeout:
    """
    Fadout titulku nad obrazy, kde jeden z nich je spotnuty.
    """

    flip = True

    def __init__(self, screen, dimensions, pictures, font, intro_background, intro_dimmed_background, intro_title, intro_spot, intro_pos_x, intro_pos_y, intro_spot_offset, intro_sw, intro_sh, intro_spot_region, intro_dcell_padding, intro_spot_grid_pos2, intro_picture, accompaniment_id):
        self.accompaniment_id = accompaniment_id

        # cilovy surface
        self.screen = screen
        self.pictures = pictures
        self.intro_picture = intro_picture

        # rozmery (obrazovky, gridu)
        self.dgrid = dimensions['grid']  # rozmer gridu (pocet bunek na sirku/vysku, padding smerem do bunky)
        self.dscreen = dimensions['screen']  # rozmer obrazovky [px]
        self.dcell = dimensions['cell']  # rozmer jedne bunky, ve ktere bude vykreslen obraz [px] (bez paddingu)
        self.dcell_padding = intro_dcell_padding
        self.cells_count = self.dgrid['width'] * self.dgrid['height']  # celkovy pocet bunek v gridu

        # dulezite obrazky
        self.intro_background = intro_background
        self.intro_dimmed_background = intro_dimmed_background
        self.intro_title = intro_title
        self.intro_spot = intro_spot
        self.intro_spot_grid_pos2 = intro_spot_grid_pos2

        # pozice a rozmer spotu
        self.intro_pos_x = intro_pos_x
        self.intro_pos_y = intro_pos_y
        self.intro_spot_offset = intro_spot_offset
        self.intro_sw = intro_sw
        self.intro_sh = intro_sh

        # maly pracovni surface, do ktereho se sesklada spot misto
        self.intro_spot_region = intro_spot_region

        # priprava pozadi
        self.background = pygame.Surface((self.dscreen['width'], self.dscreen['height']), pygame.SRCALPHA)
        self.prepare_background()

        # titulek
        self.title_pos1, p2 = self.find_title_boundaries()
        tw = p2[0] - self.title_pos1[0]
        th = p2[1] - self.title_pos1[1]
        self.title_size = (self.title_pos1[0], self.title_pos1[1], tw, th)
        self.title_alpha = 255

        self.done = False

    def find_title_boundaries(self):
        """
        Najde levou/horni a pravou/dolni pozici v obrazku self.intro_title kde zacina/konci
        titulek (self.intro_title ma rozmer jedne kompletni obrazovky, ale pro vykreslovani
        je efektivnejsi prekreslovat jen to kde fakt neco je; proto musim najit hranice titulku).
        """
        width = self.intro_title.get_width()
        height = self.intro_title.get_height()
        min_y, max_y = None, None
        min_x, max_x = None, None

        for y in range(height):
            for x in range(width):
                color = self.intro_title.get_at((x,y))
                if color[3] != 0:
                    min_y = y
                    break
            if min_y is not None:
                break

        for y in range(height - 1, -1, -1):
            for x in range(width):
                color = self.intro_title.get_at((x,y))
                if color[3] != 0:
                    max_y = y
                    break
            if max_y is not None:
                break

        for x in range(width):
            for y in range(height):
                color = self.intro_title.get_at((x,y))
                if color[3] != 0:
                    min_x = x
                    break
            if min_x is not None:
                break

        for x in range(width - 1, -1, -1):
            for y in range(height):
                color = self.intro_title.get_at((x,y))
                if color[3] != 0:
                    max_x = x
                    break
            if max_x is not None:
                break

        return (min_x, min_y), (max_x, max_y)

    def prepare_background(self):
        """
        Pripravi pozadi pro fadeout efekt, tj:

        * vykresli dimmed obrazy
        * spotnuty obraz vykresli v originalnich barvach
        * pres spotnuty obraz vykresli kolecko (spot)
        * NEVYKRESLI TITULEK
        """
        # komplet tmave pozadi
        self.background.blit(self.intro_dimmed_background, (0, 0))

        # offset k vypocitane pozici (x, y), diky kteremu bude kuzel svetla mirit vzdy do stredu obrazu
        ox = self.intro_spot_offset[0]
        oy = self.intro_spot_offset[1]

        _x1 = self.intro_pos_x + ox
        _y1 = self.intro_pos_y + oy
        # NOTE: nasledujici kejkle souvisi s podivnym chovanim PyGame, pokud chci
        # s pomoci blit vykreslit spot na negativnich souradnicich (za levou ci horni
        # hranou); ono se to chova divne, ale kdyz v techto situacich oblast kterou chci
        # prekreslit vypocitam z praveho dolniho rohu (namisto leveho horniho), tak to fici
        _x = 0
        _y = 0
        if _x1 < 0:
            _x = abs(_x1)
            _x1 = 0
        if _y1 < 0:
            _y = abs(_y1)
            _y1 = 0

        # vykresleni

        # promazani oblasti ktera se prekresluje
        # (operujem s pruhlednostma, kdybych to nechal, bude to delat bordel)
        self.intro_spot_region.fill((0,0,0))
        # ukrademe kousek pozadi...
        self.intro_spot_region.blit(self.intro_background, (_x, _y), (_x1, _y1, self.intro_sw, self.intro_sh))
        # ...prdnem pres nej spot...
        self.intro_spot_region.blit(self.intro_spot, (0, 0))
        # ...a vysledek (intro_spot_region) konecne prdnem do pozadi
        self.background.blit(self.intro_spot_region, (self.intro_pos_x + ox, self.intro_pos_y + oy), (0, 0, self.intro_spot_region.get_width(), self.intro_spot_region.get_height()))

    def process(self, tick, context):
        """
        Kontinualni fadeout titulku.
        """
        if self.title_alpha == 0:
            self.done = True

        # prekreslime oblast titulku pozadim
        self.screen.blit(self.background, self.title_pos1, self.title_size)
        # vykreslime titulek s postupne se menici pruhlednosti
        self.intro_title.set_alpha(self.title_alpha)
        self.screen.blit(self.intro_title, self.title_pos1, self.title_size)
        # vypocitame pruhlednost pro dalsi run
        if self.title_alpha > 0:
            self.title_alpha -= 20
        elif self.title_alpha < 0:
            self.title_alpha = 0

        if self.done:
            return 'zoom'  # TODO:

    def export(self):
        return {
            'intro_dcell_padding': self.dcell_padding,
            'fadeout_picture': self.intro_picture,
            'fadeout_background': self.background,
            'intro_spot_grid_pos2': self.intro_spot_grid_pos2,
            'accompaniment_id': self.accompaniment_id,
        }
