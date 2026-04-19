import pygame
import os

class StatIconRenderer:
    """
    Loads and draws the 24x24 buff/debuff icons.
    Sheet layout (rows):
        0 = Attack
        1 = Defense
        2 = Speed

    Columns:
        0 = +1
        1 = +2
        2 = -1
        3 = -2
    """

    ICON_W = 24
    ICON_H = 24

    def __init__(self):
        root = os.path.abspath(os.path.join(os.path.join(os.path.dirname(__file__), ".."), ".."))
        sheet_path = os.path.join(root, "sprites", "statbuffdebuff.png")

        self.sheet = pygame.image.load(sheet_path).convert_alpha()

        # Pre-slice all 12 icons
        self.icons = {}  # (row, col) → Surface
        self._slice_sheet()

    def _slice_sheet(self):
        for row in range(3):      # attack, defense, speed
            for col in range(4):  # +1, +2, -1, -2
                rect = pygame.Rect(
                    col * self.ICON_W,
                    row * self.ICON_H,
                    self.ICON_W,
                    self.ICON_H
                )
                icon = self.sheet.subsurface(rect)
                self.icons[(row, col)] = icon

    def draw_buff_icon(self, screen, stat_row, stage_col, x, y):
        """
        stat_row: 0=Atk, 1=Def, 2=Spd
        stage_col: 0=+1, 1=+2, 2=-1, 3=-2
        """
        icon = self.icons.get((stat_row, stage_col))
        if icon:
            screen.blit(icon, (x, y))
