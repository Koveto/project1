import os
import pygame

# Scale factor
SCALE = 4

# Resolution (Game Boy Advance)
LOGICAL_WIDTH = 240
LOGICAL_HEIGHT = 160
ACTUAL_WIDTH = LOGICAL_WIDTH * SCALE
ACTUAL_HEIGHT = LOGICAL_HEIGHT * SCALE

# Tile size
LOGICAL_TILE_SIZE = 16
ACTUAL_TILE_SIZE = LOGICAL_TILE_SIZE * SCALE

# Speed
SPEED = 4

TARGET_FPS = 30

SCROLL_SPEED = 5

ELEMENT_INDEX = {
    "Physical": 0,
    "Fire": 1,
    "Force": 2,
    "Ice": 3,
    "Electric": 4,
    "Light": 5,
    "Dark": 6
}

# Root folder for all sprite assets
SPRITE_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "sprites")
)

def sprite_path(name):
    return os.path.join(SPRITE_ROOT, name)

def load_scaled_sprite(name, scale=1.0, colorkey=None):
    """
    Loads a sprite from /sprites/, applies optional colorkey,
    and scales it by a multiplier.
    """
    path = sprite_path(name)
    img = pygame.image.load(path).convert()

    if colorkey is not None:
        img.set_colorkey(colorkey)

    w, h = img.get_size()
    img = pygame.transform.scale(img, (int(w * scale), int(h * scale)))
    return img

def key_confirm(key):
    return key in (pygame.K_z, pygame.K_RETURN)

def key_back(key):
    return key in (pygame.K_x, pygame.K_LSHIFT, pygame.K_RSHIFT)
