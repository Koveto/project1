import pygame, math
from constants import *
from battle.battle_constants import *

class BackgroundRenderer:
    def __init__(self, background_surface, player_sprites, enemy_sprites, smt_moves):
        self.background = background_surface
        self.player_sprites = player_sprites
        self.enemy_sprites = enemy_sprites
        self.smt_moves = smt_moves

    def draw_background(self, screen):
        screen.blit(self.background, COORDS_BACKGROUND)

    def draw_enemies(self, b, screen, poke_offset):
        target_enemy_pos = None
        info_index = ROW_NOT_INFO_STATE
        if b.menu_mode == MENU_MODE_INFO:
            if b.info_row == 0:
                info_index = b.info_col

        for i in ENEMY_DRAW_ORDER:
            sprite = self.enemy_sprites[i]
            if sprite is None:
                continue

            x = ENEMY_BASE_X + i * ENEMY_SPACING
            y = ENEMY_Y

            # Bounce only during target selection
            if b.menu_mode in (MENU_MODE_TARGET_SELECT, MENU_MODE_ITEM_TARGET_SELECT):
                if i == b.target_index:
                    y += poke_offset
            if b.menu_mode == MENU_MODE_INFO:
                if i == info_index:
                    y += poke_offset

            # Draw sprite
            screen.blit(sprite, (x, y))

            # NORMAL CASE: highlight the target enemy
            if b.menu_mode not in (MENU_MODE_DAMAGING_PLAYER, MENU_MODE_ENEMY_DAMAGE):
                if i == b.target_index:
                    target_enemy_pos = (sprite, x, y)

            elif b.menu_mode == MENU_MODE_INFO:
                target_enemy_pos = (sprite, x, y)

            # ENEMY TURN CASE: highlight the attacking enemy
            else:
                if b.active_enemy_index is not None and i == b.active_enemy_index:
                    target_enemy_pos = (sprite, x, y)

        return target_enemy_pos


    def draw_players(self, b, screen, active_index, poke_offset):
        active_pokemon_pos = None

        for i, sprite in enumerate(self.player_sprites):
            if sprite is None:
                continue

            pokemon = b.model.player_team[i]

            x = PLAYER_BASE_X + i * PLAYER_SPACING

            if pokemon.is_player:
                x += PLAYER_OFFSET
                y = PLAYER_Y + PLAYER_Y_OFFSET
            else:
                y = PLAYER_Y + NORMAL_Y_OFFSET

            if (b.menu_mode == MENU_MODE_TARGET_BUFF_ALL) or (i == active_index and b.menu_mode not in (MENU_MODE_DAMAGING_ENEMY,
                                                       MENU_MODE_DAMAGING_PLAYER,
                                                       MENU_MODE_ENEMY_DAMAGE)):
                y += poke_offset

            screen.blit(sprite, (x, y))

            if i == active_index:
                active_pokemon_pos = (sprite, x, y)

        return active_pokemon_pos

    def draw_dark_overlay(self, b, screen, highlight_player_pos, target_enemy_pos, poke_offset):
        if b.menu_mode not in (
            MENU_MODE_TARGET_SELECT,
            MENU_MODE_DAMAGING_ENEMY,
            MENU_MODE_ITEM_ALLY_TARGET,
            MENU_MODE_ITEM_TARGET_SELECT,
            MENU_MODE_DAMAGING_PLAYER,
            MENU_MODE_ENEMY_DAMAGE,
            MENU_MODE_INFO,
            MENU_MODE_TARGET_BUFF,
            MENU_MODE_TARGET_BUFF_ALL,
            MENU_MODE_BUFF_PLAYER,
            MENU_MODE_BUFF_PLAYER_ALL
        ):
            return

        # Darken everything
        dark_surface = pygame.Surface((ACTUAL_WIDTH, FRAME_Y))
        dark_surface.set_alpha(140)
        dark_surface.fill((0, 0, 0))
        screen.blit(dark_surface, (0, 0))

        # In ITEM_INFO: only un-darken the selected ally
        if b.menu_mode in (MENU_MODE_ITEM_ALLY_TARGET,
                           MENU_MODE_TARGET_BUFF,
                           MENU_MODE_BUFF_PLAYER):
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

        # Original behavior for TARGET_SELECT and DAMAGING_ENEMY
        if highlight_player_pos is not None:
            sprite, x, y = highlight_player_pos
            screen.blit(sprite, (x, y))

        if target_enemy_pos is not None:
            sprite, x, y = target_enemy_pos
            screen.blit(sprite, (x, y))


    def draw_affinity_flash(self, b, screen, active_pokemon, \
                            target, anim_frame, target_enemy_pos):
        if b.menu_mode not in (MENU_MODE_TARGET_SELECT, 
                             MENU_MODE_ITEM_TARGET_SELECT):
            return

        selected_index = b.skills_scroll + b.skills_cursor
        if b.menu_mode == MENU_MODE_TARGET_SELECT:
            move_name = active_pokemon.moves[selected_index]
        else:
            move_name = b.pending_item_data["type"].split("damage_")[1]
        move = self.smt_moves[move_name]

        element = move["element"]
        element_index = ELEMENT_INDEX[element]
        affinity_value = target.affinities[element_index]

        if affinity_value == 0:
            return

        if target_enemy_pos is None:
            return

        sprite, x, y = target_enemy_pos

        flash = (math.sin(anim_frame * 0.3) + 1) * 0.5
        alpha = int(120 * flash)

        # Determine flash color based on affinity tiers
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

        tint = pygame.Surface((w, h), pygame.SRCALPHA)
        tint.fill((*flash_color, 255))
        tint.blit(sprite_alpha, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        tint.set_alpha(alpha)

        screen.blit(tint, (x, y))
