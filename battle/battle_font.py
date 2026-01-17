# battle/battle_font.py

import pygame
import os

class BattleFont:
    """
    Loads and renders text using sprites/font1.png.
    Each glyph is 7x11 in the sheet, scaled ×4 for display.
    """

    GLYPH_W = 7
    GLYPH_H = 13
    SCALE = 4

    COLS = 26
    ROWS = 3

    def __init__(self):
        root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        font_path = os.path.join(root, "sprites", "font3.png")

        # Load sheet (white = transparent)
        sheet = pygame.image.load(font_path).convert()
        sheet.set_colorkey((255, 255, 255))

        self.glyphs = {}
        self._slice_sheet(sheet)

    # ---------------------------------------------------------
    # Slice spritesheet into glyphs (scaled ×4)
    # ---------------------------------------------------------

    def _slice_sheet(self, sheet):
        """
        Cuts the 182x33 sheet into 7x11 glyphs, scales them ×4,
        and maps characters.
        """

        # Row 0: A-Z
        for i in range(26):
            rect = pygame.Rect(
                i * self.GLYPH_W,
                0,
                self.GLYPH_W,
                self.GLYPH_H
            )
            glyph = sheet.subsurface(rect)
            glyph = pygame.transform.scale(
                glyph,
                (self.GLYPH_W * self.SCALE, self.GLYPH_H * self.SCALE)
            )
            self.glyphs[chr(ord('A') + i)] = glyph

        # Row 1: a-z
        for i in range(26):
            rect = pygame.Rect(
                i * self.GLYPH_W,
                self.GLYPH_H,
                self.GLYPH_W,
                self.GLYPH_H
            )
            glyph = sheet.subsurface(rect)
            glyph = pygame.transform.scale(
                glyph,
                (self.GLYPH_W * self.SCALE, self.GLYPH_H * self.SCALE)
            )
            self.glyphs[chr(ord('a') + i)] = glyph

        # Row 2: digits + punctuation
        row2 = "0123456789!?.-\"\"''"

        for i, ch in enumerate(row2):
            rect = pygame.Rect(
                i * self.GLYPH_W,
                self.GLYPH_H * 2,
                self.GLYPH_W,
                self.GLYPH_H
            )
            glyph = sheet.subsurface(rect)
            glyph = pygame.transform.scale(
                glyph,
                (self.GLYPH_W * self.SCALE, self.GLYPH_H * self.SCALE)
            )
            self.glyphs[ch] = glyph

        # Space is blank
        blank = pygame.Surface(
            (self.GLYPH_W * self.SCALE, self.GLYPH_H * self.SCALE),
            pygame.SRCALPHA
        )
        self.glyphs[" "] = blank

    # ---------------------------------------------------------
    # Draw text
    # ---------------------------------------------------------

    def draw_text(self, screen, text, x, y):
        """
        Draws text using the scaled bitmap font.
        """
        cx = x
        for ch in text:
            glyph = self.glyphs.get(ch)
            if glyph:
                screen.blit(glyph, (cx, y))
            cx += self.GLYPH_W * self.SCALE
