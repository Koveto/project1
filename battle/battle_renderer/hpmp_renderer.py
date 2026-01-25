import pygame
from constants import *
from battle.battle_constants import *

class HPMPRenderer:
    def __init__(self, font1, hpmp_sprite, lv_sprite, hp_fill, mp_fill, mp_cost_fill):
        self.font1 = font1
        self.hpmp_sprite = hpmp_sprite
        self.lv_sprite = lv_sprite
        self.hp_fill = hp_fill
        self.mp_fill = mp_fill
        self.mp_cost_fill = mp_cost_fill

    def draw_hp_bar(self, screen, pokemon, hp_offset,
                base_x=HP_BAR_X, base_y=HP_BAR_Y,
                override_hp=None):

        # Safety: no HP bar if max HP is invalid
        if pokemon.max_hp <= 0:
            return

        # Use animated HP if provided, otherwise use the real remaining HP
        hp_value = override_hp if override_hp is not None else getattr(pokemon, "hp_anim", pokemon.remaining_hp)

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


    def draw_mp_cost_bar(self, screen, pokemon, move_name, hp_offset, smt_moves):
        move = smt_moves.get(move_name)
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


    def draw_player_hpmp(self, screen, active_pokemon, hpmp_y, ui_hp_offset):
        # draws the player HP/MP UI block
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


    def draw_enemy_hpmp(self, screen, target, enemy_hpmp_y, ui_hp_offset):
        # draws the enemy HP/MP UI block
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
