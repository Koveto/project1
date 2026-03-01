import os
from PIL import Image
import pygame

# Constants for the new sheet
CELL = 69          # full grid cell size
SPRITE = 64        # actual sprite size inside the cell
BORDER = 5         # top/left border
ALPHA_KEY = (165, 235, 255)


# Cache
_big_sheet = None

# Path setup
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SPRITE_DIR = os.path.join(ROOT, "sprites")
BIG_SHEET_PATH = os.path.join(SPRITE_DIR, "pokemon.png")
PLAYER_SPRITE_PATH = os.path.join(ROOT, "sprites", "player_battle.png")
PLAYER_W = 48
PLAYER_H = 52


def _load_big_sheet():
    global _big_sheet
    if _big_sheet is None:
        sheet = Image.open(BIG_SHEET_PATH).convert("RGBA")
        _big_sheet = sheet
    return _big_sheet


def _pil_to_pygame(image):
    mode = image.mode
    size = image.size
    data = image.tobytes()
    return pygame.image.fromstring(data, size, mode).convert_alpha()


def load_pokemon_sprite(row, column, scale=1):
    """
    Load a single Pokémon sprite from the giant 69x69 grid sheet.
    Each cell is 69x69, but the actual sprite is the bottom-right 64x64.
    """
    sheet = _load_big_sheet()

    # Compute pixel coordinates of the 69x69 cell
    x0 = column * CELL
    y0 = row * CELL

    # Horizontal is fine
    sx0 = x0 + BORDER
    sx1 = sx0 + SPRITE

    # Nudge vertical crop 1px up to avoid bottom bleed
    sy0 = y0 + BORDER #-1
    sy1 = sy0 + SPRITE

    frame = sheet.crop((sx0, sy0, sx1, sy1))

    # Apply alpha key cleanup
    data = frame.getdata()
    cleaned = []
    for r, g, b, a in data:
        if (r, g, b) == ALPHA_KEY:
            cleaned.append((r, g, b, 0))
        else:
            cleaned.append((r, g, b, a))
    frame.putdata(cleaned)

    if scale != 1:
        frame = frame.resize((SPRITE * scale, SPRITE * scale), Image.NEAREST)

    return _pil_to_pygame(frame)



def load_player_sprite(scale):
    """
    Loads the player's battle sprite from sprites/player_battle.png.
    The sprite is 48x52 and uses ff00e4 as the transparent color key.
    Returns a scaled pygame.Surface.
    """

    # Load raw image
    img = pygame.image.load(PLAYER_SPRITE_PATH).convert()

    # Apply color key transparency (ff00e4)
    colorkey = (0xFF, 0x00, 0xE4)
    img.set_colorkey(colorkey)

    # Scale the sprite
    scaled = pygame.transform.scale(
        img,
        (PLAYER_W * scale, PLAYER_H * scale)
    )

    return scaled
