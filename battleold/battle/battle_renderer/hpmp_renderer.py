import pygame
from constants import *
from battle.battle_constants import *

class HPMPRenderer:
    def __init__(self, font1, font3, hpmp_sprite, 
                 hpmp_sprite_enemy, lv_sprite, 
                 hp_fill, mp_fill, mp_cost_fill,
                 stat_icon_renderer):
        self.font1 = font1
        self.font3 = font3
        self.hpmp_sprite = hpmp_sprite
        self.hpmp_sprite_enemy = hpmp_sprite_enemy
        self.lv_sprite = lv_sprite
        self.hp_fill = hp_fill
        self.mp_fill = mp_fill
        self.mp_cost_fill = mp_cost_fill
        self.stat_icon_renderer = stat_icon_renderer

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
    
    def format_hpmp_text_enemy(self, pokemon, hp_override=None):
        # Use animated HP if provided, otherwise logical remaining_hp
        hp_value = hp_override if hp_override is not None else pokemon.remaining_hp

        hp_cur = f"{hp_value:3d}"
        hp_max = f"{pokemon.max_hp:3d}"

        hp_text = f"HP{hp_cur}/{hp_max}"
        return f"{hp_text}"

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


    def draw_mp_cost_bar(self, b, screen, move_name, hp_offset):
        if b.menu_mode == MENU_MODE_TARGET_BUFF and \
            b.selected_ally != b.model.turn_index:
            return
        if b.menu_mode == MENU_MODE_TARGET_HEAL and \
            b.selected_ally != b.model.turn_index:
            return

        move = b.smt_moves.get(move_name)
        if not move:
            return

        cost = move["mp"]
        rem_mp = b.model.get_active_pokemon().remaining_mp
        max_mp = b.model.get_active_pokemon().max_mp

        if cost > rem_mp:
            return

        if max_mp <= 0 or cost <= 0:
            return
        
        pixels_per_mp = MP_BAR_WIDTH / max_mp
        
        # Cost as a fraction of max MP
        ratio = cost / max_mp
        ratio = max(0.0, min(1.0, ratio))

        rem = rem_mp / max_mp

        fill_width = int(cost * pixels_per_mp)
        if fill_width <= 0:
            return
        
        rem_width = int((1 - rem) * MP_BAR_WIDTH)

        fill_surface = pygame.transform.scale(
            self.mp_cost_fill,
            (fill_width, MP_BAR_HEIGHT)
        )

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
            # Anchor the cost bar on the RIGHT side of the MP bar
            right_edge = MP_BAR_X + MP_BAR_WIDTH - rem_width
            left_edge = right_edge - fill_width

            screen.blit(fill_surface, (left_edge, MP_BAR_Y + hp_offset))


    def draw_player_hpmp(self, screen, active_pokemon, hpmp_y, ui_hp_offset, blink):
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

        # Draw stat buffs (only if non-zero)
        self.draw_stat_buffs(
            screen,
            active_pokemon,
            BUFF_X,
            hpmp_y + BUFF_Y,
            blink
        )

    def draw_enemy_hpmp(self, screen, target, enemy_hpmp_y, ui_hp_offset, blink):
        # draws the enemy HP/MP UI block
        screen.blit(self.hpmp_sprite_enemy, (HPMP_ENEMY_X, enemy_hpmp_y))

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

        # --- Draw HP/MP ratio text (temporary placement) ---
        ratio_text = self.format_hpmp_text_enemy(target, hp_override=hp_source)
        self.font3.draw_text(
            screen,
            ratio_text,
            HPMP_ENEMY_X + 20,                 # temporary X offset
            enemy_hpmp_y + HPMP_RATIO_Y_OFFSET # same offset for now
        )

        self.draw_stat_buffs(
            screen,
            target,
            BUFF_X_ENEMY,
            enemy_hpmp_y + BUFF_Y_ENEMY,
            blink
        )


    def draw_stat_buffs(self, screen, pokemon, base_x, base_y, blink):
        """
        Draws attack/defense/speed buff icons for the given Pokémon.
        base_x/base_y are BUFF_X/BUFF_Y or BUFF_X_ENEMY/BUFF_Y_ENEMY.
        """

        # Map buff values (-2..+2) to column index in the spritesheet
        stage_to_col = {
            +1: 0,
            +2: 1,
            -1: 2,
            -2: 3
        }

        # Attack
        if pokemon.attack_buff != 0:
            col = stage_to_col[pokemon.attack_buff]

            # Flash if 1 turn left
            if pokemon.attack_buff_turns == 1 and not blink:
                pass
            else:
                self.stat_icon_renderer.draw_buff_icon(
                    screen, 0, col,
                    base_x,
                    base_y
                )


        # Defense
        if pokemon.defense_buff != 0:
            col = stage_to_col[pokemon.defense_buff]

            # Flash if 1 turn left
            if pokemon.defense_buff_turns == 1 and not blink:
                pass
            else:
                self.stat_icon_renderer.draw_buff_icon(
                    screen, 1, col,
                    base_x + BUFF_SPACING,
                    base_y
                )

        # Speed
        if pokemon.speed_buff != 0:
            col = stage_to_col[pokemon.speed_buff]

            # Flash if 1 turn left
            if pokemon.speed_buff_turns == 1 and not blink:
                pass
            else:
                self.stat_icon_renderer.draw_buff_icon(
                    screen, 2, col,
                    base_x + BUFF_SPACING + BUFF_SPACING,
                    base_y
                )


    def draw_player_hpmp_all(self, b, screen, hpmp_y, ui_hp_offset, blink):

        if b.menu_mode == MENU_MODE_TARGET_BUFF_ALL:
            bounce = 0
        else:
            bounce = -1 * ui_hp_offset

        screen.blit(self.hpmp_sprite, (HPMP_X, hpmp_y + bounce))
        screen.blit(self.hpmp_sprite, (HPMP_X - HPMP_X_DIF, hpmp_y + bounce))
        screen.blit(self.hpmp_sprite, (HPMP_X - HPMP_X_DIF, hpmp_y - HPMP_Y_DIF + bounce))
        screen.blit(self.hpmp_sprite, (HPMP_X, hpmp_y - HPMP_Y_DIF + bounce))

        self.font1.draw_text(
            screen,
            b.model.get_player_team()[3].name,
            ACTIVE_POKEMON_NAME_X,
            hpmp_y + ACTIVE_POKEMON_NAME_Y_OFFSET + bounce
        )
        self.font1.draw_text(
            screen,
            b.model.get_player_team()[2].name,
            ACTIVE_POKEMON_NAME_X - HPMP_X_DIF,
            hpmp_y + ACTIVE_POKEMON_NAME_Y_OFFSET + bounce
        )
        self.font1.draw_text(
            screen,
            b.model.get_player_team()[0].name,
            ACTIVE_POKEMON_NAME_X - HPMP_X_DIF,
            hpmp_y + ACTIVE_POKEMON_NAME_Y_OFFSET - HPMP_Y_DIF + bounce
        )
        self.font1.draw_text(
            screen,
            b.model.get_player_team()[1].name,
            ACTIVE_POKEMON_NAME_X,
            hpmp_y + ACTIVE_POKEMON_NAME_Y_OFFSET - HPMP_Y_DIF + bounce
        )

        screen.blit(self.lv_sprite, (LV_X, hpmp_y + LV_Y_OFFSET + bounce))
        screen.blit(self.lv_sprite, (LV_X - HPMP_X_DIF, hpmp_y + LV_Y_OFFSET + bounce))
        screen.blit(self.lv_sprite, (LV_X - HPMP_X_DIF, hpmp_y + LV_Y_OFFSET - HPMP_Y_DIF + bounce))
        screen.blit(self.lv_sprite, (LV_X, hpmp_y + LV_Y_OFFSET - HPMP_Y_DIF + bounce))

        self.font1.draw_text(
            screen,
            str(b.model.get_player_team()[3].level),
            LV_TEXT_X,
            hpmp_y + LV_TEXT_Y_OFFSET + bounce
        )
        self.font1.draw_text(
            screen,
            str(b.model.get_player_team()[2].level),
            LV_TEXT_X - HPMP_X_DIF,
            hpmp_y + LV_TEXT_Y_OFFSET + bounce
        )
        self.font1.draw_text(
            screen,
            str(b.model.get_player_team()[0].level),
            LV_TEXT_X - HPMP_X_DIF,
            hpmp_y + LV_TEXT_Y_OFFSET - HPMP_Y_DIF + bounce
        )
        self.font1.draw_text(
            screen,
            str(b.model.get_player_team()[1].level),
            LV_TEXT_X,
            hpmp_y + LV_TEXT_Y_OFFSET - HPMP_Y_DIF + bounce
        )

        self.draw_hp_bar(screen, b.model.get_player_team()[3], ui_hp_offset, base_x=(HP_BAR_X), base_y=(HP_BAR_Y + bounce))
        self.draw_mp_bar(screen, b.model.get_player_team()[3], ui_hp_offset, base_x=(MP_BAR_X), base_y=(MP_BAR_Y + bounce))
        self.draw_hp_bar(screen, b.model.get_player_team()[2], ui_hp_offset, base_x=(HP_BAR_X - HPMP_X_DIF), base_y=(HP_BAR_Y + bounce))
        self.draw_mp_bar(screen, b.model.get_player_team()[2], ui_hp_offset, base_x=(MP_BAR_X - HPMP_X_DIF), base_y=(MP_BAR_Y + bounce))
        self.draw_hp_bar(screen, b.model.get_player_team()[0], ui_hp_offset, base_x=(HP_BAR_X - HPMP_X_DIF), base_y=(HP_BAR_Y - HPMP_Y_DIF + bounce))
        self.draw_mp_bar(screen, b.model.get_player_team()[0], ui_hp_offset, base_x=(MP_BAR_X - HPMP_X_DIF), base_y=(MP_BAR_Y - HPMP_Y_DIF + bounce))
        self.draw_hp_bar(screen, b.model.get_player_team()[1], ui_hp_offset, base_x=(HP_BAR_X), base_y=(HP_BAR_Y - HPMP_Y_DIF + bounce))
        self.draw_mp_bar(screen, b.model.get_player_team()[1], ui_hp_offset, base_x=(MP_BAR_X), base_y=(MP_BAR_Y - HPMP_Y_DIF + bounce))

        # --- Draw HP/MP ratio text (temporary placement) ---
        hp_source = getattr(b.model.get_player_team()[3], "hp_anim", b.model.get_player_team()[3].remaining_hp)
        ratio_text = self.format_hpmp_text(b.model.get_player_team()[3], hp_override=hp_source)
        self.font3.draw_text(
            screen,
            ratio_text,
            HPMP_X + 20, 
            hpmp_y + HPMP_RATIO_Y_OFFSET + bounce
        )
        hp_source = getattr(b.model.get_player_team()[2], "hp_anim", b.model.get_player_team()[2].remaining_hp)
        ratio_text = self.format_hpmp_text(b.model.get_player_team()[2], hp_override=hp_source)
        self.font3.draw_text(
            screen,
            ratio_text,
            HPMP_X + 20 - HPMP_X_DIF, 
            hpmp_y + HPMP_RATIO_Y_OFFSET + bounce
        )
        hp_source = getattr(b.model.get_player_team()[0], "hp_anim", b.model.get_player_team()[0].remaining_hp)
        ratio_text = self.format_hpmp_text(b.model.get_player_team()[0], hp_override=hp_source)
        self.font3.draw_text(
            screen,
            ratio_text,
            HPMP_X + 20 - HPMP_X_DIF, 
            hpmp_y + HPMP_RATIO_Y_OFFSET - HPMP_Y_DIF + bounce
        )
        hp_source = getattr(b.model.get_player_team()[1], "hp_anim", b.model.get_player_team()[1].remaining_hp)
        ratio_text = self.format_hpmp_text(b.model.get_player_team()[1], hp_override=hp_source)
        self.font3.draw_text(
            screen,
            ratio_text,
            HPMP_X + 20, 
            hpmp_y + HPMP_RATIO_Y_OFFSET - HPMP_Y_DIF + bounce
        )

        # Draw stat buffs (only if non-zero)
        self.draw_stat_buffs(
            screen,
            b.model.get_player_team()[3],
            BUFF_X,
            hpmp_y + BUFF_Y + bounce,
            blink
        )
        self.draw_stat_buffs(
            screen,
            b.model.get_player_team()[2],
            BUFF_X - HPMP_X_DIF,
            hpmp_y + BUFF_Y + bounce,
            blink
        )
        self.draw_stat_buffs(
            screen,
            b.model.get_player_team()[0],
            BUFF_X - HPMP_X_DIF,
            hpmp_y + BUFF_Y - HPMP_Y_DIF + bounce,
            blink
        )
        self.draw_stat_buffs(
            screen,
            b.model.get_player_team()[1],
            BUFF_X,
            hpmp_y + BUFF_Y - HPMP_Y_DIF + bounce,
            blink
        )