# battle/battle_renderer.py

import pygame, os, math
from battle.battle_font import BattleFont
from pokedex.pokemon_sprites import load_pokemon_sprite, load_player_sprite
from constants import load_scaled_sprite

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
FRAME_PATH = os.path.join(ROOT, "sprites", "battleframe.png")
FRAME_W = 240
FRAME_H = 48
PT_X = 820
PT_Y = 305
PT_SPACING = 34
HP_BAR_HEIGHT = 8
MP_BAR_HEIGHT = 8
HP_BAR_X = 748   # where the HP fill starts on screen
HP_BAR_Y = 396
HP_BAR_WIDTH = 192   # how wide the HP bar can be
MP_BAR_X = 748
MP_BAR_Y = 416
MP_BAR_WIDTH = 192


class BattleRenderer:

    def __init__(self, background_surface, model):
        self.background = background_surface
        self.model = model

        self.font0 = BattleFont("font3.png", glyph_w=7, glyph_h=13, scale=4, spacing=28)
        self.font1 = BattleFont("font5.png", glyph_w=7, glyph_h=13, scale=3, spacing=16)

        root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        sprite_path = lambda name: os.path.join(root, "sprites", name)

        # --- Universal sprite loading ---
        self.hp_fill = load_scaled_sprite(
            sprite_path("hpfill.png"), 
            scale=4
        )
        
        self.mp_fill = load_scaled_sprite(
            sprite_path("mpfill.png"), 
            scale=4
        )

        self.cursor_sprite = load_scaled_sprite(
            sprite_path("cursor.png"),
            scale=4,
            colorkey=(255, 255, 255)   # white transparent
        )

        self.hpmp_sprite = load_scaled_sprite(
            sprite_path("hpmp.png"),
            scale=4,
            colorkey=(255, 0, 228)     # magenta transparent
        )

        self.lv_sprite = load_scaled_sprite(
            sprite_path("lv.png"),
            scale=3,
            colorkey=None              # no transparency
        )

        # Press Turn icons (new)
        self.press_turn_red = load_scaled_sprite(
            sprite_path("pokeballred.png"),
            scale=2,
            colorkey=(255, 0, 228)
        )

        self.press_turn_blue = load_scaled_sprite(
            sprite_path("pokeballblue.png"),
            scale=2,
            colorkey=(255, 0, 228)
        )

        # --- Pokémon sprites ---
        self.player_sprites = [
            self._load_sprite_for_pokemon(p, is_back=True) if p else None
            for p in model.player_team
        ]

        self.enemy_sprites = [
            self._load_sprite_for_pokemon(p, is_back=False) if p else None
            for p in model.enemy_team
        ]

        # --- Battle frame ---
        self.battleframe = self.load_battle_frame()

        # Layout constants
        self.PLAYER_BASE_X = -64
        self.PLAYER_Y = 192
        self.PLAYER_SPACING = 150

        self.ENEMY_BASE_X = 300
        self.ENEMY_Y = 0
        self.ENEMY_SPACING = 152

        self.PLAYER_OFFSET = 50

        self.menu_positions = [
            (65, 525), (316, 525), (536, 525), (765, 525),
            (65, 573), (316, 573), (536, 573), (765, 573)
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
    def draw_press_turn_icon(self, screen, state, x, y):
        if state == "transparent":
            return

        if state == "solid_blue":
            screen.blit(self.press_turn_blue, (x, y))
        elif state == "solid_red":
            screen.blit(self.press_turn_red, (x, y))
        elif state == "flash_blue":
            # Flashing: draw only on “on” frames
            if (self.anim_frame // 10) % 2 == 0:
                screen.blit(self.press_turn_blue, (x, y))
        elif state == "flash_red":
            if (self.anim_frame // 10) % 2 == 0:
                screen.blit(self.press_turn_red, (x, y))

    def draw_hp_bar(self, screen, pokemon, hp_offset):
        if pokemon.max_hp <= 0:
            return

        ratio = pokemon.remaining_hp / pokemon.max_hp
        ratio = max(0.0, min(1.0, ratio))

        fill_width = int(HP_BAR_WIDTH * ratio)
        if fill_width <= 0:
            return

        fill_surface = pygame.transform.scale(
            self.hp_fill,
            (fill_width, HP_BAR_HEIGHT)
        )
        screen.blit(fill_surface, (HP_BAR_X, HP_BAR_Y + hp_offset))

    def draw_mp_bar(self, screen, pokemon, hp_offset):
        if pokemon.max_mp <= 0:
            return

        ratio = pokemon.remaining_mp / pokemon.max_mp
        ratio = max(0.0, min(1.0, ratio))

        fill_width = int(MP_BAR_WIDTH * ratio)
        if fill_width <= 0:
            return

        fill_surface = pygame.transform.scale(
            self.mp_fill,
            (fill_width, MP_BAR_HEIGHT)
        )
        screen.blit(fill_surface, (MP_BAR_X, MP_BAR_Y + hp_offset))

    def draw(self, screen, menu_index, menu_mode, previous_menu_index):

        # ---------------------------------------------------------
        # Active Pokémon based on turn_index
        # ---------------------------------------------------------
        active_index = self.model.turn_index
        active_pokemon = self.model.player_team[active_index]

        self.anim_frame += 1

        AMP = 8
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
        # Desired draw order: 1, 3, 0, 2
        draw_order = [1, 3, 0, 2]

        for i in draw_order:
            sprite = self.enemy_sprites[i]
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
                y = self.PLAYER_Y + 16

            # Apply bounce to the active party member (including Brendan if index 0)
            if i == active_index:
                y += poke_offset

            screen.blit(sprite, (x, y))

        
        # ---------------------------------------------------------
        # HP/MP + Frame
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
        self.draw_hp_bar(screen, active_pokemon, hp_offset)
        self.draw_mp_bar(screen, active_pokemon, hp_offset)
        screen.blit(self.battleframe, (0, 448))

        # ---------------------------------------------------------
        # Press Turn Icons
        # ---------------------------------------------------------
        press_turn_states = self.model.get_press_turn_icon_states(self.anim_frame)

        for i, state in enumerate(press_turn_states):
            x = PT_X + i * PT_SPACING   # left → right
            y = PT_Y + hp_offset
            self.draw_press_turn_icon(screen, state, x, y)

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

