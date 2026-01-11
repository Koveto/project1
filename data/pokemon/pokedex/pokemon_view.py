import os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(ROOT)
import pygame
from ui_layout import (
    SPRITE_X, SPRITE_Y,
    PANEL_X, PANEL_Y, PANEL_WIDTH,
    FONT_PATH, FONT_SIZE_TITLE, FONT_SIZE_TEXT,
    COLOR_TEXT
)
from pokemon_sprites import load_pokemon_sprite
from pokemon_typechart import defensive_profile


class PokemonView:
    """
    Handles all drawing of the current Pokémon:
    sprite, name, types, stats, weaknesses, etc.
    """

    def __init__(self, controller):
        self.controller = controller

        # Load fonts
        self.font_title = pygame.font.Font(FONT_PATH, FONT_SIZE_TITLE)
        self.font_text = pygame.font.Font(FONT_PATH, FONT_SIZE_TEXT)

        # Cache for sprites so we don't reload every frame
        self.sprite_cache = {}

    # ---------------------------------------------------------
    # Sprite loading
    # ---------------------------------------------------------
    def get_sprite(self, pokemon):
        number = pokemon.number

        # Determine generation and starting index
        if number <= 151:
            gen = 1
            gen_start = 1
        elif number <= 251:
            gen = 2
            gen_start = 152
        else:
            gen = 3
            gen_start = 252

        # Compute number within generation
        number_within_gen = number - gen_start + 1

        # -----------------------------
        # Special case handling for #201
        # -----------------------------
        if gen == 2:
            if number == 201:
                return None  # No sprite for #201

            if number >= 202:
                number_within_gen -= 1  # Shift forward by 1
        # -----------------------------

        # Compute sprite index (2 sprites per Pokémon)
        sprite_index = (number_within_gen - 1) * 2

        key = (gen, sprite_index)

        if key not in self.sprite_cache:
            sprite = load_pokemon_sprite(
                gen=gen,
                index=sprite_index,
                scale=3
            )
            self.sprite_cache[key] = sprite

        return self.sprite_cache[key]




    # ---------------------------------------------------------
    # Text helpers
    # ---------------------------------------------------------
    def draw_text(self, surface, text, x, y, font, color=COLOR_TEXT):
        img = font.render(text, True, color)
        surface.blit(img, (x, y))
        return y + img.get_height() + 4  # next line position

    # ---------------------------------------------------------
    # Main draw function
    # ---------------------------------------------------------
    def draw(self, screen):
        pokemon = self.controller.get_current_pokemon()

        # -----------------------------
        # Draw sprite
        # -----------------------------
        sprite = self.get_sprite(pokemon)

        if sprite is not None:
            rect = sprite.get_rect(center=(SPRITE_X, SPRITE_Y))
            screen.blit(sprite, rect)
        else:
            # Draw a placeholder message for Pokémon with no sprite
            self.draw_text(
                screen,
                "No sprite available",
                SPRITE_X - 80,
                SPRITE_Y - 20,
                self.font_text
            )


        # -----------------------------
        # Draw info panel
        # -----------------------------
        x = PANEL_X
        y = PANEL_Y

        # Name + number
        name_line = f"#{pokemon.number}  {pokemon.name}"
        y = self.draw_text(screen, name_line, x, y, self.font_title)

        # Types
        type_line = " / ".join(pokemon.types)
        y = self.draw_text(screen, f"Type: {type_line}", x, y, self.font_text)

        # Base stats
        stats = pokemon.stats
        y = self.draw_text(screen, f"HP: {stats.hp}", x, y, self.font_text)
        y = self.draw_text(screen, f"ATK: {stats.atk}", x, y, self.font_text)
        y = self.draw_text(screen, f"DEF: {stats.defense}", x, y, self.font_text)
        y = self.draw_text(screen, f"SP.ATK: {stats.sp_atk}", x, y, self.font_text)
        y = self.draw_text(screen, f"SP.DEF: {stats.sp_def}", x, y, self.font_text)
        y = self.draw_text(screen, f"SPEED: {stats.speed}", x, y, self.font_text)

        # Weaknesses / Resistances / Immunities
        weak, resist, immune = defensive_profile(pokemon)

        y += 10
        y = self.draw_text(screen, "Weaknesses:", x, y, self.font_text)
        for w in weak:
            y = self.draw_text(screen, f"  - {w}", x, y, self.font_text)

        y += 6
        y = self.draw_text(screen, "Resistances:", x, y, self.font_text)
        for r in resist:
            y = self.draw_text(screen, f"  - {r}", x, y, self.font_text)

        y += 6
        y = self.draw_text(screen, "Immunities:", x, y, self.font_text)
        for i in immune:
            y = self.draw_text(screen, f"  - {i}", x, y, self.font_text)
