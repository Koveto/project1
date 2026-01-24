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

    def draw_enemies(self, screen, menu_mode, target_index, poke_offset, active_enemy_index=None):
        target_enemy_pos = None

        for i in ENEMY_DRAW_ORDER:
            sprite = self.enemy_sprites[i]
            if sprite is None:
                continue

            x = ENEMY_BASE_X + i * ENEMY_SPACING
            y = ENEMY_Y

            # Bounce only during target selection
            if menu_mode in (MENU_MODE_TARGET_SELECT, MENU_MODE_ITEM_TARGET_SELECT):
                if i == target_index:
                    y += poke_offset

            # Draw sprite
            screen.blit(sprite, (x, y))

            # NORMAL CASE: highlight the target enemy
            if menu_mode not in (MENU_MODE_DAMAGING_PLAYER, MENU_MODE_ENEMY_DAMAGE):
                if i == target_index:
                    target_enemy_pos = (sprite, x, y)

            # ENEMY TURN CASE: highlight the attacking enemy
            else:
                if active_enemy_index is not None and i == active_enemy_index:
                    target_enemy_pos = (sprite, x, y)

        return target_enemy_pos


    def draw_players(self, screen, menu_mode, active_index, poke_offset, model):
        active_pokemon_pos = None

        for i, sprite in enumerate(self.player_sprites):
            if sprite is None:
                continue

            pokemon = model.player_team[i]

            x = PLAYER_BASE_X + i * PLAYER_SPACING

            if pokemon.is_player:
                x += PLAYER_OFFSET
                y = PLAYER_Y + PLAYER_Y_OFFSET
            else:
                y = PLAYER_Y + NORMAL_Y_OFFSET

            if i == active_index and menu_mode not in (MENU_MODE_DAMAGING_ENEMY,
                                                       MENU_MODE_DAMAGING_PLAYER,
                                                       MENU_MODE_ENEMY_DAMAGE):
                y += poke_offset

            screen.blit(sprite, (x, y))

            if i == active_index:
                active_pokemon_pos = (sprite, x, y)

        return active_pokemon_pos

    def draw_dark_overlay(self, screen, menu_mode, highlight_player_pos, target_enemy_pos):
        if menu_mode not in (
            MENU_MODE_TARGET_SELECT,
            MENU_MODE_DAMAGING_ENEMY,
            MENU_MODE_ITEM_INFO,
            MENU_MODE_ITEM_TARGET_SELECT,
            MENU_MODE_DAMAGING_PLAYER,
            MENU_MODE_ENEMY_DAMAGE
        ):
            return

        # Darken everything
        dark_surface = pygame.Surface((ACTUAL_WIDTH, FRAME_Y))
        dark_surface.set_alpha(140)
        dark_surface.fill((0, 0, 0))
        screen.blit(dark_surface, (0, 0))

        # In ITEM_INFO: only un-darken the selected ally
        if menu_mode == MENU_MODE_ITEM_INFO:
            if highlight_player_pos is not None:
                sprite, x, y = highlight_player_pos
                screen.blit(sprite, (x, y))
            return

        # Original behavior for TARGET_SELECT and DAMAGING_ENEMY
        if highlight_player_pos is not None:
            sprite, x, y = highlight_player_pos
            screen.blit(sprite, (x, y))

        if target_enemy_pos is not None:
            sprite, x, y = target_enemy_pos
            screen.blit(sprite, (x, y))


    def draw_affinity_flash(self, screen, menu_mode, active_pokemon, 
                            skills_scroll, skills_cursor, 
                            target, anim_frame, target_enemy_pos,
                            pending_item_data):
        if menu_mode not in (MENU_MODE_TARGET_SELECT, 
                             MENU_MODE_ITEM_TARGET_SELECT):
            return

        selected_index = skills_scroll + skills_cursor
        if menu_mode == MENU_MODE_TARGET_SELECT:
            move_name = active_pokemon.moves[selected_index]
        else:
            move_name = pending_item_data["type"].split("damage_")[1]
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
