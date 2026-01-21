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

        # UI sprites
        self.hp_fill = load_scaled_sprite(sprite_path(FILENAME_HPFILL), scale=SCALE)
        self.mp_fill = load_scaled_sprite(sprite_path(FILENAME_MPFILL), scale=SCALE)
        self.mp_cost_fill = load_scaled_sprite(sprite_path(FILENAME_MPCOSTFILL), scale=SCALE)
        self.cursor_sprite = load_scaled_sprite(sprite_path(FILENAME_CURSOR), scale=SCALE, colorkey=COLOR_WHITE)
        self.hpmp_sprite = load_scaled_sprite(sprite_path(FILENAME_HPMP), scale=SCALE, colorkey=COLOR_MAGENTA)
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
        self.text_renderer = TextRenderer(self.font0, self.cursor_sprite)
        self.background_renderer = BackgroundRenderer(background_surface, self.player_sprites, self.enemy_sprites, self.smt_moves)
        self.hpmp_renderer = HPMPRenderer(self.font1, self.hpmp_sprite, self.lv_sprite, self.hp_fill, self.mp_fill, self.mp_cost_fill)
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


    # ---------------------------------------------------------
    # Main draw function
    # ---------------------------------------------------------
    def draw(self, screen, menu_index, menu_mode, previous_menu_index,
             skills_cursor, skills_scroll, target_index,
             scroll_text, scroll_index, scroll_done,
             damage_done, affinity_done, affinity_text,
             affinity_scroll_index, affinity_scroll_done):

        # Active Pokémon
        active_index = self.model.turn_index
        active_pokemon = self.model.player_team[active_index]
        target = self.model.enemy_team[target_index]

        # Animation
        self.animation.update()
        blink = self.animation.get_blink()
        poke_offset, hp_offset = self.animation.get_bounce_offsets()

        # Background + sprites
        self.background_renderer.draw_background(screen)
        target_enemy_pos = self.background_renderer.draw_enemies(screen, menu_mode, target_index, poke_offset)
        active_pokemon_pos = self.background_renderer.draw_players(screen, menu_mode, active_index, poke_offset, self.model)
        self.background_renderer.draw_dark_overlay(screen, menu_mode, active_pokemon_pos, target_enemy_pos)
        self.background_renderer.draw_affinity_flash(screen, menu_mode, active_pokemon,
                                                     skills_scroll, skills_cursor, target,
                                                     self.animation.anim_frame, target_enemy_pos)

        # HP/MP UI
        if menu_mode == MENU_MODE_DAMAGING_ENEMY:
            hpmp_y = HPMP_Y
            enemy_hpmp_y = HPMP_ENEMY_Y
            ui_hp_offset = 0
        else:
            hpmp_y = HPMP_Y + hp_offset
            enemy_hpmp_y = HPMP_ENEMY_Y + hp_offset
            ui_hp_offset = hp_offset

        self.hpmp_renderer.draw_player_hpmp(screen, active_pokemon, hpmp_y, ui_hp_offset)

        if menu_mode in (MENU_MODE_TARGET_SELECT, MENU_MODE_DAMAGING_ENEMY):
            self.hpmp_renderer.draw_enemy_hpmp(screen, target, enemy_hpmp_y, ui_hp_offset)

        screen.blit(self.battleframe, COORDS_FRAME)

        # Press Turn icons
        press_turn_states = self.model.get_press_turn_icon_states(self.animation.anim_frame)
        self.press_turn_renderer.draw_all(screen, press_turn_states, menu_mode, hp_offset, self.animation.anim_frame)

        # Menus + text
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
                affinity_scroll_index, affinity_scroll_done, blink
            )
            return

        else:
            self.menu_renderer.draw_dummy_menu(screen, previous_menu_index)
