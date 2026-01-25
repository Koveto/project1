import pygame
from constants import *
from battle.battle_constants import *

class HPMPRenderer:
    def __init__(self, font1, font3, hpmp_sprite, lv_sprite, hp_fill, mp_fill, mp_cost_fill):
        self.font1 = font1
        self.font3 = font3
        self.hpmp_sprite = hpmp_sprite
        self.lv_sprite = lv_sprite
        self.hp_fill = hp_fill
        self.mp_fill = mp_fill
        self.mp_cost_fill = mp_cost_fill

    def format_hpmp_text(self, pokemon, hp_override=None):
        # Use animated HP if provided, otherwise logical remaining_hp
        hp_value = hp_override if hp_override is not None else pokemon.remaining_hp

        hp_cur = f"{hp_value:3d}"
        hp_max = f"{pokemon.max_hp:3d}"
        mp_cur = f"{pokemon.remaining_mp:3d}"
        mp_max = f"{pokemon.max_mp:3d}"

        hp_text = f"HP{hp_cur}/{hp_max}"
        mp_text = f"MP{mp_cur}/{mp_max}"
        return f"{hp_text}   {mp_text}"




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

        # --- Draw HP/MP ratio text (temporary placement) ---
        hp_source = getattr(active_pokemon, "hp_anim", active_pokemon.remaining_hp)
        ratio_text = self.format_hpmp_text(active_pokemon, hp_override=hp_source)
        self.font3.draw_text(
            screen,
            ratio_text,
            HPMP_X + 20,                 # temporary X offset
            hpmp_y + HPMP_RATIO_Y_OFFSET # we'll define this next
        )



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
        
        # --- Draw HP/MP ratio text (temporary placement) ---
        ratio_text = self.format_hpmp_text(target, hp_override=hp_source)
        self.font3.draw_text(
            screen,
            ratio_text,
            HPMP_ENEMY_X + 20,                 # temporary X offset
            enemy_hpmp_y + HPMP_RATIO_Y_OFFSET # same offset for now
        )

