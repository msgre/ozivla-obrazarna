import math
import pygame
import random
import requests

from PIL import Image, ImageDraw, ImageFilter

from obrazarna_klient.config import TITLE_COLOR, SPOT_ALPHA, SPOT_BLUR, SPOT_STEPS, SPOT_RADIUS_ADDON, SPOT_WAIT, TITLE_BLUR
from obrazarna_klient.easing2 import EasyInOut
from obrazarna_klient.config import API_DOMAIN


CONSISTENT_STEPS = True


class Intro:
    """
    Vykresli obrazy v gridu, prekryje je cernym zavojem a na to vse vykresli titulek
    "Ozivla Obrazarna". Pres jednotlive obrazy putuje svetelny kuzel, ktery jakoby zameruje
    ruzne obrazy, chvili pocka a pak zas zameri na dalsi.
    """

    flip = True

    def __init__(self, screen, dimensions, pictures, font):
        self.accompaniment_id = None
        # reference na hlavni obrazovku
        self.screen = screen
        self.screen.fill((0, 0, 0))

        # rozmery (obrazovky, gridu)
        self.dgrid = dimensions['grid']  # rozmer gridu (pocet bunek na sirku/vysku, padding smerem do bunky)
        self.dscreen = dimensions['screen']  # rozmer obrazovky [px]
        self.dcell = dimensions['cell']  # rozmer jedne bunky, ve ktere bude vykreslen obraz [px] (bez paddingu)
        self.dcell_padding = {
            'width': dimensions['cell']['width'] + 2 * dimensions['grid']['padding'],
            'height': dimensions['cell']['height'] + 2 * dimensions['grid']['padding'],
        }
        self.cells_count = self.dgrid['width'] * self.dgrid['height']  # celkovy pocet bunek v gridu

        self.max_distance = self.get_distance((0, 0), (self.dscreen['width']-1, self.dscreen['height']-1))
        self.step_length = self.max_distance / SPOT_STEPS

        # slovnik obrazu nahranych ze serveru
        self.pictures = pictures
        
        # nahodne vybrane obrazy do gridu
        self.choose_random_pictures()

        # --- obrazky ---

        # napis
        self.title = get_title_image(
            width=self.dscreen['width'],
            height=self.dscreen['height'],
            font=font,
            text="Oživlá obrazárna",
            color=TITLE_COLOR
        )

        # kuzel svetla
        self.spot_grid_pos1, self.spot_grid_pos2 = self.get_random_grid_pos(count=2)
        self.spot_pos1 = self.convert_grid_pos(self.spot_grid_pos1)
        self.spot_pos2 = self.convert_grid_pos(self.spot_grid_pos2)
        self.easing = EasyInOut(self.spot_pos1, self.spot_pos2, self.get_steps())
        self.pos_x = self.spot_pos1[0]
        self.pos_y = self.spot_pos1[1]
        self.spot = get_spot_image(
            width=self.dcell['width'],
            height=self.dcell['height'],
            color=SPOT_ALPHA,
            blur=SPOT_BLUR,
            extra=SPOT_RADIUS_ADDON
        )
        self.sw = self.spot.get_width()
        self.sh = self.spot.get_height()
        self.spot_offset = (
            self.dgrid['padding'] + (self.dcell['width'] - self.sw) // 2,
            self.dgrid['padding'] + (self.dcell['height'] - self.sh) // 2,
        )

        # pozadi
        self.background = pygame.Surface((self.dscreen['width'], self.dscreen['height']), pygame.SRCALPHA)
        self.background.fill((0, 0, 0))
        self.draw_pictures(self.background)
        self.original_background = self.background.copy()
        self.dimmed_background = get_dimmed_image(
            surface=self.background,
            color=SPOT_ALPHA
        )
        self.original_dimmed_background = self.dimmed_background.copy()
        self.background.blit(self.title, (0, 0))
        self.dimmed_background.blit(self.title, (0, 0))

        # initial vykresleni obrazovky do hlavni obrazovky
        self.screen.blit(self.dimmed_background, (0,0))
        self.spot_region = pygame.Surface((self.sw, self.sh), pygame.SRCALPHA)

        # citac pro cekacku nad obrazem
        self.wait = -1
        self.triggered = False

        self.final_pos_buff = None


    def process(self, tick, context):
        """
        TODO:
        """
        if not self.triggered and context.get('pressed', False):
            self.triggered = True

        # offset k vypocitane pozici (x, y), diky kteremu bude kuzel svetla mirit vzdy do stredu obrazu
        ox = self.spot_offset[0]
        oy = self.spot_offset[1]

        # prekresleni spotu na stare pozici
        # (takze obrazovka ted vypada jako dimmed background s napisem)
        _x1 = self.pos_x + ox
        _y1 = self.pos_y + oy
        self.screen.blit(self.dimmed_background, (_x1, _y1), (_x1, _y1, self.sw, self.sh))

        # vypocet nove pozice spotu
        if self.wait == -1:
            (self.pos_x, self.pos_y) = self.easing.step()
        _x1 = self.pos_x + ox
        _y1 = self.pos_y + oy
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
        self.spot_region.fill((0,0,0))
        # ukrademe kousek pozadi...
        self.spot_region.blit(self.background, (_x, _y), (_x1, _y1, self.sw, self.sh))
        # ...prdnem pres nej spot...
        self.spot_region.blit(self.spot, (0, 0))
        # ...a pak jeste titulek...
        self.spot_region.blit(self.title, (0, 0), (self.pos_x + ox, self.pos_y + oy, self.spot_region.get_width(), self.spot_region.get_height()))
        # ...a vysledek (spot_region) konecne prdnem na hlavni obrazovku
        self.screen.blit(self.spot_region, (self.pos_x + ox, self.pos_y + oy), (0, 0, self.spot_region.get_width(), self.spot_region.get_height()))

        if self.wait > 0:
            self.wait -= 1
        elif self.wait == 0:
            self.wait = -1
            # cilova pozice je nyni vychozi
            self.spot_grid_pos1 = self.spot_grid_pos2
            self.spot_pos1 = self.spot_pos2
            # nova, nahodne vybrana cilova pozice
            if self.triggered:
                self.spot_grid_pos2 = self.get_recommended_pos(old=self.spot_grid_pos1)
            else:
                self.spot_grid_pos2 = self.get_random_grid_pos(old=self.spot_grid_pos1)[0]
            self.spot_pos2 = self.convert_grid_pos(self.spot_grid_pos2)
            # inicializace easingu (hladkeho pohybu mezi pozicemi)
            self.easing = EasyInOut(self.spot_pos1, self.spot_pos2, self.get_steps())
        elif self.easing.done():
            if self.triggered:
                self.wait = 0
            else:
                self.wait = SPOT_WAIT
            if self.triggered and self.final_pos_buff is not None and not self.final_pos_buff:
                return 'fadeout'  # TODO: z nekama brat

    def get_steps(self):
        """
        Spocita pocet kroku pro spot mezi body spot_pos1 a spot_pos2.
        """
        if CONSISTENT_STEPS:
            distance = self.get_distance(self.spot_pos1, self.spot_pos2)
            return int(round(distance / self.step_length))
        else:
            return SPOT_STEPS

    def get_distance(self, pos1, pos2):
        """
        Vrati vzdalenost mezi zadanymi body.
        """
        dx = pos1[0] - pos2[0]
        dy = pos1[1] - pos2[1]
        return math.sqrt(dx * dx + dy * dy)

    def convert_grid_pos(self, pos):
        """
        Prevede pozici grid bunky na pixelove souradnice.

        Tj. neco jako (3, 1) -> (450, 274)
        """
        x = self.dcell_padding['width'] * pos[0]
        y = self.dcell_padding['height'] * pos[1]
        return (x, y)

    def choose_random_pictures(self):
        """
        Vybere nahodny set obrazku, ktere se v tomto cyklu zobrazi na obrazovce.
        """
        keys = list(self.pictures.keys())
        random.shuffle(keys)
        self.choosen = keys[:self.cells_count]

    def draw_pictures(self, screen):
        """
        Vykresli vybrane obrazky na obrazovku.
        """
        base_x = 0
        base_y = 0
        x_idx = 0

        for id_ in self.choosen:
            picture = self.pictures[id_]

            # vypocet pozice obrazu
            x = base_x + (self.dcell_padding['width'] - picture.grid_width) // 2
            y = base_y + (self.dcell_padding['height'] - picture.grid_height) // 2

            # vykresleni do obrazovky
            screen.blit(picture.grid_surf, (x, y))

            # posun na dalsi pozici
            base_x += self.dcell_padding['width']
            x_idx += 1
            if x_idx >= self.dgrid['width']:
                x_idx = 0
                base_x = 0
                base_y += self.dcell_padding['height']

    def get_random_values(self, count, old=None):
        """
        Vybere nahodnou hodnotu z rozsahu (0..count). Pokud je zadany old, pak zajisti,
        aby se tato hodnota nevybrala.
        """
        values = list(range(count))
        if old is not None:
            values.remove(old)
        random.shuffle(values)
        return values

    def get_random_grid_pos(self, count=1, old=None):
        """
        Vygeneruje `count` nahodnych pozic a vrati je jako seznam tupliku.
        Pokud je zadany old (jako tuple (x,y)), pak zajisti, ze se tato souradnice ve vystupu neobjevi.
        """
        x = self.get_random_values(self.dgrid['width'], old=None if old is None else old[0])
        y = self.get_random_values(self.dgrid['height'], old=None if old is None else old[1])
        return [(x[i], y[i]) for i in range(count)]

    def get_recommended_pos(self, old=None):
        if not self.final_pos_buff:
            self.final_pos_buff = []

            # nechame si ze serveru doporucit obraz, ktery ma byt vybran
            selected = ",".join(map(str, self.choosen))
            params = {'selected': selected}
            r = requests.get(f'{API_DOMAIN}/api/performance/recommend/', params=params)
            data = r.json()
            recommended_id = data['picture']['id']
            self.accompaniment_id = data['accompaniment']['id']

            # najdeme pozici obrazu na obrazovce
            recommended_idx = self.choosen.index(recommended_id)
            y = recommended_idx // self.dgrid['width']
            x = recommended_idx - (y * self.dgrid['width'])
            
            if (x, y) == old:
                self.final_pos_buff.append(self.get_random_grid_pos(old=old)[0])
            self.final_pos_buff.append((x, y))

        return self.final_pos_buff.pop(0)

    def export(self):
        picture_idx = self.spot_grid_pos2[1] * self.dgrid['width'] + self.spot_grid_pos2[0]
        picture = self.pictures[self.choosen[picture_idx]]
        return {
            # dulezite obrazky
            'intro_background': self.original_background,
            'intro_dimmed_background': self.original_dimmed_background,
            'intro_title': self.title,
            'intro_spot': self.spot,

            # pozice a rozmer spotu
            'intro_pos_x': self.pos_x,
            'intro_pos_y': self.pos_y,
            'intro_spot_offset': self.spot_offset,
            'intro_sw': self.sw,
            'intro_sh': self.sh,

            # maly pracovni surface, do ktereho se sesklada spot misto
            'intro_spot_region': self.spot_region,
            'intro_spot_grid_pos2': self.spot_grid_pos2,
            'intro_picture': picture,
            
            # obecne
            'intro_dcell_padding': self.dcell_padding,

            'accompaniment_id': self.accompaniment_id,
        }


