# battle/battle_renderer.py

import pygame, os, math
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
        self.font0 = BattleFont("font3.png", glyph_w=7, glyph_h=13, scale=4, spacing=28)
        self.font1 = BattleFont("font5.png", glyph_w=7, glyph_h=13, scale=3, spacing=16)
        self.cursor_sprite = self.load_cursor_sprite()
        self.hpmp_sprite = self.load_hpmp_sprite()
        self.lv_sprite = self.load_lv_sprite(scale=3)

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

        self.ENEMY_BASE_X = 300
        self.ENEMY_Y = 0
        self.ENEMY_SPACING = 152

        self.PLAYER_OFFSET = 50  # player character offset

        self.menu_positions = [
            (65, 525),   # Skills
            (316, 525),  # Item
            (536, 525),  # Guard
            (765, 525),  # Talk
            (65, 573),   # Change
            (316, 573),  # Escape
            (536, 573),  # Pass
            (765, 573)   # Info
        ]

        self.anim_frame = 0

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
    
    def load_hpmp_sprite(self, scale=4):
        root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        path = os.path.join(root, "sprites", "hpmp.png")

        img = pygame.image.load(path).convert()

        # FF00E4 → transparent
        img.set_colorkey((255, 0, 228))

        w, h = img.get_size()
        img = pygame.transform.scale(img, (w * scale, h * scale))

        return img

    def load_lv_sprite(self, scale=4):
        root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        path = os.path.join(root, "sprites", "lv.png")

        img = pygame.image.load(path).convert()   # no alpha → convert()

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

    def draw(self, screen, menu_index, menu_mode, previous_menu_index):

        # ---------------------------------------------------------
        # Active Pokémon based on turn_index
        # ---------------------------------------------------------
        active_index = self.model.turn_index
        active_pokemon = self.model.player_team[active_index]

        self.anim_frame += 1

        AMP = 4
        SPEED = 0.18

        poke_offset = int(AMP * math.sin(self.anim_frame * SPEED))
        hp_offset = int(-AMP * math.sin(self.anim_frame * SPEED + 0.6))

        # ---------------------------------------------------------
        # Background + battleframe
        # ---------------------------------------------------------
        screen.blit(self.background, (0, 0))

        # ---------------------------------------------------------
        # Enemy Pokémon (no HP/MP box for now)
        # ---------------------------------------------------------
        for i, sprite in enumerate(self.enemy_sprites):
            if sprite is None:
                continue

            x = self.ENEMY_BASE_X + i * self.ENEMY_SPACING
            screen.blit(sprite, (x, self.ENEMY_Y))

        # ---------------------------------------------------------
        # Player-side sprites (Pokémon + player)
        # ---------------------------------------------------------
        for i, sprite in enumerate(self.player_sprites):
            if sprite is None:
                continue

            pokemon = self.model.player_team[i]

            slot = i
            x = self.PLAYER_BASE_X + slot * self.PLAYER_SPACING

            if pokemon.is_player:
                # Player sprite base position
                x += self.PLAYER_OFFSET
                y = self.PLAYER_Y + 64
            else:
                # Normal Pokémon base position
                y = self.PLAYER_Y

            # Apply bounce to the active party member (including Brendan if index 0)
            if i == active_index:
                y += poke_offset

            screen.blit(sprite, (x, y))

        
        # ---------------------------------------------------------
        # HP/MP
        # ---------------------------------------------------------
        """
        screen.blit(self.hpmp_sprite, (0, 0))
        self.font1.draw_text(screen, p.name, 20, 14)
        screen.blit(self.lv_sprite, (205, 23))
        self.font1.draw_text(screen, str(p.level), 230, 14)
        """
        hpmp_y = 328 + hp_offset
        screen.blit(self.hpmp_sprite, (672, hpmp_y))
        self.font1.draw_text(screen, active_pokemon.name, 692, hpmp_y + 14)
        screen.blit(self.lv_sprite, (877, hpmp_y + 23))
        self.font1.draw_text(screen, str(active_pokemon.level), 902, hpmp_y + 14)
        
        screen.blit(self.battleframe, (0, 448))

        # ---------------------------------------------------------
        # Menu text
        # ---------------------------------------------------------
        if menu_mode == "main":
            self.font0.draw_text(screen, f"What will {active_pokemon.name} do?", 40, 470)
            self.font0.draw_text(screen, "  Skills   Item    Guard   Talk", 40, 517)
            self.font0.draw_text(screen, "  Change   Escape  Pass    Info", 40, 565)

            cursor_x, cursor_y = self.menu_positions[menu_index]
            screen.blit(self.cursor_sprite, (cursor_x, cursor_y))
        else:
            dummy_texts = [
                "Skills submenu placeholder",
                "Item submenu placeholder",
                "Guard submenu placeholder",
                "Talk submenu placeholder",
                "Change submenu placeholder",
                "Escape submenu placeholder",
                "Pass submenu placeholder",
                "Info submenu placeholder"
            ]

            msg = dummy_texts[previous_menu_index]
            self.font0.draw_text(screen, msg, 40, 470)
            self.font0.draw_text(screen, "(Press X to return)", 40, 517)
