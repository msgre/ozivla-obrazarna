from django.conf import settings

# velikost gridu
GRID_WIDTH = getattr(settings, 'GRID_WIDTH', 6)
GRID_HEIGHT = getattr(settings, 'GRID_HEIGHT', 3)
PADDING = getattr(settings, 'PADDING', 20)
SCREEN_WIDTH = getattr(settings, 'SCREEN_WIDTH', 1280)
SCREEN_HEIGHT = getattr(settings, 'SCREEN_HEIGHT', 720)

# odvozene konstanty
CELL_WIDTH = int(round(SCREEN_WIDTH / GRID_WIDTH - 2 * PADDING))
CELL_HEIGHT = int(round(SCREEN_HEIGHT / GRID_HEIGHT - 2 * PADDING))


def calculate_dimension(width, height):
    """
    Vypocita idealni rozmery obrazku tak, aby se vesly do gridu.
    
    Vraci:
        (width, height, ratio)
    """
    if not width or not height:
        return (None, None, None)
    w_ratio = CELL_WIDTH / width
    h_ratio = CELL_HEIGHT / height
    ratio = h_ratio if h_ratio < w_ratio else w_ratio
    return (int(round(width * ratio)), int(round(height * ratio)), ratio)
