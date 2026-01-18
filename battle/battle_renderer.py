# battle/battle_renderer.py

import pygame, math
from constants import *
from battle.battle_constants import *
from battle.battle_font import BattleFont
from pokedex.pokemon_sprites import load_pokemon_sprite, load_player_sprite
from data.smt.smt_moves import load_moves

class BattleRenderer:

    def __init__(self, background_surface, model):
        self.background = background_surface
        self.model = model

        self.font0 = BattleFont(FONT0_FILENAME, glyph_w=FONT0_WIDTH, glyph_h=FONT0_HEIGHT, scale=FONT0_SCALE, spacing=FONT0_SPACING)
        self.font1 = BattleFont(FONT1_FILENAME, glyph_w=FONT1_WIDTH, glyph_h=FONT1_HEIGHT, scale=FONT1_SCALE, spacing=FONT1_SPACING)
        self.font2 = BattleFont(FONT2_FILENAME, glyph_w=FONT2_WIDTH, glyph_h=FONT2_HEIGHT, scale=FONT2_SCALE, spacing=FONT2_SPACING)

        # --- Universal sprite loading ---
        self.hp_fill = load_scaled_sprite(
            sprite_path(FILENAME_HPFILL), 
            scale=SCALE
        )
        
        self.mp_fill = load_scaled_sprite(
            sprite_path(FILENAME_MPFILL), 
            scale=SCALE
        )

        self.cursor_sprite = load_scaled_sprite(
            sprite_path(FILENAME_CURSOR),
            scale=SCALE,
            colorkey=COLOR_WHITE
        )

        self.hpmp_sprite = load_scaled_sprite(
            sprite_path(FILENAME_HPMP),
            scale=SCALE,
            colorkey=COLOR_MAGENTA
        )

        self.lv_sprite = load_scaled_sprite(
            sprite_path(FILENAME_LV),
            scale=FONT1_SCALE
        )

        self.battleframe = load_scaled_sprite(
            sprite_path(FILENAME_FRAME),
            scale=SCALE,
        )

        # Press Turn icons (new)
        self.press_turn_red = load_scaled_sprite(
            sprite_path(FILENAME_PBRED),
            scale=SCALE_PRESSTURN,
            colorkey=COLOR_MAGENTA
        )

        self.press_turn_blue = load_scaled_sprite(
            sprite_path(FILENAME_PBBLUE),
            scale=SCALE_PRESSTURN,
            colorkey=COLOR_MAGENTA
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

        

        self.anim_frame = 0
        
        self.smt_moves = load_moves(FILENAME_MOVES)



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
            return load_player_sprite(scale=SCALE)

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
            scale=SCALE
        )

    # ---------------------------------------------------------
    # Drawing
    # ---------------------------------------------------------
    def draw_press_turn_icon(self, screen, state, x, y):
        if state == PT_STATE_TRANSPARENT:
            return

        if state == PT_STATE_SOLIDBLUE:
            screen.blit(self.press_turn_blue, (x, y))
        elif state == PT_STATE_SOLIDRED:
            screen.blit(self.press_turn_red, (x, y))
        elif state == PT_STATE_FLASHBLUE:
            # Flashing: draw only on “on” frames
            if (self.anim_frame // PT_DURATION_FLASH) % 2 == 0:
                screen.blit(self.press_turn_blue, (x, y))
        elif state == PT_STATE_FLASHRED:
            if (self.anim_frame // PT_DURATION_FLASH) % 2 == 0:
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

        poke_offset = int(AMP * math.sin(self.anim_frame * SPEED))
        hp_offset = int(-AMP * math.sin(self.anim_frame * SPEED + PHASE))

        # ---------------------------------------------------------
        # Background
        # ---------------------------------------------------------
        screen.blit(self.background, COORDS_BACKGROUND)

        # ---------------------------------------------------------
        # Enemy Pokémon (no HP/MP box for now)
        # ---------------------------------------------------------
        for i in ENEMY_DRAW_ORDER:
            sprite = self.enemy_sprites[i]
            if sprite is None:
                continue

            x = ENEMY_BASE_X + i * ENEMY_SPACING
            screen.blit(sprite, (x, ENEMY_Y))


        # ---------------------------------------------------------
        # Player-side sprites (Pokémon + player)
        # ---------------------------------------------------------
        for i, sprite in enumerate(self.player_sprites):
            if sprite is None:
                continue

            pokemon = self.model.player_team[i]

            slot = i
            x = PLAYER_BASE_X + slot * PLAYER_SPACING

            if pokemon.is_player:
                # Player sprite base position
                x += PLAYER_OFFSET
                y = PLAYER_Y + PLAYER_Y_OFFSET
            else:
                # Normal Pokémon base position
                y = PLAYER_Y + NORMAL_Y_OFFSET

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
        hpmp_y = HPMP_Y + hp_offset
        screen.blit(self.hpmp_sprite, (HPMP_X, hpmp_y))
        self.font1.draw_text(screen, active_pokemon.name, ACTIVE_POKEMON_NAME_X, hpmp_y + ACTIVE_POKEMON_NAME_Y_OFFSET)
        screen.blit(self.lv_sprite, (LV_X, hpmp_y + LV_Y_OFFSET))
        self.font1.draw_text(screen, str(active_pokemon.level), LV_TEXT_X, hpmp_y + LV_TEXT_Y_OFFSET)
        self.draw_hp_bar(screen, active_pokemon, hp_offset)
        self.draw_mp_bar(screen, active_pokemon, hp_offset)
        screen.blit(self.battleframe, COORDS_FRAME)

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
        if menu_mode == MENU_MODE_MAIN:
            self.font0.draw_text(screen, f"What will {active_pokemon.name} do?", X_MENU_MAIN, Y_MENU_MAIN_0)
            self.font0.draw_text(screen, MENU_MAIN_LINE_1, X_MENU_MAIN, Y_MENU_MAIN_1)
            self.font0.draw_text(screen, MENU_MAIN_LINE_2, X_MENU_MAIN, Y_MENU_MAIN_2)

            cursor_x, cursor_y = COORDS_MENU_MAIN[menu_index]
            screen.blit(self.cursor_sprite, (cursor_x, cursor_y))
        elif menu_mode == MENU_MODE_SKILLS:
            pokemon = active_pokemon

            y = SKILLS_Y
            for move_name in pokemon.moves:
                text = pokemon.format_move_for_menu(move_name, self.smt_moves)
                self.font2.draw_text(screen, text, SKILLS_X, y)
                y += SKILLS_Y_INCR

            # Draw cursor
            cursor_x, cursor_y = COORDS_MENU_SKILLS[menu_index]
            screen.blit(self.cursor_sprite, (cursor_x, cursor_y))
        else:
            msg = DUMMY_TEXTS[previous_menu_index]
            self.font0.draw_text(screen, msg, X_MENU_MAIN, Y_MENU_MAIN_0)
            self.font0.draw_text(screen, DUMMY_MSG, X_MENU_MAIN, Y_MENU_MAIN_1)

