# battle/battle_renderer.py

import pygame, math
from constants import *
from battle.battle_constants import *
from battle.battle_font import BattleFont
from pokedex.pokemon_sprites import load_pokemon_sprite, load_player_sprite

class BattleRenderer:

    def __init__(self, background_surface, model, moves):
        self.background = background_surface
        self.model = model
        self.smt_moves = moves
        self.anim_frame = 0

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

        self.mp_cost_fill = load_scaled_sprite(
            sprite_path(FILENAME_MPCOSTFILL), 
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

    def draw_hp_bar(self, screen, pokemon, hp_offset, base_x=HP_BAR_X, base_y=HP_BAR_Y):
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
        screen.blit(fill_surface, (base_x, base_y + hp_offset))


    def draw_mp_bar(self, screen, pokemon, hp_offset, base_x=MP_BAR_X, base_y=MP_BAR_Y):
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
        screen.blit(fill_surface, (base_x, base_y + hp_offset))


    def draw_mp_cost_bar(self, screen, pokemon, move_name, hp_offset):
        move = self.smt_moves.get(move_name)
        if not move:
            return

        cost = move["mp"]
        max_mp = pokemon.max_mp

        if max_mp <= 0 or cost <= 0:
            return

        # Cost as a fraction of max MP
        ratio = cost / max_mp
        ratio = max(0.0, min(1.0, ratio))

        fill_width = int(MP_BAR_WIDTH * ratio)
        if fill_width <= 0:
            return

        fill_surface = pygame.transform.scale(
            self.mp_cost_fill,
            (fill_width, MP_BAR_HEIGHT)
        )

        # Anchor the cost bar on the RIGHT side of the MP bar
        right_edge = MP_BAR_X + MP_BAR_WIDTH
        left_edge = right_edge - fill_width

        screen.blit(fill_surface, (left_edge, MP_BAR_Y + hp_offset))



    def draw(self, screen, menu_index, 
            menu_mode, previous_menu_index, 
            skills_cursor, skills_scroll,
            target_index):

        # ---------------------------------------------------------
        # Active Pokémon based on turn_index
        # ---------------------------------------------------------
        active_index = self.model.turn_index
        active_pokemon = self.model.player_team[active_index]
        target = self.model.enemy_team[target_index]

        self.anim_frame += 1

        poke_offset = int(AMP * math.sin(self.anim_frame * SPEED))
        hp_offset = int(-AMP * math.sin(self.anim_frame * SPEED + PHASE))

        # ---------------------------------------------------------
        # Background
        # ---------------------------------------------------------
        screen.blit(self.background, COORDS_BACKGROUND)

        # ---------------------------------------------------------
        # Enemy Pokémon
        # ---------------------------------------------------------
        target_enemy_pos = None  # we'll store this for later re-draw
        for i in ENEMY_DRAW_ORDER:
            sprite = self.enemy_sprites[i]
            if sprite is None:
                continue

            x = ENEMY_BASE_X + i * ENEMY_SPACING
            y = ENEMY_Y

            # Bounce the targeted enemy in target-select mode
            if menu_mode == MENU_MODE_TARGET_SELECT and i == target_index:
                y += poke_offset

            screen.blit(sprite, (x, y))

            if menu_mode == MENU_MODE_TARGET_SELECT and i == target_index:
                target_enemy_pos = (sprite, x, y)

        # ---------------------------------------------------------
        # Player-side sprites (Pokémon + player)
        # ---------------------------------------------------------
        active_pokemon_pos = None

        for i, sprite in enumerate(self.player_sprites):
            if sprite is None:
                continue

            pokemon = self.model.player_team[i]

            slot = i
            x = PLAYER_BASE_X + slot * PLAYER_SPACING

            if pokemon.is_player:
                x += PLAYER_OFFSET
                y = PLAYER_Y + PLAYER_Y_OFFSET
            else:
                y = PLAYER_Y + NORMAL_Y_OFFSET

            if i == active_index:
                y += poke_offset

            screen.blit(sprite, (x, y))

            if i == active_index:
                active_pokemon_pos = (sprite, x, y)

        # ---------------------------------------------------------
        # Darken battlefield in target-select mode
        # + affinity-based flashing on target
        # ---------------------------------------------------------
        if menu_mode == MENU_MODE_TARGET_SELECT:
            # Which move is being used?
            selected_index = skills_scroll + skills_cursor
            move_name = active_pokemon.moves[selected_index]
            move = self.smt_moves[move_name]

            element = move["element"]          # e.g. "Fire"
            element_index = ELEMENT_INDEX[element]
            affinity_value = target.affinities[element_index]

            # Darken everything above the frame
            dark_surface = pygame.Surface((ACTUAL_WIDTH, FRAME_Y))
            dark_surface.set_alpha(140)  # tweak to taste
            dark_surface.fill((0, 0, 0))
            screen.blit(dark_surface, (0, 0))

            # Re-draw active Pokémon on top
            if active_pokemon_pos is not None:
                sprite, x, y = active_pokemon_pos
                screen.blit(sprite, (x, y))

            # Re-draw targeted enemy on top
            if target_enemy_pos is not None:
                sprite, x, y = target_enemy_pos
                screen.blit(sprite, (x, y))

                # Affinity-based flashing overlay on the target
                if affinity_value != 0:
                    flash = (math.sin(self.anim_frame * 0.3) + 1) * 0.5
                    alpha = int(120 * flash)

                    if affinity_value > 0:
                        flash_color = (255, 0, 0)
                    else:
                        flash_color = (0, 255, 0)

                    sprite_alpha = sprite.convert_alpha()
                    w, h = sprite_alpha.get_size()

                    tint = pygame.Surface((w, h), pygame.SRCALPHA)
                    tint.fill((*flash_color, 255))  # <-- FIXED: full alpha

                    tint.blit(sprite_alpha, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

                    tint.set_alpha(alpha)

                    screen.blit(tint, (x, y))




        # ---------------------------------------------------------
        # HP/MP + Frame
        # ---------------------------------------------------------
        # --- Player HP/MP (always drawn) ---
        hpmp_y = HPMP_Y + hp_offset
        screen.blit(self.hpmp_sprite, (HPMP_X, hpmp_y))

        self.font1.draw_text(
            screen,
            active_pokemon.name,
            ACTIVE_POKEMON_NAME_X,
            hpmp_y + ACTIVE_POKEMON_NAME_Y_OFFSET
        )

        screen.blit(self.lv_sprite, (LV_X, hpmp_y + LV_Y_OFFSET))

        self.font1.draw_text(
            screen,
            str(active_pokemon.level),
            LV_TEXT_X,
            hpmp_y + LV_TEXT_Y_OFFSET
        )

        self.draw_hp_bar(screen, active_pokemon, hp_offset)
        self.draw_mp_bar(screen, active_pokemon, hp_offset)

        # --- Enemy HP (only in target-select mode) ---
        if menu_mode == MENU_MODE_TARGET_SELECT:

            # Enemy HPMP frame at enemy coordinates
            screen.blit(self.hpmp_sprite, (HPMP_ENEMY_X, HPMP_ENEMY_Y + hp_offset))

            # Enemy name
            self.font1.draw_text(
                screen,
                target.name,
                ACTIVE_TARGET_NAME_X,
                HPMP_ENEMY_Y + ACTIVE_TARGET_NAME_Y_OFFSET + hp_offset
            )

            # Enemy level
            screen.blit(self.lv_sprite, (LV_X_ENEMY, HPMP_ENEMY_Y + LVL_Y_OFFSET_ENEMY + hp_offset))

            self.font1.draw_text(
                screen,
                str(target.level),
                LV_TEXT_X_ENEMY,
                HPMP_ENEMY_Y + LV_TEXT_Y_OFFSET_ENEMY + hp_offset
            )

            self.draw_hp_bar(screen, target, hp_offset, base_x=HPMP_TO_FILL_X, base_y=HPMP_TO_FILL_Y_0)
            self.draw_mp_bar(screen, target, hp_offset, base_x=HPMP_TO_FILL_X, base_y=HPMP_TO_FILL_Y_1)

        if menu_mode == MENU_MODE_SKILLS:
            # Determine which move is selected
            selected_index = skills_scroll + skills_cursor
            if selected_index < len(active_pokemon.moves):
                selected_move = active_pokemon.moves[selected_index]
                self.draw_mp_cost_bar(screen, active_pokemon, selected_move, hp_offset)

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
            visible_moves = active_pokemon.moves[skills_scroll : skills_scroll + 3]
            y = SKILLS_Y
            for move_name in visible_moves:
                text = active_pokemon.format_move_for_menu(move_name, self.smt_moves)
                self.font2.draw_text(screen, text, SKILLS_X, y)
                y += SKILLS_Y_INCR

            # Draw cursor at one of the 3 fixed positions
            cursor_x, cursor_y = COORDS_MENU_SKILLS[skills_cursor]
            screen.blit(self.cursor_sprite, (cursor_x, cursor_y))
        elif menu_mode == MENU_MODE_TARGET_SELECT:
            # Determine which move is selected
            selected_index = skills_scroll + skills_cursor
            move_name = active_pokemon.moves[selected_index]

            # Draw ONLY the selected move, but in the same row it was before
            cursor_row = skills_cursor  # 0, 1, or 2
            y = SKILLS_Y + cursor_row * SKILLS_Y_INCR

            text = active_pokemon.format_move_for_menu(move_name, self.smt_moves)
            self.font2.draw_text(screen, text, SKILLS_X, y)

            # Draw cursor in the same place too
            cursor_x, cursor_y = COORDS_MENU_SKILLS[cursor_row]
            screen.blit(self.cursor_sprite, (cursor_x, cursor_y))
        else:
            msg = DUMMY_TEXTS[previous_menu_index]
            self.font0.draw_text(screen, msg, X_MENU_MAIN, Y_MENU_MAIN_0)
            self.font0.draw_text(screen, DUMMY_MSG, X_MENU_MAIN, Y_MENU_MAIN_1)

