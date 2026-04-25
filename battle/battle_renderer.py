import pygame, os, math
from constants import *

from pokedex.pokemon_sprites import load_pokemon_sprite, load_player_sprite

from battle.battle_constants import *
from battle.battle_font import BattleFont
from battle.battle_background import load_battle_background

"""
from battle.renderers.text_renderer import TextRenderer
from battle.renderers.background_renderer import BackgroundRenderer
from battle.renderers.hpmp_renderer import HPMPRenderer
from battle.renderers.menu_renderer import MenuRenderer
from battle.renderers.press_turn_renderer import PressTurnRenderer
from battle.renderers.stat_icon_renderer import StatIconRenderer
"""

class BattleRenderer:
    def __init__(self, b):
        # ========================= START INIT =================================
        self.background = load_battle_background(b.background)

        # Fonts
        self.font0 = BattleFont(FONT0_FILENAME, glyph_w=FONT0_WIDTH, glyph_h=FONT0_HEIGHT,
                                scale=FONT0_SCALE, spacing=FONT0_SPACING)
        self.font1 = BattleFont(FONT1_FILENAME, glyph_w=FONT1_WIDTH, glyph_h=FONT1_HEIGHT,
                                scale=FONT1_SCALE, spacing=FONT1_SPACING)
        self.font2 = BattleFont(FONT2_FILENAME, glyph_w=FONT2_WIDTH, glyph_h=FONT2_HEIGHT,
                                scale=FONT2_SCALE, spacing=FONT2_SPACING)
        self.font3 = BattleFont(FONT3_FILENAME, glyph_w=FONT3_WIDTH, glyph_h=FONT3_HEIGHT,
                                scale=FONT3_SCALE, spacing=FONT3_SPACING)

        # UI sprites
        self.hp_fill = load_scaled_sprite(sprite_path(FILENAME_HPFILL), scale=SCALE)
        self.mp_fill = load_scaled_sprite(sprite_path(FILENAME_MPFILL), scale=SCALE)
        self.mp_cost_fill = load_scaled_sprite(sprite_path(FILENAME_MPCOSTFILL), scale=SCALE)
        self.cursor_sprite = load_scaled_sprite(sprite_path(FILENAME_CURSOR), scale=SCALE, colorkey=COLOR_WHITE)
        self.hpmp_sprite = load_scaled_sprite(sprite_path(FILENAME_HPMP), scale=SCALE, colorkey=COLOR_MAGENTA)
        self.hpmp_sprite_enemy = load_scaled_sprite(sprite_path(FILENAME_HPMP_ENEMY), scale=SCALE, colorkey=COLOR_MAGENTA)
        self.lv_sprite = load_scaled_sprite(sprite_path(FILENAME_LV), scale=FONT1_SCALE)
        self.bframe = load_scaled_sprite(sprite_path(FILENAME_FRAME), scale=SCALE)
        self.press_turn_red = load_scaled_sprite(sprite_path(FILENAME_PBRED), scale=SCALE_PRESSTURN, colorkey=COLOR_MAGENTA)
        self.press_turn_blue = load_scaled_sprite(sprite_path(FILENAME_PBBLUE), scale=SCALE_PRESSTURN, colorkey=COLOR_MAGENTA)

        # Pokémon sprites
        self.player_sprites = [
            self._load_sprite_for_pokemon(p, is_back=True) if p else None
            for p in b.player_team
        ]
        self.enemy_sprites = [
            self._load_sprite_for_pokemon(p, is_back=False) if p else None
            for p in b.enemy_team
        ]

        # This value increases indefinitely... causes errors??
        self.anim_frame = 0

        root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        
        sheet_path_statbuffdebuff = os.path.join(root, "sprites", "statbuffdebuff.png")
        sheet_statbuffdebuff = pygame.image.load(sheet_path_statbuffdebuff).convert_alpha()
        self.statbuffdebuff = {}  # (row, col) → Surface
        for row in range(3):      # attack, defense, speed
            for col in range(4):  # +1, +2, -1, -2
                rect = pygame.Rect(
                    col * 24,
                    row * 24,
                    24,
                    24
                )
                temp = sheet_statbuffdebuff.subsurface(rect)
                self.statbuffdebuff[(row, col)] = temp

        # Sub-renderers
        """self.stat_icon_renderer = StatIconRenderer()
        self.text_renderer = TextRenderer(self.font0, self.cursor_sprite)
        self.background_renderer = BackgroundRenderer(battle_background, self.player_sprites, self.enemy_sprites, b.smt_moves)
        self.hpmp_renderer = HPMPRenderer(self.font1, self.font3, self.hpmp_sprite, self.hpmp_sprite_enemy, self.lv_sprite, self.hp_fill, self.mp_fill, self.mp_cost_fill, self.stat_icon_renderer)
        self.menu_renderer = MenuRenderer(self.font0, self.font2, self.cursor_sprite, b.smt_moves)
        self.press_turn_renderer = PressTurnRenderer(self.press_turn_blue, self.press_turn_red)"""
        # ========================= END INIT =================================

    def draw(self, b, screen):
        # ========================= START DRAW =================================
        self.anim_frame += 1
        blink = ((self.anim_frame // 10) % 2 == 0)
        bounce_offset_pkmn = int(BOUNCE_AMP * math.sin(self.anim_frame * BOUNCE_SPEED))
        bounce_offset_hp = int(-BOUNCE_AMP * math.sin(self.anim_frame * BOUNCE_SPEED + BOUNCE_PHASE))

        screen.blit(self.background, COORDS_BACKGROUND)

        target_pkmn_info = None # (sprite, (x, y))
        active_pkmn_info = None
        pkmn = b.player_team[b.turn_index]

        """
        info_index = ROW_NOT_INFO_STATE
        if b.menu_mode == MENU_MODE_INFO:
            if b.info_row == 0:
                info_index = b.info_col
        """
        for i in ENEMY_DRAW_ORDER:
            sprite = self.enemy_sprites[i]
            if sprite is None:
                continue

            x = X_PKMN_ENEMY + i * D_PKMN_ENEMY
            y = Y_PKMN_ENEMY

            "if b.menu_mode in (MENU_MODE_TARGET_SELECT, MENU_MODE_ITEM_TARGET_SELECT):"
            if b.draw_enemy_bounce:
                if i == b.target_index:
                    y += bounce_offset_pkmn
            """
            if b.menu_mode == MENU_MODE_INFO:
                if i == info_index:
                    y += bounce_offset_pkmn
            """

            screen.blit(sprite, (x, y))

            """
            if b.menu_mode not in (MENU_MODE_ANNOUNCE_ENEMY_ATTACK, MENU_MODE_DAMAGING_PLAYER):
                if i == b.target_index:
                    target_enemy_pos = (sprite, x, y)
            """
            if i == b.target_index:
                target_pkmn_info = (sprite, x, y)
            """
            elif b.menu_mode == MENU_MODE_INFO:
                target_enemy_pos = (sprite, x, y)

            # ENEMY TURN CASE: highlight the attacking enemy
            else:
                if b.active_enemy_index is not None and i == b.active_enemy_index:
                    target_enemy_pos = (sprite, x, y)
            """

        which_pkmn_bouncing = b.turn_index
        """
        if b.menu_mode in (MENU_MODE_ITEM_ALLY_TARGET, 
                           MENU_MODE_TARGET_BUFF,
                           MENU_MODE_BUFF_PLAYER,
                           MENU_MODE_TARGET_HEAL):
            bounce_index = b.selected_ally
        elif b.menu_mode == MENU_MODE_ANNOUNCE_ENEMY_ATTACK:
            bounce_index = b.enemy_target_index
        elif b.menu_mode == MENU_MODE_INFO:
            if b.info_row == ROW_PLAYER:
                bounce_index = b.info_col
            else:
                bounce_index = ROW_NOT_INFO_STATE
        elif b.menu_mode in (MENU_MODE_BUFF_PLAYER_ALL,
                             MENU_MODE_TARGET_BUFF_ALL):
            bounce_index = ROW_NOT_INFO_STATE
        """

        for i in range(len(self.player_sprites)):
            sprite = self.player_sprites[i]
            if sprite is None:
                continue

            pokemon = b.player_team[i]

            x = X_PKMN_PLAYER + i * D_PKMN_PLAYER

            if pokemon.is_player:
                x += D_PLAYER_OFFSET_X
                y = Y_PKMN_PLAYER + D_PLAYER_OFFSET_Y
            else:
                y = Y_PKMN_PLAYER + D_PKMN_PLAYER_OFFSET_Y

            """
            if (b.menu_mode == MENU_MODE_TARGET_BUFF_ALL) or (i == active_index and b.menu_mode not in (MENU_MODE_DAMAGING_ENEMY,
                                                       MENU_MODE_ANNOUNCE_ENEMY_ATTACK,
                                                       MENU_MODE_DAMAGING_PLAYER)):
                y += poke_offset
            """
            if (i == which_pkmn_bouncing) and \
                (b.draw_player_bounce):
                y += bounce_offset_pkmn

            screen.blit(sprite, (x, y))

            if (i == which_pkmn_bouncing):
                active_pkmn_info = (sprite, x, y)

        """
        if b.menu_mode in (MENU_MODE_ITEM_ALLY_TARGET,
                           MENU_MODE_BUFF_PLAYER,
                           MENU_MODE_TARGET_HEAL):
            sprite = self.background_renderer.player_sprites[b.selected_ally]
            pokemon = b.model.player_team[b.selected_ally]

            x = PLAYER_BASE_X + b.selected_ally * PLAYER_SPACING
            if pokemon.is_player:
                x += PLAYER_OFFSET
                y = PLAYER_Y + PLAYER_Y_OFFSET
            else:
                y = PLAYER_Y + NORMAL_Y_OFFSET

            y += poke_offset
            highlight_player_pos = (sprite, x, y)
        if b.menu_mode in (MENU_MODE_ANNOUNCE_ENEMY_ATTACK,
                         MENU_MODE_DAMAGING_PLAYER):
            sprite = self.background_renderer.player_sprites[b.enemy_target_index]
            pokemon = b.model.player_team[b.enemy_target_index]

            x = PLAYER_BASE_X + b.enemy_target_index * PLAYER_SPACING
            if pokemon.is_player:
                x += PLAYER_OFFSET
                y = PLAYER_Y + PLAYER_Y_OFFSET
            else:
                y = PLAYER_Y + NORMAL_Y_OFFSET

            highlight_player_pos = (sprite, x, y)
        if b.menu_mode == MENU_MODE_INFO:
            if b.info_row == ROW_ENEMY:
                sprite = self.background_renderer.enemy_sprites[b.info_col]
                pokemon = b.model.enemy_team[b.info_col]

                x = ENEMY_BASE_X + b.info_col * ENEMY_SPACING
                y = ENEMY_Y + poke_offset

                highlight_player_pos = None
                target_enemy_pos = (sprite, x, y)
            if b.info_row == ROW_PLAYER:
                sprite = self.background_renderer.player_sprites[b.info_col]
                pokemon = b.model.player_team[b.info_col]

                x = PLAYER_BASE_X + b.info_col * PLAYER_SPACING
                if pokemon.is_player:
                    x += PLAYER_OFFSET
                    y = PLAYER_Y + PLAYER_Y_OFFSET + poke_offset
                else:
                    y = PLAYER_Y + NORMAL_Y_OFFSET + poke_offset

                highlight_player_pos = (sprite, x, y)
                target_enemy_pos = None

        if b.menu_mode in (
            MENU_MODE_TARGET_SELECT,
            MENU_MODE_DAMAGING_ENEMY,
            MENU_MODE_ITEM_ALLY_TARGET,
            MENU_MODE_ITEM_TARGET_SELECT,
            MENU_MODE_ANNOUNCE_ENEMY_ATTACK,
            MENU_MODE_DAMAGING_PLAYER,
            MENU_MODE_INFO,
            MENU_MODE_TARGET_BUFF,
            MENU_MODE_TARGET_BUFF_ALL,
            MENU_MODE_BUFF_PLAYER,
            MENU_MODE_BUFF_PLAYER_ALL,
            MENU_MODE_TARGET_HEAL
        ):
        """
        if b.draw_darken:
            dark_surface = pygame.Surface((ACTUAL_WIDTH, Y_FRAME))
            dark_surface.set_alpha(140)
            dark_surface.fill((0,0,0))
            screen.blit(dark_surface, (0,0))
            """
            if b.menu_mode in (MENU_MODE_ITEM_ALLY_TARGET,
                            MENU_MODE_TARGET_BUFF,
                            MENU_MODE_BUFF_PLAYER,
                            MENU_MODE_TARGET_HEAL):
                if highlight_player_pos is not None:
                    sprite, x, y = highlight_player_pos
                    screen.blit(sprite, (x, y))
                return
            if b.menu_mode in (MENU_MODE_BUFF_PLAYER_ALL,
                           MENU_MODE_TARGET_BUFF_ALL):
                if b.menu_mode == MENU_MODE_BUFF_PLAYER_ALL:
                    bounce = 0
                else:
                    bounce = poke_offset
                for i in range(len(b.model.player_team)):
                    pkmn = b.model.player_team[i]
                    sprite = self.player_sprites[i]
                    if pkmn.is_player:
                        x = PLAYER_BASE_X + i * PLAYER_SPACING + 50
                        y = PLAYER_Y + PLAYER_Y_OFFSET + bounce
                    else:
                        x = PLAYER_BASE_X + i * PLAYER_SPACING
                        y = PLAYER_Y + NORMAL_Y_OFFSET + bounce
                    screen.blit(sprite, (x, y))
                return
            """
            if active_pkmn_info is not None:
                sprite, x, y = active_pkmn_info
                screen.blit(sprite,(x,y))
            if target_pkmn_info is not None:
                sprite, x, y = target_pkmn_info
                screen.blit(sprite,(x,y))

        if b.draw_anim_skill:
            element_color = ELEMENT_COLORS[b.moves[pkmn.moves[b.skills_cursor + b.skills_scroll]]['element']]
            colored_surface = pygame.Surface((ACTUAL_WIDTH, Y_FRAME))
            try:
                t = b.delay_frames / b.delay_target
                t = max(0.0, min(1.0, t))  # clamp
                if t <= 0.5:
                    x = t / 0.5
                else:
                    x = (1 - t) / 0.5
                alpha = x * x * (3 - 2 * x)
            except ZeroDivisionError:
                alpha = 0
            colored_surface.set_alpha(int(MAX_OPACITY_ANIM * alpha))
            colored_surface.fill(element_color)
            screen.blit(colored_surface, (0,0))
            if active_pkmn_info is not None:
                sprite, x, y = active_pkmn_info
                screen.blit(sprite,(x,y))
            if target_pkmn_info is not None:
                sprite, x, y = target_pkmn_info
                screen.blit(sprite,(x,y))
        
        """
        if b.menu_mode in (MENU_MODE_TARGET_SELECT, 
                             MENU_MODE_ITEM_TARGET_SELECT):
        """
        if b.draw_affinity_color:
            selected_move_index = b.skills_cursor + b.skills_scroll
            """
            if b.menu_mode == MENU_MODE_TARGET_SELECT:
                move_name = active_pokemon.moves[selected_index]
            else:
                move_name = b.pending_item_data["type"].split("damage_")[1]
            """
            selected_move = b.moves[b.player_team[b.turn_index].moves[selected_move_index]]
            affinity_value = b.enemy_team[b.target_index].affinities[ELEMENT_INDEX[selected_move["element"]]]
            if  (affinity_value != 0) and \
                (target_pkmn_info is not None):
                sprite, x, y = target_pkmn_info
                flash = (math.sin(self.anim_frame * 0.3) + 1) * 0.5
                alpha = int(120 * flash)
                if affinity_value < AFFINITY_RESIST:
                    flash_color = COLOR_GREEN
                elif AFFINITY_RESIST <= affinity_value < AFFINITY_NULL:
                    flash_color = COLOR_RED
                elif AFFINITY_NULL <= affinity_value < AFFINITY_REFLECT:
                    flash_color = COLOR_BLACK
                elif affinity_value == AFFINITY_REFLECT:
                    flash_color = COLOR_BLACK
                sprite_alpha = sprite.convert_alpha()
                w, h = sprite_alpha.get_size()
                tint = pygame.Surface((w,h), pygame.SRCALPHA)
                tint.fill((*flash_color, 255))
                tint.blit(sprite_alpha, (0,0), special_flags=pygame.BLEND_RGBA_MULT)
                tint.set_alpha(alpha)
                screen.blit(tint, (x,y))


        pkmn_for_hpmp = b.player_team[b.turn_index]
        hpmp_y = Y_HPMP
        enemy_hpmp_y = Y_HPMP_ENEMY
        ui_hp_offset = 0
        """
        if b.menu_mode not in (MENU_MODE_DAMAGING_ENEMY,
                             MENU_MODE_ANNOUNCE_ENEMY_ATTACK,
                             MENU_MODE_DAMAGING_PLAYER):
            hpmp_y += hp_offset
            enemy_hpmp_y += hp_offset
            ui_hp_offset += hp_offset
        """
        if b.draw_hp_bounce:
            hpmp_y += bounce_offset_hp
            enemy_hpmp_y += bounce_offset_hp
            ui_hp_offset += bounce_offset_hp
        """
        if b.menu_mode in (MENU_MODE_ITEM_ALLY_TARGET,
                         MENU_MODE_ITEM_USE,
                         MENU_MODE_TARGET_BUFF,
                         MENU_MODE_BUFF_PLAYER,
                         MENU_MODE_TARGET_HEAL,
                         MENU_MODE_HEAL_USE):
            pokemon_for_hpmp = b.model.player_team[b.selected_ally]
        if b.menu_mode in (MENU_MODE_ANNOUNCE_ENEMY_ATTACK,
                         MENU_MODE_DAMAGING_PLAYER):
            pokemon_for_hpmp = b.model.player_team[b.enemy_target_index]
        if b.menu_mode == MENU_MODE_INFO and b.info_row == 1:
            pokemon_for_hpmp = b.model.player_team[b.info_col]
        """
        """
        if (b.menu_mode not in (MENU_MODE_BUFF_PLAYER_ALL, MENU_MODE_TARGET_BUFF_ALL)) and \
            ((b.menu_mode != MENU_MODE_INFO) or (b.info_row == ROW_PLAYER))
        """
        screen.blit(self.hpmp_sprite, (X_HPMP, hpmp_y))
        self.font1.draw_text(
            screen,
            pkmn_for_hpmp.name,
            X_ACTIVE_POKEMON_NAME,
            hpmp_y + Y_ACTIVE_POKEMON_NAME_OFFSET
        )
        screen.blit(self.lv_sprite, (X_LV, hpmp_y + Y_LV_OFFSET))
        self.font1.draw_text(
            screen,
            str(pkmn_for_hpmp.level),
            X_LV_TEXT,
            hpmp_y + Y_LV_TEXT_OFFSET
        )
        self._draw_hp_bar(screen, pkmn_for_hpmp, ui_hp_offset)
        self._draw_mp_bar(screen, pkmn_for_hpmp, ui_hp_offset)
        hp_source = getattr(pkmn_for_hpmp, "hp_anim", pkmn_for_hpmp.remaining_hp)
        ratio_text = self._format_hpmp_text(pkmn_for_hpmp, hp_override=hp_source)
        self.font3.draw_text(screen,
                             ratio_text,
                             X_HPMP + D_HPMP_RATIO_OFFSET_X,
                             hpmp_y + D_HPMP_RATIO_OFFSET_Y)
        self._draw_stat_buffs(screen, pkmn_for_hpmp,
                              X_BUFF, hpmp_y + Y_BUFF,
                              blink)
        """
        if (b.menu_mode in (MENU_MODE_BUFF_PLAYER_ALL, MENU_MODE_TARGET_BUFF_ALL)):
            self.hpmp_renderer.draw_player_hpmp_all(b,
                                                    screen,
                                                    hpmp_y, 
                                                    ui_hp_offset,
                                                    blink) 

        if b.menu_mode in (MENU_MODE_SKILLS, 
                               MENU_MODE_TARGET_SELECT,
                               MENU_MODE_TARGET_BUFF_ALL,
                               MENU_MODE_TARGET_BUFF,
                               MENU_MODE_TARGET_HEAL)
        """
        if b.draw_mp_cost:
            selected_move = b.moves.get(pkmn.moves[b.skills_cursor + b.skills_scroll])
            """
            if b.menu_mode == MENU_MODE_TARGET_BUFF and \
                b.selected_ally != b.model.turn_index:
                return
            if b.menu_mode == MENU_MODE_TARGET_HEAL and \
                b.selected_ally != b.model.turn_index:
                return
            """
            if selected_move:
                cost = selected_move["mp"]
                remaining_mp = pkmn.remaining_mp
                if (cost <= remaining_mp):
                    pixels_per_mp = W_MP_BAR / pkmn.max_mp
                    remaining_mp_ratio = remaining_mp / pkmn.max_mp
                    fill_width = int(cost * pixels_per_mp)
                    remaining_pixel_width = int((1 - remaining_mp_ratio) * W_MP_BAR)
                    fill_surface = pygame.transform.scale(
                        self.mp_cost_fill, (fill_width, H_MP_BAR)
                    )
                    """
                    if b.menu_mode == MENU_MODE_TARGET_BUFF_ALL:
                        no = b.model.turn_index
                        if no == 0:
                            x_offset = HPMP_X_DIF
                            y_offset = HPMP_Y_DIF
                        elif no == 1:
                            x_offset = 0
                            y_offset = HPMP_Y_DIF
                        elif no == 2:
                            x_offset = HPMP_X_DIF
                            y_offset = 0
                        else:
                            x_offset = 0
                            y_offset = 0
                        right_edge = MP_BAR_X + MP_BAR_WIDTH - rem_width - x_offset
                        left_edge = right_edge - fill_width

                        screen.blit(fill_surface, (left_edge, MP_BAR_Y + hp_offset - y_offset))
                    else:
                    """
                    left_edge = (X_MP_BAR + W_MP_BAR - remaining_pixel_width) - fill_width
                    screen.blit(fill_surface, (left_edge, Y_MP_BAR + ui_hp_offset))
        """
        b.menu_mode in (
            MENU_MODE_TARGET_SELECT,
            MENU_MODE_DAMAGING_ENEMY,
            MENU_MODE_ITEM_TARGET_SELECT,
            MENU_MODE_ANNOUNCE_ENEMY_ATTACK,
            MENU_MODE_DAMAGING_PLAYER,
            MENU_MODE_INFO
        )
        """
        if b.draw_enemy_info:
            """
            if b.menu_mode in (MENU_MODE_TARGET_SELECT,
                            MENU_MODE_DAMAGING_ENEMY,
                            MENU_MODE_ITEM_TARGET_SELECT):
                enemy_for_hpmp = b.model.enemy_team[b.target_index]
            elif b.menu_mode == MENU_MODE_INFO and b.info_row == 0:
                enemy_for_hpmp = b.model.enemy_team[b.info_col]
            else:
                enemy_for_hpmp = b.model.enemy_team[b.active_enemy_index]
            """
            enemy_for_hpmp = b.enemy_team[b.target_index]
            """
            if (b.menu_mode != MENU_MODE_INFO) or \
                (b.info_row == 0):
                self.hpmp_renderer.draw_enemy_hpmp(screen, enemy_for_hpmp, enemy_hpmp_y, ui_hp_offset, blink)
            """
            screen.blit(self.hpmp_sprite_enemy, (X_HPMP_ENEMY, enemy_hpmp_y))
            self.font1.draw_text(
                screen,
                enemy_for_hpmp.name,
                X_ACTIVE_TARGET_NAME,
                enemy_hpmp_y + Y_LV_TEXT_OFFSET_ENEMY
            )
            screen.blit(self.lv_sprite,
                        (X_LV_ENEMY, enemy_hpmp_y + Y_LV_OFFSET_ENEMY))
            self.font1.draw_text(
                screen,
                str(enemy_for_hpmp.level),
                X_LV_TEXT_ENEMY,
                enemy_hpmp_y + Y_LV_TEXT_OFFSET_ENEMY
            )
            hp_source = getattr(enemy_for_hpmp,"hp_anim",enemy_for_hpmp.remaining_hp)
            self._draw_hp_bar(
                screen,
                enemy_for_hpmp,
                ui_hp_offset,
                base_x=X_HPMP_TO_FILL,
                base_y=Y_HPMP_TO_FILL,
                override_hp=hp_source
            )
            hp_cur = f"{hp_source:3d}"
            hp_max = f"{enemy_for_hpmp.max_hp:3d}"
            ratio_text = f"HP{hp_cur}/{hp_max}"
            self.font3.draw_text(
                screen,
                ratio_text,
                X_HPMP_ENEMY + 20,
                enemy_hpmp_y + Y_HPMP_RATIO_OFFSET
            )
            self._draw_stat_buffs(
                screen,
                enemy_for_hpmp,
                X_BUFF_ENEMY,
                enemy_hpmp_y + Y_BUFF_ENEMY,
                blink
            )
        screen.blit(self.bframe, (0, Y_FRAME))
        """
        if b.menu_mode != MENU_MODE_INFO
        """
        press_turn_icon_states = []
        color = "blue" if b.is_player_turn else "red"
        flashing_on = (self.anim_frame // 10) % 2 == 0
        for value in b.press_turns:
            if value == 2:
                press_turn_icon_states.append(f"solid_{color}")
            elif value == 1:
                press_turn_icon_states.append(f"flash_{color}")
            else:
                press_turn_icon_states.append(PT_STATE_TRANSPARENT)
        """
        if b.menu_mode == MENU_MODE_BUFF_PLAYER_ALL:
            hp_offset = 0
        """
        for i, state in enumerate(press_turn_icon_states):
            if (b.is_player_turn):
                x = X_PT + i * D_PT
                if not b.draw_hp_bounce:
                    y = Y_PT
                else:
                    y = Y_PT + bounce_offset_hp
            else:
                x = X_PT_ENEMY + i * D_PT
                y = Y_PT_ENEMY
            self._draw_press_turn_icon(screen, state, x, y, self.anim_frame)
        
        if b.state == STATE_MAIN:
            self.font0.draw_text(screen, f"What will {pkmn.name} do?",
                                X_MENU_MAIN, Y_MENU_MAIN_0)
            self.font0.draw_text(screen, MENU_MAIN_LINE_1,
                                X_MENU_MAIN, Y_MENU_MAIN_1)
            self.font0.draw_text(screen, MENU_MAIN_LINE_2,
                                X_MENU_MAIN, Y_MENU_MAIN_2)
            if b.menu_cursor_y == 0:
                cursor_x, cursor_y = COORDS_MENU_MAIN_0[b.menu_cursor_x]
            else:
                cursor_x, cursor_y = COORDS_MENU_MAIN_1[b.menu_cursor_x]
            screen.blit(self.cursor_sprite, (cursor_x, cursor_y))

        elif b.state == STATE_SKILLS:
            visible_moves = pkmn.moves[b.skills_scroll:b.skills_scroll + 3]
            y = Y_SKILLS
            for move_name in visible_moves:
                text = self._format_move_for_menu(move_name, b.moves, pkmn)
                self.font2.draw_text(
                    screen,
                    text,
                    X_SKILLS,
                    y
                )
                y += Y_SKILLS_INCR
            cursor_x, cursor_y = COORDS_MENU_SKILLS[b.skills_cursor]
            screen.blit(self.cursor_sprite, (cursor_x, cursor_y))
        
        elif b.state == STATE_SKILLS_TARGET_ENEMY:
            selected_move_name = pkmn.moves[b.skills_cursor + b.skills_scroll]
            text = self._format_move_for_menu(selected_move_name,
                                              b.moves,
                                              pkmn)
            y = Y_SKILLS + (b.skills_cursor * Y_SKILLS_INCR)
            self.font2.draw_text(screen, text, X_SKILLS, y)
            cursor_x, cursor_y = COORDS_MENU_SKILLS[b.skills_cursor]
            screen.blit(self.cursor_sprite, (cursor_x, cursor_y))
        
        elif b.state == STATE_SCROLL:
            full_word_lines = self._wrap_text_words(b.scroll_text)
            visible_chars = int(b.scroll_index)
            visible_lines = ["","",""]
            for line_idx, words in enumerate(full_word_lines):
                for word in words:
                    chunk = word + " "
                    if visible_chars >= len(chunk):
                        visible_lines[line_idx] += chunk
                        visible_chars -= len(chunk)
                    else:
                        visible_lines[line_idx] += chunk[:visible_chars]
                        visible_chars = 0
                        break
                if visible_chars == 0:
                    break
            self.font0.draw_text(screen, 
                                 visible_lines[0], 
                                 X_MENU_MAIN,
                                 Y_MENU_MAIN_0)
            self.font0.draw_text(screen,
                                 visible_lines[1],
                                 X_MENU_MAIN,
                                 Y_MENU_MAIN_1)
            self.font0.draw_text(screen,
                                 visible_lines[2],
                                 X_MENU_MAIN,
                                 Y_MENU_MAIN_2)
            """
            if b.scroll_done and not b.damage_done and not b.damage_started:
                if blink:
                    screen.blit(self.cursor_sprite, (CONFIRM_ARROW_X, CONFIRM_ARROW_Y))
                return
            """

        elif b.draw_text_finished:
            full_word_lines = self._wrap_text_words(b.scroll_text)
            visible_lines = ["", "", ""]
            for line_idx, words in enumerate(full_word_lines):
                visible_lines[line_idx] = " ".join(words) + " "
            self.font0.draw_text(screen, 
                                 visible_lines[0], 
                                 X_MENU_MAIN,
                                 Y_MENU_MAIN_0)
            self.font0.draw_text(screen,
                                 visible_lines[1],
                                 X_MENU_MAIN,
                                 Y_MENU_MAIN_1)
            self.font0.draw_text(screen,
                                 visible_lines[2],
                                 X_MENU_MAIN,
                                 Y_MENU_MAIN_2)


        
        # ========================= END DRAW =================================

    def _load_sprite_for_pokemon(self, pokemon, is_back):
        if pokemon is None:
            return None

        if pokemon.is_player:
            return load_player_sprite(scale=SCALE)

        row = pokemon.pokedex_number - 1
        col = pokemon.sprite_column

        return load_pokemon_sprite(row=row, column=col, scale=SCALE)
    
    def _draw_hp_bar(self, screen, pokemon, hp_offset, \
                     base_x=X_HP_BAR, base_y=Y_HP_BAR,
                     override_hp=None):
        if pokemon.max_hp <= 0:
            return
        hp_value = override_hp if override_hp is not None else getattr(pokemon, "hp_anim", pokemon.remaining_hp)
        ratio = max(0.0, min(1.0, hp_value / pokemon.max_hp))
        fill_width = int(W_HP_BAR * ratio)
        if fill_width <= 0:
            return
        fill_surface = pygame.transform.scale(
            self.hp_fill,
            (fill_width, H_HP_BAR)
        )
        screen.blit(fill_surface, (base_x, base_y + hp_offset))

    def _draw_mp_bar(self, screen, pokemon, hp_offset, \
                    base_x=X_MP_BAR, base_y=Y_MP_BAR):
        if pokemon.max_mp <= 0:
            return
        ratio = pokemon.remaining_mp / pokemon.max_mp
        ratio = max(0.0, min(1.0, ratio))
        fill_width = int(W_MP_BAR * ratio)
        if fill_width <= 0:
            return
        fill_surface = pygame.transform.scale(
            self.mp_fill,
            (fill_width, H_MP_BAR)
        )
        screen.blit(fill_surface, (base_x, base_y + hp_offset))

    def _format_hpmp_text(self, pokemon, hp_override=None):
        # Use animated HP if provided, otherwise logical remaining_hp
        hp_value = hp_override if hp_override is not None else pokemon.remaining_hp

        hp_cur = f"{hp_value:3d}"
        hp_max = f"{pokemon.max_hp:3d}"
        mp_cur = f"{pokemon.remaining_mp:3d}"
        mp_max = f"{pokemon.max_mp:3d}"

        hp_text = f"HP{hp_cur}/{hp_max}"
        mp_text = f"MP{mp_cur}/{mp_max}"
        return f"{hp_text}   {mp_text}"
    
        
    def _draw_stat_buffs(self, screen, pokemon, base_x, base_y, blink):
        stage_to_col = {
            +1: 0,
            +2: 1,
            -1: 2,
            -2: 3
        }
        if  (pokemon.attack_buff != 0) and not \
            (pokemon.attack_buff_turns == 1 and not blink):
            screen.blit(self.statbuffdebuff.get((0, stage_to_col[pokemon.attack_buff])),(base_x, base_y))
        if  (pokemon.defense_buff != 0) and not \
            (pokemon.defense_buff_turns == 1 and not blink):
            screen.blit(self.statbuffdebuff.get((1, stage_to_col[pokemon.defense_buff])),(base_x + D_STAT_BUFFS, base_y))
        if  (pokemon.speed_buff != 0) and not \
            (pokemon.speed_buff_turns == 1 and not blink):
            screen.blit(self.statbuffdebuff.get((2, stage_to_col[pokemon.speed_buff])),(base_x + D_STAT_BUFFS + D_STAT_BUFFS, base_y))
    
    def _draw_press_turn_icon(self, screen, state, x, y, anim_frame):
        if state == PT_STATE_TRANSPARENT:
            return
        if state == PT_STATE_SOLIDBLUE:
            screen.blit(self.press_turn_blue, (x, y))
        elif state == PT_STATE_SOLIDRED:
            screen.blit(self.press_turn_red, (x, y))
        elif state == PT_STATE_FLASHBLUE:
            # Flashing: draw only on “on” frames
            if (anim_frame // PT_DURATION_FLASH) % 2 == 0:
                screen.blit(self.press_turn_blue, (x, y))
        elif state == PT_STATE_FLASHRED:
            if (anim_frame // PT_DURATION_FLASH) % 2 == 0:
                screen.blit(self.press_turn_red, (x, y))

    def _format_move_for_menu(self, move_name, moves, active_pokemon):
        m = moves.get(move_name)
        if not m:
            return f"{move_name[:11]:<11} {'---':>3}  {'----':<5}  {'---':>3}  {'---':<12}"

        # Base name (max 11 chars before adding potential)
        base_name = move_name[:11]

        element = m["element"]

        # Determine potential index
        try:
            element_index = POTENTIAL_ORDER.index(element)
            pot = active_pokemon.potential[element_index]
        except ValueError:
            pot = 0

        # Build potential text
        pot_text = f" {pot:+d}" if pot != 0 else ""

        # Ensure name + pot_text fits in 11 chars
        combined = base_name + pot_text
        if len(combined) > 11:
            trim_amount = min(len(combined) - 11, 3)
            base_name = base_name[:-trim_amount]
            combined = base_name + pot_text

        name_field = f"{combined:<11}"

        # Support / Healing formatting
        if element in ("Support", "Healing"):
            mp = f"{m['mp']:>3}"
            element_short = f"{element[:7]:<7}"
            desc = m.get("description", "")[:15]
            desc = f"{desc:<15}"
            return f"{name_field} {mp}  {element_short}  {desc}"

        # Attack formatting
        mp = f"{m['mp']:>3}"
        power = f"{m['power']:>3}" if m["power"] is not None else "---"
        element_short = f"{element[:5]:<5}"
        desc = m.get("description", "")[:12]
        desc = f"{desc:<12}"

        return f"{name_field} {mp}  {element_short}  {power}  {desc}"
    
    def _wrap_text_words(self, text, max_width=32):
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
        while len(lines) < 3:
            lines.append([])
        return lines[:3]