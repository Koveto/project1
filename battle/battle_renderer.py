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

    def draw_hp_bar(self, screen, pokemon, hp_offset,
                base_x=HP_BAR_X, base_y=HP_BAR_Y,
                override_hp=None):

        # Safety: no HP bar if max HP is invalid
        if pokemon.max_hp <= 0:
            return

        # Use animated HP if provided, otherwise use the real remaining HP
        hp_value = override_hp if override_hp is not None else pokemon.remaining_hp

        # Clamp ratio between 0 and 1
        ratio = max(0.0, min(1.0, hp_value / pokemon.max_hp))

        # Compute fill width
        fill_width = int(HP_BAR_WIDTH * ratio)
        if fill_width <= 0:
            return

        # Scale the fill sprite to the correct width
        fill_surface = pygame.transform.scale(
            self.hp_fill,
            (fill_width, HP_BAR_HEIGHT)
        )

        # Draw the bar
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


    def wrap_text_words(self, text, max_width=32):
        words = text.split()
        lines = []
        current = []

        for word in words:
            # Predict length if we add this word
            predicted = " ".join(current + [word])
            if len(predicted) > max_width:
                lines.append(current)
                current = [word]
            else:
                current.append(word)

        if current:
            lines.append(current)

        # Ensure exactly 3 lines
        while len(lines) < 3:
            lines.append([])

        return lines[:3]
    
    def draw_damaging_enemy(
            self, screen,
            scroll_text, scroll_index, scroll_done,
            damage_done, affinity_done,
            affinity_text, affinity_scroll_index,
            affinity_scroll_done, blink
    ):
        
        # ---------------------------------------------------------
        # PHASE 3/4 — Affinity text (scrolling or full)
        # ---------------------------------------------------------
        if damage_done and affinity_text:

            # PHASE 3 — affinity text scrolling
            if not affinity_done:
                visible = int(affinity_scroll_index)
                text_to_draw = affinity_text[:visible]

                self.font0.draw_text(
                    screen, text_to_draw,
                    X_MENU_MAIN, Y_MENU_MAIN_0
                )

                if affinity_scroll_done and blink:
                    screen.blit(self.cursor_sprite, (CONFIRM_ARROW_X, CONFIRM_ARROW_Y))

                return

            # PHASE 4 — affinity text fully displayed
            self.font0.draw_text(
                screen, affinity_text,
                X_MENU_MAIN, Y_MENU_MAIN_0
            )

            if blink:
                screen.blit(self.cursor_sprite, (CONFIRM_ARROW_X, CONFIRM_ARROW_Y))
            return


        # ---------------------------------------------------------
        # PHASE 4b — Neutral damage: KEEP ATTACK TEXT VISIBLE
        # ---------------------------------------------------------
        if damage_done and not affinity_text:

            full_word_lines = self.wrap_text_words(scroll_text, max_width=32)

            if len(full_word_lines) > 0:
                self.font0.draw_text(screen, full_word_lines[0],
                                    X_MENU_MAIN, Y_MENU_MAIN_0)
            if len(full_word_lines) > 1:
                self.font0.draw_text(screen, full_word_lines[1],
                                    X_MENU_MAIN, Y_MENU_MAIN_1)
            if len(full_word_lines) > 2:
                self.font0.draw_text(screen, full_word_lines[2],
                                    X_MENU_MAIN, Y_MENU_MAIN_2)

            if blink:
                screen.blit(self.cursor_sprite, (CONFIRM_ARROW_X, CONFIRM_ARROW_Y))

            return


        # ---------------------------------------------------------
        # PHASE 1 — Attack text scrolls (pre‑damage)
        # ---------------------------------------------------------
        full_word_lines = self.wrap_text_words(scroll_text, max_width=32)

        visible_chars = scroll_index
        visible_lines = ["", "", ""]

        for line_idx, words in enumerate(full_word_lines):
            for word in words:
                chunk = (word + " ")
                if visible_chars >= len(chunk):
                    visible_lines[line_idx] += chunk
                    visible_chars -= len(chunk)
                else:
                    visible_lines[line_idx] += chunk[:visible_chars]
                    visible_chars = 0
                    break

            if visible_chars == 0:
                break

        # Draw attack text (scrolling)
        self.font0.draw_text(screen, visible_lines[0], X_MENU_MAIN, Y_MENU_MAIN_0)
        self.font0.draw_text(screen, visible_lines[1], X_MENU_MAIN, Y_MENU_MAIN_1)
        self.font0.draw_text(screen, visible_lines[2], X_MENU_MAIN, Y_MENU_MAIN_2)

        # ---------------------------------------------------------
        # PHASE 2 — Scroll done, HP anim running (NO ARROW)
        # ---------------------------------------------------------
        if scroll_done and not damage_done:
            return

        # ---------------------------------------------------------
        # PHASE 1.5 — Scroll done, HP anim not started yet
        # ---------------------------------------------------------
        if scroll_done and not damage_done and not self.damage_started:
            if blink:
                screen.blit(self.cursor_sprite, (CONFIRM_ARROW_X, CONFIRM_ARROW_Y))
            return




    def draw(self, screen, menu_index, 
            menu_mode, previous_menu_index, 
            skills_cursor, skills_scroll,
            target_index, scroll_text,
            scroll_index, scroll_done,
            damage_done, affinity_done,
            affinity_text, affinity_scroll_index,
            affinity_scroll_done):

        # ---------------------------------------------------------
        # Active Pokémon based on turn_index
        # ---------------------------------------------------------
        active_index = self.model.turn_index
        active_pokemon = self.model.player_team[active_index]
        target = self.model.enemy_team[target_index]

        self.anim_frame += 1
        blink = (self.anim_frame // 20) % 2 == 0


        poke_offset = int(AMP * math.sin(self.anim_frame * SPEED))
        hp_offset = int(-AMP * math.sin(self.anim_frame * SPEED + PHASE))

        # ---------------------------------------------------------
        # Background
        # ---------------------------------------------------------
        screen.blit(self.background, COORDS_BACKGROUND)

        # ---------------------------------------------------------
        # Enemy Pokémon
        # ---------------------------------------------------------
        target_enemy_pos = None
        for i in ENEMY_DRAW_ORDER:
            sprite = self.enemy_sprites[i]
            if sprite is None:
                continue

            x = ENEMY_BASE_X + i * ENEMY_SPACING
            y = ENEMY_Y

            # Bounce ONLY in target-select mode
            if menu_mode == MENU_MODE_TARGET_SELECT and i == target_index:
                y += poke_offset

            screen.blit(sprite, (x, y))

            if i == target_index:
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

            # Active Pokémon bounces in all modes EXCEPT damaging
            if i == active_index and menu_mode != MENU_MODE_DAMAGING_ENEMY:
                y += poke_offset


            screen.blit(sprite, (x, y))

            if i == active_index:
                active_pokemon_pos = (sprite, x, y)

        # ---------------------------------------------------------
        # Darken battlefield in BOTH target-select and damaging states
        # ---------------------------------------------------------
        if menu_mode in (MENU_MODE_TARGET_SELECT, MENU_MODE_DAMAGING_ENEMY):

            # Darken everything above the frame
            dark_surface = pygame.Surface((ACTUAL_WIDTH, FRAME_Y))
            dark_surface.set_alpha(140)
            dark_surface.fill((0, 0, 0))
            screen.blit(dark_surface, (0, 0))

            # Re-draw active Pokémon
            if active_pokemon_pos is not None:
                sprite, x, y = active_pokemon_pos
                screen.blit(sprite, (x, y))

            # Re-draw targeted enemy
            if target_enemy_pos is not None:
                sprite, x, y = target_enemy_pos
                screen.blit(sprite, (x, y))

            # -----------------------------------------------------
            # Flashing ONLY in target-select mode
            # -----------------------------------------------------
            if menu_mode == MENU_MODE_TARGET_SELECT:
                selected_index = skills_scroll + skills_cursor
                move_name = active_pokemon.moves[selected_index]
                move = self.smt_moves[move_name]

                element = move["element"]
                element_index = ELEMENT_INDEX[element]
                affinity_value = target.affinities[element_index]

                if affinity_value != 0:
                    flash = (math.sin(self.anim_frame * 0.3) + 1) * 0.5
                    alpha = int(120 * flash)

                    flash_color = (255, 0, 0) if affinity_value > 0 else (0, 255, 0)

                    sprite_alpha = sprite.convert_alpha()
                    w, h = sprite_alpha.get_size()

                    tint = pygame.Surface((w, h), pygame.SRCALPHA)
                    tint.fill((*flash_color, 255))
                    tint.blit(sprite_alpha, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                    tint.set_alpha(alpha)

                    screen.blit(tint, (x, y))

        # ---------------------------------------------------------
        # HP/MP + Frame
        # ---------------------------------------------------------
        # If we are damaging the enemy, freeze the UI (no bounce)
        if menu_mode == MENU_MODE_DAMAGING_ENEMY:
            hpmp_y = HPMP_Y
            enemy_hpmp_y = HPMP_ENEMY_Y
            ui_hp_offset = 0
        else:
            hpmp_y = HPMP_Y + hp_offset
            enemy_hpmp_y = HPMP_ENEMY_Y + hp_offset
            ui_hp_offset = hp_offset

        # --- Player HP/MP (always drawn) ---
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

        self.draw_hp_bar(screen, active_pokemon, ui_hp_offset)
        self.draw_mp_bar(screen, active_pokemon, ui_hp_offset)

        # --- Enemy HP/MP (shown in BOTH target-select and damaging states) ---
        if menu_mode in (MENU_MODE_TARGET_SELECT, MENU_MODE_DAMAGING_ENEMY):

            screen.blit(self.hpmp_sprite, (HPMP_ENEMY_X, enemy_hpmp_y))

            self.font1.draw_text(
                screen,
                target.name,
                ACTIVE_TARGET_NAME_X,
                enemy_hpmp_y + ACTIVE_TARGET_NAME_Y_OFFSET
            )

            screen.blit(self.lv_sprite,
                        (LV_X_ENEMY, enemy_hpmp_y + LVL_Y_OFFSET_ENEMY))

            self.font1.draw_text(
                screen,
                str(target.level),
                LV_TEXT_X_ENEMY,
                enemy_hpmp_y + LV_TEXT_Y_OFFSET_ENEMY
            )

            # Use animated HP if present
            hp_source = getattr(target, "hp_anim", target.remaining_hp)

            self.draw_hp_bar(
                screen,
                target,
                ui_hp_offset,
                base_x=HPMP_TO_FILL_X,
                base_y=HPMP_TO_FILL_Y_0,
                override_hp=hp_source
            )

            self.draw_mp_bar(screen, target, ui_hp_offset,
                            base_x=HPMP_TO_FILL_X, base_y=HPMP_TO_FILL_Y_1)


        screen.blit(self.battleframe, COORDS_FRAME)

        # ---------------------------------------------------------
        # Press Turn Icons
        # ---------------------------------------------------------
        press_turn_states = self.model.get_press_turn_icon_states(self.anim_frame)

        for i, state in enumerate(press_turn_states):
            x = PT_X + i * PT_SPACING
            if menu_mode == MENU_MODE_DAMAGING_ENEMY:
                y = PT_Y
            else:
                y = PT_Y + hp_offset

            self.draw_press_turn_icon(screen, state, x, y)

        # ---------------------------------------------------------
        # Menu text
        # ---------------------------------------------------------
        if menu_mode == MENU_MODE_MAIN:
            self.font0.draw_text(screen, f"What will {active_pokemon.name} do?",
                                X_MENU_MAIN, Y_MENU_MAIN_0)
            self.font0.draw_text(screen, MENU_MAIN_LINE_1,
                                X_MENU_MAIN, Y_MENU_MAIN_1)
            self.font0.draw_text(screen, MENU_MAIN_LINE_2,
                                X_MENU_MAIN, Y_MENU_MAIN_2)

            cursor_x, cursor_y = COORDS_MENU_MAIN[menu_index]
            screen.blit(self.cursor_sprite, (cursor_x, cursor_y))

        elif menu_mode == MENU_MODE_SKILLS:
            visible_moves = active_pokemon.moves[skills_scroll:skills_scroll + 3]
            y = SKILLS_Y
            for move_name in visible_moves:
                text = active_pokemon.format_move_for_menu(move_name, self.smt_moves)
                self.font2.draw_text(screen, text, SKILLS_X, y)
                y += SKILLS_Y_INCR

            cursor_x, cursor_y = COORDS_MENU_SKILLS[skills_cursor]
            screen.blit(self.cursor_sprite, (cursor_x, cursor_y))

        elif menu_mode == MENU_MODE_DAMAGING_ENEMY:
            self.draw_damaging_enemy(
                screen,
                scroll_text, scroll_index, scroll_done,
                damage_done, affinity_done,
                affinity_text, affinity_scroll_index,
                affinity_scroll_done, blink
            )
            return

        else:
            msg = DUMMY_TEXTS[previous_menu_index]
            self.font0.draw_text(screen, msg, X_MENU_MAIN, Y_MENU_MAIN_0)
            self.font0.draw_text(screen, DUMMY_MSG, X_MENU_MAIN, Y_MENU_MAIN_1)