# pomocne funkce


def add_pil_margin(img, top, right, bottom, left, color):
    """
    Pomocna funkce, zvetsi obrazek o zadany prostor a nove pridane casti vylije zadanou barvou.

    Neco jako kdyz se v Gimpu zvetsuje canvas.
    """
    width, height = img.size
    new_width = width + right + left
    new_height = height + top + bottom
    out = Image.new(img.mode, (new_width, new_height), color)
    out.paste(img, (left, top))
    return out


def get_dimmed_image(surface, color):
    """
    Vygeneruje kopii `surface`, pres kterou je aplikovany sedy zavoj
    (ve stejne barve jako je tomu u spot kolecka, na jeho vnejsich hranach).
    """
    out = surface.copy()

    w = surface.get_width()
    h = surface.get_height()

    alpha = Image.new("L", (w, h), color=color)
    im = Image.new("RGBA", (w, h))
    im.putalpha(alpha)

    pg_im = pygame.image.fromstring(im.tobytes(), im.size, im.mode)
    out.blit(pg_im, (0, 0))

    return out


def get_spot_image(width, height, color, blur, extra=0):
    """
    Vygeneruje obrazek, kterym simulujeme kuzel svetla.

    Jde o obrazek s alfa kanalem, ktery kdyz se naaplikuje na jiny tak v jeho stredu nechava puvodni
    obsah, ale smerem od stredu to pak utlumuje a prekryva polopruhlednou cernou vrstvou.
    """
    # prumer kolca
    diameter = max(width, height)
    
    # ctverec, do ktereho se kolco vykresli (musime pricist blur a pripadny velikostni bonus)
    edge = diameter + extra + blur * 2
    
    # pro jistotu maly bonus k velikosti, at je jistota ze nebude blur orizly
    # a at jde o nasobek 2
    if edge % 2 == 1:
        edge += 3
    else:
        edge += 2

    # priprava alfa kanalu
    # - cely bude vylity barvou "color"
    # - do nej se nakresli cerne kolco (blur daleko od hran ctverce)
    # - cely obrazek se blurne, takze hrany kolca budou mit jemny prechod mezi "color" a cernou
    alpha = Image.new("L", (edge, edge), color=color)
    draw = ImageDraw.Draw(alpha)
    draw.ellipse((blur, blur, edge-blur, edge-blur), fill=0)
    alpha = alpha.filter(ImageFilter.BoxBlur(blur))

    # vytvorime obrazek
    # - cerne vylita vrstva s alfa kanalem
    out = Image.new("RGBA", (edge, edge))
    out.putalpha(alpha)

    return pygame.image.fromstring(out.tobytes(), out.size, out.mode)


