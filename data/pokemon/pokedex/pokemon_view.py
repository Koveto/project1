import os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
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

TYPES = [
    "normal", "fire", "water", "electric", "grass", "ice",
    "fighting", "poison", "ground", "flying", "psychic", "bug",
    "rock", "ghost", "dragon", "dark", "steel", "fairy"
]
TYPE_COLS = 6
TYPE_CELL_W = 100
TYPE_CELL_H = 32

# Move this higher than before
TYPE_GRID_X = PANEL_X
TYPE_GRID_Y = PANEL_Y + 220   # tweak this if you want it even higher



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
        # Input box for jumping to a Pokédex number
        # ---------------------------------------------------------
        self.input_text = ""
        self.input_active = False

        self.input_rect = pygame.Rect(PANEL_X, PANEL_Y + 500, 200, 32)
        self.input_color_inactive = (120, 120, 120)
        self.input_color_active = (200, 200, 200)
        self.input_color = self.input_color_inactive

        self.shiny = False
        self.button_sort_asc = pygame.Rect(50, 500, 180, 40)
        self.button_sort_desc = pygame.Rect(250, 500, 180, 40)
        self.button_sort_number = pygame.Rect(450, 500, 220, 40)


    # ---------------------------------------------------------
    # Event handling for input box
    # ---------------------------------------------------------
    def handle_event(self, event, controller):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Input box click
            if self.input_rect.collidepoint(event.pos):
                self.input_active = True
                self.input_color = self.input_color_active
            else:
                self.input_active = False
                self.input_color = self.input_color_inactive

            # Sprite click → toggle shiny
            pokemon = controller.get_current_pokemon()
            sprite = self.get_sprite(pokemon, is_shiny=self.shiny)
            if sprite is not None:
                rect = sprite.get_rect(center=(SPRITE_X, SPRITE_Y))
                if rect.collidepoint(event.pos):
                    self.shiny = not self.shiny


            if self.input_rect.collidepoint(event.pos):
                self.input_active = True
                self.input_color = self.input_color_active
            else:
                self.input_active = False
                self.input_color = self.input_color_inactive

            mx, my = event.pos

            # Sort ascending
            if self.button_sort_asc.collidepoint(mx, my):
                controller.sort_by_bst_ascending()

            # Sort descending
            if self.button_sort_desc.collidepoint(mx, my):
                controller.sort_by_bst_descending()
            
            # Sort number
            if self.button_sort_number.collidepoint(mx, my):
                controller.sort_by_number()


            
        if event.type == pygame.KEYDOWN and self.input_active:
            if event.key == pygame.K_BACKSPACE:
                self.input_text = self.input_text[:-1]

            elif event.key == pygame.K_RETURN:
                query = self.input_text.strip()

                # Number search
                if query.isdigit():
                    num = int(query)
                    if 1 <= num <= controller.max_pokemon:
                        controller.index = num - 1

                # Name search
                else:
                    idx = controller.find_by_name(query)
                    controller.index = idx

                self.input_text = ""

            else:
                if len(event.unicode) == 1 and event.unicode.isprintable():
                    self.input_text += event.unicode

    # ---------------------------------------------------------
    # Sprite loading
    # ---------------------------------------------------------
    def get_sprite(self, pokemon, is_shiny=False):
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

        # Special case: #201 has no sprite, and everything after shifts
        if gen == 2:
            if number == 201:
                return None
            if number >= 202:
                number_within_gen -= 1
        if gen == 3:
            # Missing sprite: #327
            if number == 327:
                return None
            if number >= 328:
                number_within_gen -= 1

            # Missing sprite: #353
            if number >= 352:
                number_within_gen += 1



        # Compute sprite index (2 sprites per Pokémon)
        sprite_index = (number_within_gen - 1) * 2

        key = (gen, sprite_index, is_shiny)

        if key not in self.sprite_cache:
            sprite = load_pokemon_sprite(
                gen=gen,
                index=sprite_index,
                scale=3,
                is_shiny=is_shiny
            )
            self.sprite_cache[key] = sprite

        return self.sprite_cache[key]

    # ---------------------------------------------------------
    # Stat bar drawing
    # ---------------------------------------------------------
    def draw_stat_bar(self, surface, x, y, value, max_value=255):
        bar_width = 260
        bar_height = 14
        fill_ratio = value / max_value
        fill_width = int(bar_width * fill_ratio)

        bg_rect = pygame.Rect(x, y, bar_width, bar_height)
        pygame.draw.rect(surface, (60, 60, 60), bg_rect, border_radius=4)

        fill_rect = pygame.Rect(x, y, fill_width, bar_height)
        pygame.draw.rect(surface, (80, 160, 255), fill_rect, border_radius=4)

        return y + bar_height + 10

    # ---------------------------------------------------------
    # Text helper
    # ---------------------------------------------------------
    def draw_text(self, surface, text, x, y, font, color=COLOR_TEXT):
        img = font.render(text, True, color)
        surface.blit(img, (x, y))
        return y + img.get_height() + 4

    # ---------------------------------------------------------
    # Main draw function
    # ---------------------------------------------------------
    def draw(self, screen):
        pokemon = self.controller.get_current_pokemon()

        # -----------------------------
        # Draw sprite
        # -----------------------------
        sprite = self.get_sprite(pokemon, is_shiny=self.shiny)

        if sprite is not None:
            rect = sprite.get_rect(center=(SPRITE_X, SPRITE_Y))
            screen.blit(sprite, rect)
        else:
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
        # -----------------------------
        # Draw info panel
        # -----------------------------
        x = PANEL_X
        y = PANEL_Y

        name_line = f"#{pokemon.number}  {pokemon.name}"
        y = self.draw_text(screen, name_line, x, y, self.font_title)

        type_line = " / ".join(pokemon.types)
        y = self.draw_text(screen, f"Type: {type_line}", x, y, self.font_text)

        # ⭐ Add Base Stat Total here
        y = self.draw_text(screen, f"BST: {pokemon.base_total}", x, y, self.font_text)

        stats = pokemon.stats

        # HP
        y = self.draw_text(screen, f"HP: {stats.hp}", x, y, self.font_text)
        y = self.draw_stat_bar(screen, x + 120, y - 20, stats.hp)

        # Attack
        y = self.draw_text(screen, f"ATK: {stats.atk}", x, y, self.font_text)
        y = self.draw_stat_bar(screen, x + 120, y - 20, stats.atk)

        # Defense
        y = self.draw_text(screen, f"DEF: {stats.defense}", x, y, self.font_text)
        y = self.draw_stat_bar(screen, x + 120, y - 20, stats.defense)

        # Sp. Atk
        y = self.draw_text(screen, f"SP.ATK: {stats.sp_atk}", x, y, self.font_text)
        y = self.draw_stat_bar(screen, x + 120, y - 20, stats.sp_atk)

        # Sp. Def
        y = self.draw_text(screen, f"SP.DEF: {stats.sp_def}", x, y, self.font_text)
        y = self.draw_stat_bar(screen, x + 120, y - 20, stats.sp_def)

        # Speed
        y = self.draw_text(screen, f"SPEED: {stats.speed}", x, y, self.font_text)
        y = self.draw_stat_bar(screen, x + 120, y - 20, stats.speed)


        # -----------------------------
        # Type Affinity Grid (4 columns)
        # -----------------------------
        weak, resist, immune = defensive_profile(pokemon)

        # Normalize to lowercase for matching
        weak = {w.lower() for w in weak}
        resist = {r.lower() for r in resist}
        immune = {i.lower() for i in immune}

        # All 18 Pokémon types in lowercase
        TYPES = [
            "normal", "fire", "water", "electric", "grass", "ice",
            "fighting", "poison", "ground", "flying", "psychic", "bug",
            "rock", "ghost", "dragon", "dark", "steel", "fairy"
        ]

        TYPE_COLS = 4
        TYPE_CELL_W = 120
        TYPE_CELL_H = 34

        # Move the grid higher
        TYPE_GRID_X = PANEL_X
        TYPE_GRID_Y = PANEL_Y + 220

        grid_x = TYPE_GRID_X
        grid_y = TYPE_GRID_Y

        for i, t in enumerate(TYPES):
            col = i % TYPE_COLS
            row = i // TYPE_COLS

            cell_x = grid_x + col * TYPE_CELL_W
            cell_y = grid_y + row * TYPE_CELL_H

            # Determine color box
            if t in weak:
                color = (255, 80, 80)      # red
            elif t in resist:
                color = (80, 200, 80)      # green
            elif t in immune:
                color = (255, 255, 255)    # white
            else:
                color = None

            # Draw color box under text
            if color is not None:
                pygame.draw.rect(
                    screen,
                    color,
                    pygame.Rect(cell_x, cell_y + 18, 60, 10),
                    border_radius=3
                )

            # Draw type text (capitalized for display)
            text_surface = self.font_text.render(t.title(), True, COLOR_TEXT)
            screen.blit(text_surface, (cell_x, cell_y))


        # -----------------------------
        # Draw input box
        # -----------------------------
        pygame.draw.rect(screen, self.input_color, self.input_rect, border_radius=4)

        txt_surface = self.font_text.render(self.input_text, True, (0, 0, 0))
        screen.blit(txt_surface, (self.input_rect.x + 8, self.input_rect.y + 6))

        label = self.font_text.render("Search:", True, COLOR_TEXT)
        screen.blit(label, (self.input_rect.x - 80, self.input_rect.y + 6))

        # Draw sort buttons
        pygame.draw.rect(screen, (200, 200, 200), self.button_sort_asc, border_radius=6)
        pygame.draw.rect(screen, (200, 200, 200), self.button_sort_desc, border_radius=6)
        pygame.draw.rect(screen, (200, 200, 200), self.button_sort_number, border_radius=6)

        asc_label = self.font_text.render("Sort BST Asc", True, (0, 0, 0))
        desc_label = self.font_text.render("Sort BST Dsc", True, (0, 0, 0))
        num_label = self.font_text.render("Sort by Pokédex #", True, (0, 0, 0))

        screen.blit(asc_label, (self.button_sort_asc.x + 20, self.button_sort_asc.y + 8))
        screen.blit(desc_label, (self.button_sort_desc.x + 20, self.button_sort_desc.y + 8))
        screen.blit(num_label, (self.button_sort_number.x + 20, self.button_sort_number.y + 8))