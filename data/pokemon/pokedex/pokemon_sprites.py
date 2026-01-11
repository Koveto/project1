import os
from PIL import Image
import pygame

# Constants
GRID = 5
SPRITE = 64
ALPHA_KEY = (165, 235, 255)  # A5EBFF transparency key

# Path to project root (3 levels up from pokedex/)
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
SPRITE_DIR = os.path.join(ROOT, "sprites")

# Cache for loaded sheets
_sheets = {}

# Filenames for each generation
FILENAMES = {
    (1, False, False): "gen1_nonshiny.png",
    (1, True,  False): "gen1_shiny.png",
    (1, False, True):  "gen1_nonshiny_back.png",
    (1, True,  True):  "gen1_shiny_back.png",

    (2, False, False): "gen2_nonshiny.png",
    (2, True,  False): "gen2_shiny.png",
    (2, False, True):  "gen2_nonshiny_back.png",
    (2, True,  True):  "gen2_shiny_back.png",

    (3, False, False): "gen3_nonshiny.png",
    (3, True,  False): "gen3_shiny.png",
    (3, False, True):  "gen3_nonshiny_back.png",
    (3, True,  True):  "gen3_shiny_back.png",
}


def _load_sheet(gen, is_shiny, is_back):
    """Load the correct spritesheet once and reuse it."""
    key = (gen, is_shiny, is_back)

    if key not in _sheets:
        filename = FILENAMES[key]
        path = os.path.join(SPRITE_DIR, filename)
        sheet = Image.open(path).convert("RGBA")
        _sheets[key] = sheet

    return _sheets[key]


def _pil_to_pygame(image):
    """Convert a PIL Image (RGBA) to a Pygame Surface."""
    mode = image.mode
    size = image.size
    data = image.tobytes()
    return pygame.image.fromstring(data, size, mode).convert_alpha()


def load_pokemon_sprite(gen, index, is_shiny=False, is_back=False, scale=1):
    """
    Load a single Pokémon sprite from Gen 1, Gen 2, or Gen 3.
    Returns a Pygame Surface.
    """

    sheet = _load_sheet(gen, is_shiny, is_back)
    sheet_w, sheet_h = sheet.size

    # Compute how many sprites per row
    sprites_per_row = (sheet_w - GRID) // (SPRITE + GRID)

    # Convert index → row/column
    row = index // sprites_per_row
    col = index % sprites_per_row

    # Pixel coordinates
    x0 = GRID + col * (SPRITE + GRID)
    y0 = GRID + row * (SPRITE + GRID)
    x1 = x0 + SPRITE
    y1 = y0 + SPRITE

    # Crop
    frame = sheet.crop((x0, y0, x1, y1))

    # Transparency cleanup
    data = frame.getdata()
    cleaned = []
    for r, g, b, a in data:
        if (r, g, b) == ALPHA_KEY:
            cleaned.append((r, g, b, 0))
        else:
            cleaned.append((r, g, b, a))
    frame.putdata(cleaned)

    # Scale
    if scale != 1:
        frame = frame.resize((SPRITE * scale, SPRITE * scale), Image.NEAREST)

    # Convert to Pygame Surface
    return _pil_to_pygame(frame)
