import pygame

SPRITE_W = 240
SPRITE_H = 112
SCALE = 4

def load_battle_background(index):
    """
    Loads one background (0–15) from sprites/battlebackgrounds.png.
    Returns a scaled 960×448 surface.
    """

    sheet = pygame.image.load("sprites/battlebackgrounds.png").convert_alpha()

    # Compute row/column in 4×4 grid
    col = index % 4
    row = index // 4

    x = col * SPRITE_W
    y = row * SPRITE_H

    # Extract the subsurface
    rect = pygame.Rect(x, y, SPRITE_W, SPRITE_H)
    bg = sheet.subsurface(rect)

    # Scale ×4
    bg = pygame.transform.scale(bg, (SPRITE_W * SCALE, SPRITE_H * SCALE))

    return bg
