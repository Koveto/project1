# battle/battle_renderer.py

import pygame, os
from battle.battle_font import BattleFont
from pokedex.pokemon_sprites import load_pokemon_sprite, load_player_sprite

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
FRAME_PATH = os.path.join(ROOT, "sprites", "battleframe.png")
FRAME_W = 240
FRAME_H = 48

class BattleRenderer:

    def __init__(self, background_surface, model):
        self.background = background_surface
        self.model = model
        self.font = BattleFont()
        self.cursor_sprite = self.load_cursor_sprite()

        # Preload sprites for player team (None → None)
        self.player_sprites = [
            self._load_sprite_for_pokemon(p, is_back=True) if p is not None else None
            for p in model.player_team
        ]

        # Preload sprites for enemy team (None → None)
        self.enemy_sprites = [
            self._load_sprite_for_pokemon(p, is_back=False) if p is not None else None
            for p in model.enemy_team
        ]

        self.battleframe = self.load_battle_frame()

        # Layout constants
        self.PLAYER_BASE_X = -64
        self.PLAYER_Y = 192
        self.PLAYER_SPACING = 150

        self.ENEMY_BASE_X = 148
        self.ENEMY_Y = 0
        self.ENEMY_SPACING = 182

        self.PLAYER_OFFSET = 50  # player character offset

        self.menu_positions = [
            (65, 525),   # Skills
            (316, 525),  # Item
            (536, 525),  # Guard
            (765, 525),  # Talk
            (65, 573),   # Change
            (316, 573),  # Escape
            (536, 573),  # Pass
        ]

    # ---------------------------------------------------------
    # Sprite loading
    # ---------------------------------------------------------

    def _load_sprite_for_pokemon(self, pokemon, is_back):
        """
        Loads either:
        - the player sprite (if pokedex_number == -1)
        - a Pokémon sprite (normal rules)
        """
        if pokemon is None:
            return None

        if pokemon.is_player:
            return load_player_sprite(scale=4)

        dex = pokemon.pokedex_number

        if is_back:
            index = dex - 1
        else:
            index = (dex * 2) - 2

        return load_pokemon_sprite(
            gen=pokemon.gen,
            index=index,
            is_shiny=pokemon.is_shiny,
            is_back=is_back,
            scale=4
        )
    
    def load_cursor_sprite(self, scale=4):
        root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        path = os.path.join(root, "sprites", "cursor.png")

        img = pygame.image.load(path).convert()
        img.set_colorkey((255, 255, 255))  # white = transparent

        w, h = img.get_size()
        img = pygame.transform.scale(img, (w * scale, h * scale))
        return img

    
    def load_battle_frame(self, scale=4):
        """
        Loads sprites/battleframe.png (240x48, no alpha).
        Returns a scaled pygame.Surface.
        """

        # Resolve path relative to battle/ folder
        root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        frame_path = os.path.join(root, "sprites", "battleframe.png")

        # Raw size
        FRAME_W = 240
        FRAME_H = 48

        # Load (no alpha → convert())
        img = pygame.image.load(frame_path).convert()

        # Scale
        scaled = pygame.transform.scale(
            img,
            (FRAME_W * scale, FRAME_H * scale)
        )

        return scaled


    # ---------------------------------------------------------
    # Drawing
    # ---------------------------------------------------------

    def draw(self, screen, menu_index):
        screen.blit(self.battleframe, (0, 448))

        # Background
        screen.blit(self.background, (0, 0))

        # Enemy Pokémon
        for i, sprite in enumerate(self.enemy_sprites):
            if sprite is None:
                continue  # skip empty slots

            x = self.ENEMY_BASE_X + i * self.ENEMY_SPACING
            screen.blit(sprite, (x, self.ENEMY_Y))

        # Player-side sprites (Pokémon + player)
        for i, sprite in enumerate(self.player_sprites):
            if sprite is None:
                continue  # skip empty slots

            pokemon = self.model.player_team[i]

            # Base slot = index
            slot = i
            x = self.PLAYER_BASE_X + slot * self.PLAYER_SPACING

            if pokemon.is_player:
                # Player special-case drawing
                x += self.PLAYER_OFFSET
                y = self.PLAYER_Y + 48
            else:
                # Normal Pokémon
                y = self.PLAYER_Y

            screen.blit(sprite, (x, y))

    
        self.font.draw_text(screen, "What will Brendan do?", 40, 470)
        self.font.draw_text(screen, "  Skills   Item    Guard   Talk", 40, 517)
        self.font.draw_text(screen, "  Change   Escape  Pass", 40, 565)

        # Draw cursor next to selected option
        cursor_x, cursor_y = self.menu_positions[menu_index]
        screen.blit(self.cursor_sprite, (cursor_x, cursor_y))

