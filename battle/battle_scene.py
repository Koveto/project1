# battle/battle_scene.py  (recommended new name)

import pygame, math
from constants import *
from battle.battle_constants import *
from battle.battle_font import BattleFont
from pokedex.pokemon_sprites import load_pokemon_sprite, load_player_sprite

# Modular renderers
from battle.battle_renderer.text_renderer import TextRenderer
from battle.battle_renderer.background_renderer import BackgroundRenderer
from battle.battle_renderer.hpmp_renderer import HPMPRenderer
from battle.battle_renderer.menu_renderer import MenuRenderer
from battle.battle_renderer.press_turn_renderer import PressTurnRenderer
from battle.battle_renderer.animation_renderer import AnimationRenderer
from battle.battle_renderer.stat_icon_renderer import StatIconRenderer


class BattleRenderer:
    """Coordinates all battle rendering subsystems."""

    def __init__(self, background_surface, model, moves):

        # Core references
        self.background = background_surface
        self.model = model
        self.smt_moves = moves

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
        self.battleframe = load_scaled_sprite(sprite_path(FILENAME_FRAME), scale=SCALE)

        # Press Turn icons
        self.press_turn_red = load_scaled_sprite(sprite_path(FILENAME_PBRED), scale=SCALE_PRESSTURN, colorkey=COLOR_MAGENTA)
        self.press_turn_blue = load_scaled_sprite(sprite_path(FILENAME_PBBLUE), scale=SCALE_PRESSTURN, colorkey=COLOR_MAGENTA)

        # Pokémon sprites
        self.player_sprites = [
            self._load_sprite_for_pokemon(p, is_back=True) if p else None
            for p in model.player_team
        ]
        self.enemy_sprites = [
            self._load_sprite_for_pokemon(p, is_back=False) if p else None
            for p in model.enemy_team
        ]

        # Sub-renderers
        self.stat_icon_renderer = StatIconRenderer()
        self.text_renderer = TextRenderer(self.font0, self.cursor_sprite)
        self.background_renderer = BackgroundRenderer(background_surface, self.player_sprites, self.enemy_sprites, self.smt_moves)
        self.hpmp_renderer = HPMPRenderer(self.font1, self.font3, self.hpmp_sprite, self.hpmp_sprite_enemy, self.lv_sprite, self.hp_fill, self.mp_fill, self.mp_cost_fill, self.stat_icon_renderer)
        self.menu_renderer = MenuRenderer(self.font0, self.font2, self.cursor_sprite, self.smt_moves)
        self.press_turn_renderer = PressTurnRenderer(self.press_turn_blue, self.press_turn_red)
        self.animation = AnimationRenderer()


    # ---------------------------------------------------------
    # Sprite loading
    # ---------------------------------------------------------
    def _load_sprite_for_pokemon(self, pokemon, is_back):
        """Loads either the player sprite or a Pokémon sprite."""
        if pokemon is None:
            return None

        if pokemon.is_player:
            return load_player_sprite(scale=SCALE)

        dex = pokemon.pokedex_number
        index = dex - 1 if is_back else (dex * 2) - 2

        return load_pokemon_sprite(
            gen=pokemon.gen,
            index=index,
            is_shiny=pokemon.is_shiny,
            is_back=is_back,
            scale=SCALE
        )
    
    def _call_menu_mode_function(self,
                                 menu_mode,
                                 screen,
                                 active_pokemon,
                                 menu_index,
                                 skills_scroll,
                                 skills_cursor,
                                 scroll_text,
                                 scroll_index,
                                 scroll_done,
                                 damage_done,
                                 affinity_done,
                                 affinity_text,
                                 affinity_scroll_index,
                                 affinity_scroll_done,
                                 damage_text,
                                 damage_scroll_index,
                                 damage_scroll_done,
                                 blink,
                                 inventory,
                                 item_cursor_x,
                                 item_cursor_y,
                                 pending_item_data,
                                 item_use_text,
                                 item_use_scroll_done,
                                 item_use_scroll_index,
                                 item_recover_text,
                                 item_recover_scroll_index,
                                 item_recover_scroll_done,
                                 previous_menu_index):
        if menu_mode == MENU_MODE_MAIN:
            self.menu_renderer.draw_main_menu(screen, active_pokemon, menu_index)

        elif menu_mode == MENU_MODE_SKILLS:
            self.menu_renderer.draw_skills_menu(screen, active_pokemon, skills_scroll, skills_cursor)

        elif menu_mode == MENU_MODE_TARGET_SELECT:
            self.menu_renderer.draw_target_select_menu(
                screen,
                active_pokemon,
                skills_scroll,
                skills_cursor
            )

        elif menu_mode == MENU_MODE_DAMAGING_ENEMY:
            self.text_renderer.draw_damaging_enemy(
                screen, scroll_text, scroll_index, scroll_done,
                damage_done, affinity_done, affinity_text,
                affinity_scroll_index, affinity_scroll_done, 
                damage_text, damage_scroll_index, damage_scroll_done, 
                blink
            )
            return
        
        elif menu_mode == MENU_MODE_ITEMS:
            self.menu_renderer.draw_item_menu(
                screen,
                inventory,
                item_cursor_x,
                item_cursor_y
            )
            return
        
        elif menu_mode == MENU_MODE_ITEM_INFO:
            self.menu_renderer.draw_item_info(
                screen,
                pending_item_data,
                self.text_renderer
            )
            return

        elif menu_mode == MENU_MODE_ITEM_USE:
            self.text_renderer.draw_item_use(
                screen,
                item_use_text,
                item_use_scroll_index,
                item_use_scroll_done,
                item_recover_text,
                item_recover_scroll_index,
                item_recover_scroll_done,
                blink
            )
            return
        
        elif menu_mode == MENU_MODE_ITEM_TARGET_SELECT:
            self.menu_renderer.draw_item_target_select_menu(
                screen,
                active_pokemon,
                skills_scroll,
                skills_cursor,
                pending_item_data
            )
        
        elif menu_mode == MENU_MODE_GUARDING:
            self.text_renderer.draw_simple_scroll(
                screen,
                scroll_text,
                scroll_index,
                scroll_done,
                blink
            )
            return
        
        elif menu_mode == MENU_MODE_TALK:
            self.text_renderer.draw_simple_scroll(
                screen, scroll_text, scroll_index, scroll_done, blink
            )
            return

        elif menu_mode == MENU_MODE_ESCAPE:
            self.text_renderer.draw_simple_scroll(
                screen, scroll_text, scroll_index, scroll_done, blink
            )
            return
        
        elif menu_mode == MENU_MODE_DAMAGING_PLAYER:
            self.text_renderer.draw_enemy_attack_text(
                screen,
                scroll_text,
                scroll_index,
                scroll_done,
                blink
            )
            return
        
        elif menu_mode == MENU_MODE_ENEMY_DAMAGE:
            # Enemy damage phase uses the same multi-phase renderer
            # as the player-side damaging phase.
            self.text_renderer.draw_damaging_enemy(
                screen,
                scroll_text,
                scroll_index,
                scroll_done,
                damage_done,
                affinity_done,
                affinity_text,
                affinity_scroll_index,
                affinity_scroll_done,
                damage_text,
                damage_scroll_index,
                damage_scroll_done,
                blink
            )
            return

        elif menu_mode == MENU_MODE_INFO:
            self.font0.draw_text(screen, "Press X to return", X_MENU_MAIN, Y_MENU_MAIN_0)

        else:
            self.menu_renderer.draw_dummy_menu(screen, previous_menu_index)

    def _draw_press_turn_icons(self,
                               screen,
                               menu_mode,
                               hp_offset):
        press_turn_states = self.model.get_press_turn_icon_states(self.animation.anim_frame)
        self.press_turn_renderer.draw_all(screen, press_turn_states, menu_mode, hp_offset, self.animation.anim_frame, self.model.is_player_turn)

    def _is_drawn_press_turn_icons(self, menu_mode):
        return menu_mode != MENU_MODE_INFO
    
    def _draw_enemy_hpmp(self,
                         menu_mode,
                         target,
                         info_row,
                         info_col,
                         active_enemy_index,
                         screen,
                         enemy_hpmp_y,
                         ui_hp_offset,
                         blink):
        if menu_mode in (MENU_MODE_TARGET_SELECT,
                        MENU_MODE_DAMAGING_ENEMY,
                        MENU_MODE_ITEM_TARGET_SELECT):
            enemy_for_hpmp = target
        elif menu_mode == MENU_MODE_INFO and info_row == 0:
            enemy_for_hpmp = self.model.enemy_team[info_col]
        else:
            enemy_for_hpmp = self.model.enemy_team[active_enemy_index]
        if (menu_mode != MENU_MODE_INFO) or \
            (info_row == 0):
            self.hpmp_renderer.draw_enemy_hpmp(screen, enemy_for_hpmp, enemy_hpmp_y, ui_hp_offset, blink)

    def _is_drawn_enemy_hpmp(self, menu_mode):
        return menu_mode in (
            MENU_MODE_TARGET_SELECT,
            MENU_MODE_DAMAGING_ENEMY,
            MENU_MODE_ITEM_TARGET_SELECT,
            MENU_MODE_DAMAGING_PLAYER,
            MENU_MODE_ENEMY_DAMAGE,
            MENU_MODE_INFO
        )
    
    def _draw_mpcost(self, skills_cursor, screen, ui_hp_offset):
        move_name = self.model.get_active_pokemon().moves[skills_cursor]
        self.hpmp_renderer.draw_mp_cost_bar(
            screen,
            self.model.get_active_pokemon(),
            move_name,
            ui_hp_offset,
            self.smt_moves
        )

    def _is_drawn_mpcost(self, menu_mode):
        return menu_mode in (MENU_MODE_SKILLS, MENU_MODE_TARGET_SELECT)
    
    def _is_drawn_player_hpmp(self, menu_mode, info_row):
        return (menu_mode != MENU_MODE_INFO) or (info_row == ROW_PLAYER)
            
    def _draw_player_hpmp(self,
                              screen,
                              pokemon_for_hpmp,
                              hpmp_y,
                              ui_hp_offset,
                              blink):
        self.hpmp_renderer.draw_player_hpmp(screen, pokemon_for_hpmp, hpmp_y, ui_hp_offset, blink)

    def _get_data_hpmp(self, 
                       menu_mode, 
                       hp_offset, 
                       active_pokemon, 
                       selected_ally,
                       enemy_target_index,
                       info_row,
                       info_col):
        hpmp_y = HPMP_Y
        enemy_hpmp_y = HPMP_ENEMY_Y
        ui_hp_offset = 0
        pokemon_for_hpmp = None
        if menu_mode not in (MENU_MODE_DAMAGING_ENEMY,
                             MENU_MODE_DAMAGING_PLAYER,
                             MENU_MODE_ENEMY_DAMAGE):
            hpmp_y += hp_offset
            enemy_hpmp_y += hp_offset
            ui_hp_offset += hp_offset
        pokemon_for_hpmp = active_pokemon
        if menu_mode in (MENU_MODE_ITEM_INFO,
                         MENU_MODE_ITEM_USE):
            pokemon_for_hpmp = self.model.player_team[selected_ally]
        if menu_mode in (MENU_MODE_DAMAGING_PLAYER,
                         MENU_MODE_ENEMY_DAMAGE):
            pokemon_for_hpmp = self.model.player_team[enemy_target_index]
        if menu_mode == MENU_MODE_INFO and info_row == 1:
            pokemon_for_hpmp = self.model.player_team[info_col]
        return (hpmp_y, enemy_hpmp_y, ui_hp_offset, pokemon_for_hpmp)
    
    def _get_data_dark_overlay(self, 
              menu_mode,
              info_row,
              info_col,
              poke_offset,
              target_enemy_pos,
              selected_ally,
              enemy_target_index,
              screen,
              bounce_index):
        highlight_player_pos = self.background_renderer.draw_players(
            screen, menu_mode, bounce_index, poke_offset, self.model
        )
        target_enemy_pos = target_enemy_pos
        if menu_mode == MENU_MODE_ITEM_INFO:
            sprite = self.background_renderer.player_sprites[selected_ally]
            pokemon = self.model.player_team[selected_ally]

            x = PLAYER_BASE_X + selected_ally * PLAYER_SPACING
            if pokemon.is_player:
                x += PLAYER_OFFSET
                y = PLAYER_Y + PLAYER_Y_OFFSET
            else:
                y = PLAYER_Y + NORMAL_Y_OFFSET

            y += poke_offset
            highlight_player_pos = (sprite, x, y)
        if menu_mode in (MENU_MODE_DAMAGING_PLAYER,
                         MENU_MODE_ENEMY_DAMAGE):
            sprite = self.background_renderer.player_sprites[enemy_target_index]
            pokemon = self.model.player_team[enemy_target_index]

            x = PLAYER_BASE_X + enemy_target_index * PLAYER_SPACING
            if pokemon.is_player:
                x += PLAYER_OFFSET
                y = PLAYER_Y + PLAYER_Y_OFFSET
            else:
                y = PLAYER_Y + NORMAL_Y_OFFSET

            highlight_player_pos = (sprite, x, y)
        if menu_mode == MENU_MODE_INFO:
            if info_row == ROW_ENEMY:
                sprite = self.background_renderer.enemy_sprites[info_col]
                pokemon = self.model.enemy_team[info_col]

                x = ENEMY_BASE_X + info_col * ENEMY_SPACING
                y = ENEMY_Y + poke_offset

                highlight_player_pos = None
                target_enemy_pos = (sprite, x, y)
            if info_row == ROW_PLAYER:
                sprite = self.background_renderer.player_sprites[info_col]
                pokemon = self.model.player_team[info_col]

                x = PLAYER_BASE_X + info_col * PLAYER_SPACING
                if pokemon.is_player:
                    x += PLAYER_OFFSET
                    y = PLAYER_Y + PLAYER_Y_OFFSET + poke_offset
                else:
                    y = PLAYER_Y + NORMAL_Y_OFFSET + poke_offset

                highlight_player_pos = (sprite, x, y)
                target_enemy_pos = None
        return (highlight_player_pos, target_enemy_pos)
    
    def _get_data_bounce_index(self,
                               menu_mode,
                               selected_ally,
                               enemy_target_index,
                               info_row,
                               info_col):
        bounce_index = self.model.turn_index
        if menu_mode == MENU_MODE_ITEM_INFO:
            bounce_index = selected_ally
        elif menu_mode == MENU_MODE_DAMAGING_PLAYER:
            bounce_index = enemy_target_index
        elif menu_mode == MENU_MODE_INFO:
            if info_row == ROW_PLAYER:
                bounce_index = info_col
            else:
                bounce_index = ROW_NOT_INFO_STATE
        return bounce_index


    # ---------------------------------------------------------
    # Main draw function
    # ---------------------------------------------------------
    def draw(self, screen, menu_index, menu_mode, previous_menu_index,
             skills_cursor, skills_scroll, target_index,
             scroll_text, scroll_index, scroll_done,
             damage_done, affinity_done, affinity_text,
             affinity_scroll_index, affinity_scroll_done,
             inventory, item_cursor_x, item_cursor_y,
             pending_item_data, selected_ally,
             damage_text, damage_scroll_index, damage_scroll_done,
             item_use_text, item_use_scroll_index,
             item_use_scroll_done,
             item_recover_text, item_recover_scroll_index, item_recover_scroll_done,
             enemy_target_index, active_enemy_index,
             info_row, info_col):

        self.animation.update()
        blink = self.animation.get_blink()
        poke_offset, hp_offset = self.animation.get_bounce_offsets()

        self.background_renderer.draw_background(screen)
        
        target_enemy_pos = self.background_renderer.draw_enemies(screen, menu_mode, 
                                                                 target_index, poke_offset,
                                                                 info_row, info_col,
                                                                 active_enemy_index)
        
        bounce_index = self._get_data_bounce_index(menu_mode,
                                                   selected_ally,
                                                   enemy_target_index,
                                                   info_row,
                                                   info_col)

        highlight_player_pos, \
        target_enemy_pos = self._get_data_dark_overlay(menu_mode,
                                      info_row,
                                      info_col,
                                      poke_offset,
                                      target_enemy_pos,
                                      selected_ally,
                                      enemy_target_index,
                                      screen,
                                      bounce_index)

        self.background_renderer.draw_dark_overlay(
            screen,
            menu_mode,
            highlight_player_pos,
            target_enemy_pos
        )

        self.background_renderer.draw_affinity_flash(screen, 
                                                     menu_mode, 
                                                     self.model.player_team[self.model.turn_index],
                                                     skills_scroll, 
                                                     skills_cursor, 
                                                     self.model.enemy_team[target_index],
                                                     self.animation.anim_frame, 
                                                     target_enemy_pos,
                                                     pending_item_data)

        hpmp_y, \
        enemy_hpmp_y, \
        ui_hp_offset, \
        pokemon_for_hpmp = self._get_data_hpmp(
                       menu_mode, 
                       hp_offset, 
                       self.model.player_team[self.model.turn_index], 
                       selected_ally,
                       enemy_target_index,
                       info_row,
                       info_col)        

        if self._is_drawn_player_hpmp(menu_mode, info_row):
            self._draw_player_hpmp(screen,
                                   pokemon_for_hpmp,
                                   hpmp_y,
                                   ui_hp_offset,
                                   blink)        

        if self._is_drawn_mpcost(menu_mode):
            self._draw_mpcost(skills_cursor, screen, ui_hp_offset)

        if self._is_drawn_enemy_hpmp(menu_mode):
            self._draw_enemy_hpmp(menu_mode,
                                  self.model.enemy_team[target_index],
                                  info_row,
                                  info_col,
                                  active_enemy_index,
                                  screen,
                                  enemy_hpmp_y,
                                  ui_hp_offset,
                                  blink)

        screen.blit(self.battleframe, COORDS_FRAME)

        # Press Turn icons
        if self._is_drawn_press_turn_icons(menu_mode):
            self._draw_press_turn_icons(screen,
                                        menu_mode,
                                        hp_offset)

        # Menus + text
        self._call_menu_mode_function(
                                 menu_mode,
                                 screen,
                                 self.model.player_team[self.model.turn_index],
                                 menu_index,
                                 skills_scroll,
                                 skills_cursor,
                                 scroll_text,
                                 scroll_index,
                                 scroll_done,
                                 damage_done,
                                 affinity_done,
                                 affinity_text,
                                 affinity_scroll_index,
                                 affinity_scroll_done,
                                 damage_text,
                                 damage_scroll_index,
                                 damage_scroll_done,
                                 blink,
                                 inventory,
                                 item_cursor_x,
                                 item_cursor_y,
                                 pending_item_data,
                                 item_use_text,
                                 item_use_scroll_done,
                                 item_use_scroll_index,
                                 item_recover_text,
                                 item_recover_scroll_index,
                                 item_recover_scroll_done,
                                 previous_menu_index)
        
