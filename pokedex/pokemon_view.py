import pygame
from pokedex.ui_layout import (
    SPRITE_X, SPRITE_Y,
    PANEL_X, PANEL_Y, PANEL_WIDTH,
    FONT_PATH, FONT_SIZE_TITLE, FONT_SIZE_TEXT,
    COLOR_TEXT
)
from pokedex.pokemon_sprites import load_pokemon_sprite


# ---------------------------------------------------------
# SMT ELEMENTS
# ---------------------------------------------------------
ELEMENTS = ["Physical", "Fire", "Force", "Ice", "Electric", "Light", "Dark"]

TYPE_COLS = 4
TYPE_CELL_W = 140
TYPE_CELL_H = 40

TYPE_GRID_X = PANEL_X
TYPE_GRID_Y = PANEL_Y + 220


class PokemonView:
    """
    Handles all drawing of the current Pokémon:
    sprite, name, stats, affinities, etc.
    """

    def __init__(self, controller):
        self.controller = controller

        # Load fonts
        self.font_title = pygame.font.Font(FONT_PATH, FONT_SIZE_TITLE)
        self.font_text = pygame.font.Font(FONT_PATH, FONT_SIZE_TEXT)

        # Cache for sprites
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

        self.col = 0

        # Sorting buttons
        self.button_sort_asc = pygame.Rect(50, 500, 180, 40)
        self.button_sort_desc = pygame.Rect(250, 500, 180, 40)
        self.button_sort_number = pygame.Rect(450, 500, 220, 40)

        self.stat_rects = {}
        self.element_rects = []


    # ---------------------------------------------------------
    # Event handling
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
            sprite = self.get_sprite(pokemon)
            if sprite is not None:
                rect = sprite.get_rect(center=(SPRITE_X, SPRITE_Y))
                if rect.collidepoint(event.pos):
                    self.col = (self.col + 1) % 10

            mx, my = event.pos

            # Sort ascending
            if self.button_sort_asc.collidepoint(mx, my):
                controller.sort_by_bst_ascending()

            # Sort descending
            if self.button_sort_desc.collidepoint(mx, my):
                controller.sort_by_bst_descending()

            # Sort by number
            if self.button_sort_number.collidepoint(mx, my):
                controller.sort_by_number()

            # Click on stat bars
            for stat, rect in self.stat_rects.items():
                if rect.collidepoint(event.pos):
                    controller.sort_by_stat(stat)
                    return

            # Click on element affinities
            for i, rect in enumerate(self.element_rects):
                if rect.collidepoint(event.pos):
                    controller.sort_by_affinity(i)
                    return



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
    def get_sprite(self, pokemon):
        """
        Returns a cached Pygame sprite for this Pokémon using the new giant sheet.
        """
        if pokemon is None:
            return None

        row = pokemon.pokedex_number - 1
        col = self.col

        key = (row, col)

        if key not in self.sprite_cache:
            sprite = load_pokemon_sprite(
                row=row,
                column=col,
                scale=3
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
        sprite = self.get_sprite(pokemon)

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
        x = PANEL_X
        y = PANEL_Y

        name_line = f"#{pokemon.pokedex_number}  {pokemon.name}"
        y = self.draw_text(screen, name_line, x, y, self.font_title)

        # Base Stat Total
        y = self.draw_text(screen, f"BST: {pokemon.bst}", x, y, self.font_text)

        # Level (NEW)
        y = self.draw_text(screen, f"Level: {pokemon.level}", x, y, self.font_text)

        base_stats = pokemon.base_stats

        # HP
        y = self.draw_text(screen, f"HP: {base_stats["hp"]}", x, y, self.font_text)
        bar_x = x + 120
        bar_y = y - 20
        self.stat_rects["hp"] = pygame.Rect(bar_x, bar_y, 260, 14)
        y = self.draw_stat_bar(screen, bar_x, bar_y, base_stats["hp"])

        # Attack
        y = self.draw_text(screen, f"ATK: {base_stats["atk"]}", x, y, self.font_text)
        bar_x = x + 120
        bar_y = y - 20
        self.stat_rects["atk"] = pygame.Rect(bar_x, bar_y, 260, 14)
        y = self.draw_stat_bar(screen, bar_x, bar_y, base_stats["atk"])

        # def
        y = self.draw_text(screen, f"DEF: {base_stats["def"]}", x, y, self.font_text)
        bar_x = x + 120
        bar_y = y - 20
        self.stat_rects["def"] = pygame.Rect(bar_x, bar_y, 260, 14)
        y = self.draw_stat_bar(screen, bar_x, bar_y, base_stats["def"])

        # Sp. Atk
        y = self.draw_text(screen, f"SP.ATK: {base_stats["spatk"]}", x, y, self.font_text)
        bar_x = x + 120
        bar_y = y - 20
        self.stat_rects["spatk"] = pygame.Rect(bar_x, bar_y, 260, 14)
        y = self.draw_stat_bar(screen, bar_x, bar_y, base_stats["spatk"])

        # Sp. Def
        y = self.draw_text(screen, f"SP.DEF: {base_stats["spdef"]}", x, y, self.font_text)
        bar_x = x + 120
        bar_y = y - 20
        self.stat_rects["spdef"] = pygame.Rect(bar_x, bar_y, 260, 14)
        y = self.draw_stat_bar(screen, bar_x, bar_y, base_stats["spdef"])

        # spd
        y = self.draw_text(screen, f"SPD: {base_stats["spd"]}", x, y, self.font_text)
        bar_x = x + 120
        bar_y = y - 20
        self.stat_rects["spd"] = pygame.Rect(bar_x, bar_y, 260, 14)
        y = self.draw_stat_bar(screen, bar_x, bar_y, base_stats["spd"])


        # -----------------------------
        # SMT ELEMENT AFFINITY GRID
        # -----------------------------
        affinities = pokemon.affinities

        grid_x = TYPE_GRID_X
        grid_y = TYPE_GRID_Y

        self.element_rects = []

        for i, elem in enumerate(ELEMENTS):
            col = i % TYPE_COLS
            row = i // TYPE_COLS

            cell_x = grid_x + col * TYPE_CELL_W
            cell_y = grid_y + row * TYPE_CELL_H

            val = affinities[i]

            # Determine color
            if val < 0:
                color = (255, 80, 80)        # red
            elif 1 <= val < 3:
                color = (80, 200, 80)        # green
            elif 3 <= val < 9:
                color = (80, 80, 255)        # blue
            elif val == 9:
                color = (255, 255, 255)      # white
            else:
                color = None

            # Draw color box
            rect = pygame.Rect(cell_x, cell_y + 18, 60, 12)
            self.element_rects.append(rect)

            if color is not None:
                pygame.draw.rect(
                    screen,
                    color,
                    rect,
                    border_radius=3
                )

            # Draw element name
            text_surface = self.font_text.render(elem, True, COLOR_TEXT)
            screen.blit(text_surface, (cell_x, cell_y))


        # -----------------------------
        # Draw input box
        # -----------------------------
        pygame.draw.rect(screen, self.input_color, self.input_rect, border_radius=4)

        txt_surface = self.font_text.render(self.input_text, True, (0, 0, 0))
        screen.blit(txt_surface, (self.input_rect.x + 8, self.input_rect.y + 6))

        label = self.font_text.render("Search:", True, COLOR_TEXT)
        screen.blit(label, (self.input_rect.x - 80, self.input_rect.y + 6))

        # -----------------------------
        # Draw sort buttons
        # -----------------------------
        pygame.draw.rect(screen, (200, 200, 200), self.button_sort_asc, border_radius=6)
        pygame.draw.rect(screen, (200, 200, 200), self.button_sort_desc, border_radius=6)
        pygame.draw.rect(screen, (200, 200, 200), self.button_sort_number, border_radius=6)

        asc_label = self.font_text.render("Sort BST Asc", True, (0, 0, 0))
        desc_label = self.font_text.render("Sort BST Dsc", True, (0, 0, 0))
        num_label = self.font_text.render("Sort by Pokédex #", True, (0, 0, 0))

        screen.blit(asc_label, (self.button_sort_asc.x + 20, self.button_sort_asc.y + 8))
        screen.blit(desc_label, (self.button_sort_desc.x + 20, self.button_sort_desc.y + 8))
        screen.blit(num_label, (self.button_sort_number.x + 20, self.button_sort_number.y + 8))