def get_title_image(width, height, font, text, color, blur=TITLE_BLUR):
    """
    Vygeneruje obrazek o velikosti cele obrazovky s napisem uprostred.

    Obrazek je pruhledny, napis ma pod sebou blurnuty stin.
    """
    # vyrenderovani napisu
    shadow = font.render(text, True, (0, 0, 0))
    title = font.render(text, True, color)

    # spocita pozici tak aby byl napis uprostred obrazovky
    title_rect = title.get_rect()
    x = (width - title_rect.width) // 2
    y = (height - title_rect.height) // 2

    # vystupni obrazek, do ktereho se napis bude generovat
    out = Image.new("RGBA", (width, height))

    # --- vygenerovani stinu pod napisem (aby sel precist, kdyz je pod nim spot) ---

    # nejdriv prevedem PyGame image (vyrenderovany napis) -> PIL image
    shadow_bytes = pygame.image.tostring(shadow, "RGBA")
    shadow_image = Image.frombuffer("RGBA", shadow.get_rect().size, shadow_bytes)

    # obrazek zvetsime, protoze potrebujem prostor pro blur
    wm = (out.size[0] - shadow.get_width()) // 2
    hm = (out.size[1] - shadow.get_height()) // 2
    shadow_image = add_pil_margin(
        img=shadow_image,
        top=hm,
        right=wm,
        bottom=hm,
        left=wm,
        color=0
    )

    # cerny obdelnik...
    tmp_image = Image.new("RGBA", shadow_image.size, color=(0,0,0))
    # ...do ktereho prdnem alfa kanal s blurnutym napisem...
    tmp_image.putalpha(shadow_image.getchannel("A").filter(ImageFilter.GaussianBlur(blur))) 
    # ...a ktery pastnem do vystupniho obrazku
    # bacha! bez parametru mask by to nefungovalo!
    out.paste(tmp_image, (0, 0), mask=tmp_image.getchannel("A"))

    # --- vygenerujeme bily napis nad stinem ---

    # prevedem PyGame image (vyrenderovany napis) -> PIL image
    title_bytes = pygame.image.tostring(title, "RGBA")
    title_image = Image.frombuffer("RGBA", title.get_rect().size, title_bytes)

    # bily obdelnik...
    tmp_image = Image.new("RGBA", title_image.size, color=(255,255,255))
    # ...s alfa kanalem v podobe napisu
    tmp_image.putalpha(title_image.getchannel("A"))
    # ...prdnuty do vystupniho obrazku
    out.paste(tmp_image, (x, y), mask=tmp_image.getchannel("A"))

    # a nakonec prevod PIL -> PyGame image
    return pygame.image.fromstring(out.tobytes(), out.size, out.mode)
