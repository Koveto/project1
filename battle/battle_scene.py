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

    def __init__(self, b, background_surface):

        # Core references
        self.background = background_surface

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

        # Press Turn icons
        self.press_turn_red = load_scaled_sprite(sprite_path(FILENAME_PBRED), scale=SCALE_PRESSTURN, colorkey=COLOR_MAGENTA)
        self.press_turn_blue = load_scaled_sprite(sprite_path(FILENAME_PBBLUE), scale=SCALE_PRESSTURN, colorkey=COLOR_MAGENTA)

        # Pokémon sprites
        self.player_sprites = [
            self._load_sprite_for_pokemon(p, is_back=True) if p else None
            for p in b.model.player_team
        ]
        self.enemy_sprites = [
            self._load_sprite_for_pokemon(p, is_back=False) if p else None
            for p in b.model.enemy_team
        ]

        # Sub-renderers
        self.stat_icon_renderer = StatIconRenderer()
        self.text_renderer = TextRenderer(self.font0, self.cursor_sprite)
        self.background_renderer = BackgroundRenderer(background_surface, self.player_sprites, self.enemy_sprites, b.smt_moves)
        self.hpmp_renderer = HPMPRenderer(self.font1, self.font3, self.hpmp_sprite, self.hpmp_sprite_enemy, self.lv_sprite, self.hp_fill, self.mp_fill, self.mp_cost_fill, self.stat_icon_renderer)
        self.menu_renderer = MenuRenderer(self.font0, self.font2, self.cursor_sprite, b.smt_moves)
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
                                 b,
                                 screen,
                                 scroll_index,
                                 blink):
        active_pokemon = b.model.player_team[b.model.turn_index]
        
        if b.menu_mode == MENU_MODE_MAIN:
            self.menu_renderer.draw_main_menu(b, screen, active_pokemon)

        elif b.menu_mode == MENU_MODE_SKILLS:
            self.menu_renderer.draw_skills_menu(b, screen, active_pokemon)

        elif b.menu_mode == MENU_MODE_TARGET_SELECT:
            self.menu_renderer.draw_target_select_menu(
                b,
                screen,
                active_pokemon,
            )

        elif b.menu_mode == MENU_MODE_DAMAGING_ENEMY:
            self.text_renderer.draw_damaging_enemy(
                b, screen, scroll_index, 
                blink
            )
            return
        
        elif b.menu_mode == MENU_MODE_ITEMS:
            self.menu_renderer.draw_item_menu(
                b, screen,
            )
            return
        
        elif b.menu_mode == MENU_MODE_ITEM_ALLY_TARGET:
            self.menu_renderer.draw_item_ally_target(
                b,
                screen,
                self.text_renderer
            )
            return

        elif b.menu_mode == MENU_MODE_ITEM_USE:
            self.text_renderer.draw_item_use(
                b,
                screen,
                blink
            )
            return
        
        elif b.menu_mode == MENU_MODE_ITEM_TARGET_SELECT:
            self.menu_renderer.draw_item_target_select_menu(
                b,
                screen,
                active_pokemon
            )
        
        elif b.menu_mode == MENU_MODE_GUARDING:
            self.text_renderer.draw_simple_scroll(
                b,
                screen,
                scroll_index,
                blink
            )
            return
        
        elif b.menu_mode == MENU_MODE_TALK:
            self.text_renderer.draw_simple_scroll(
                b, screen, scroll_index, blink
            )
            return

        elif b.menu_mode == MENU_MODE_ESCAPE:
            self.text_renderer.draw_simple_scroll(
                b, screen, scroll_index, blink
            )
            return
        
        elif b.menu_mode == MENU_MODE_DAMAGING_PLAYER:
            self.text_renderer.draw_simple_scroll(
                b,
                screen,
                scroll_index,
                blink
            )
            return
        
        elif b.menu_mode == MENU_MODE_ENEMY_DAMAGE:
            self.text_renderer.draw_damaging_enemy(
                b,
                screen,
                scroll_index,
                blink
            )
            return

        elif b.menu_mode == MENU_MODE_INFO:
            self.font0.draw_text(screen, "Press X to return", X_MENU_MAIN, Y_MENU_MAIN_0)

        elif b.menu_mode == MENU_MODE_TARGET_BUFF:
            self.menu_renderer.draw_target_buff_menu(b, screen, active_pokemon)
        
        elif b.menu_mode == MENU_MODE_BUFF_PLAYER:
            self.text_renderer.draw_simple_scroll(
                b,
                screen,
                scroll_index,
                blink
            )

        else:
            self.menu_renderer.draw_dummy_menu(b, screen)

    def _draw_press_turn_icons(self,
                               b,
                               screen,
                               hp_offset):
        press_turn_states = b.model.get_press_turn_icon_states(self.animation.anim_frame)
        self.press_turn_renderer.draw_all(b, screen, press_turn_states, hp_offset, self.animation.anim_frame)

    def _is_drawn_press_turn_icons(self, b):
        return b.menu_mode != MENU_MODE_INFO
    
    def _draw_enemy_hpmp(self,
                         b,
                         screen,
                         enemy_hpmp_y,
                         ui_hp_offset,
                         blink):
        if b.menu_mode in (MENU_MODE_TARGET_SELECT,
                        MENU_MODE_DAMAGING_ENEMY,
                        MENU_MODE_ITEM_TARGET_SELECT):
            enemy_for_hpmp = b.model.enemy_team[b.target_index]
        elif b.menu_mode == MENU_MODE_INFO and b.info_row == 0:
            enemy_for_hpmp = b.model.enemy_team[b.info_col]
        else:
            enemy_for_hpmp = b.model.enemy_team[b.active_enemy_index]
        if (b.menu_mode != MENU_MODE_INFO) or \
            (b.info_row == 0):
            self.hpmp_renderer.draw_enemy_hpmp(screen, enemy_for_hpmp, enemy_hpmp_y, ui_hp_offset, blink)

    def _is_drawn_enemy_hpmp(self, b):
        return b.menu_mode in (
            MENU_MODE_TARGET_SELECT,
            MENU_MODE_DAMAGING_ENEMY,
            MENU_MODE_ITEM_TARGET_SELECT,
            MENU_MODE_DAMAGING_PLAYER,
            MENU_MODE_ENEMY_DAMAGE,
            MENU_MODE_INFO
        )
    
    def _draw_mpcost(self, b, screen, ui_hp_offset):
        move_name = b.model.get_active_pokemon().moves[b.skills_scroll + b.skills_cursor]
        self.hpmp_renderer.draw_mp_cost_bar(
            b,
            screen,
            move_name,
            ui_hp_offset
        )

    def _is_drawn_mpcost(self, b):
        return b.menu_mode in (MENU_MODE_SKILLS, MENU_MODE_TARGET_SELECT)
    
    def _is_drawn_player_hpmp(self, b):
        return (b.menu_mode != MENU_MODE_INFO) or (b.info_row == ROW_PLAYER)
            
    def _draw_player_hpmp(self,
                              screen,
                              pokemon_for_hpmp,
                              hpmp_y,
                              ui_hp_offset,
                              blink):
        self.hpmp_renderer.draw_player_hpmp(screen, pokemon_for_hpmp, hpmp_y, ui_hp_offset, blink)

    def _get_data_hpmp(self, 
                       b,
                       hp_offset):
        active_pokemon = b.model.player_team[b.model.turn_index]
        hpmp_y = HPMP_Y
        enemy_hpmp_y = HPMP_ENEMY_Y
        ui_hp_offset = 0
        pokemon_for_hpmp = None
        if b.menu_mode not in (MENU_MODE_DAMAGING_ENEMY,
                             MENU_MODE_DAMAGING_PLAYER,
                             MENU_MODE_ENEMY_DAMAGE):
            hpmp_y += hp_offset
            enemy_hpmp_y += hp_offset
            ui_hp_offset += hp_offset
        pokemon_for_hpmp = active_pokemon
        if b.menu_mode in (MENU_MODE_ITEM_ALLY_TARGET,
                         MENU_MODE_ITEM_USE):
            pokemon_for_hpmp = b.model.player_team[b.selected_ally]
        if b.menu_mode in (MENU_MODE_DAMAGING_PLAYER,
                         MENU_MODE_ENEMY_DAMAGE):
            pokemon_for_hpmp = b.model.player_team[b.enemy_target_index]
        if b.menu_mode == MENU_MODE_INFO and b.info_row == 1:
            pokemon_for_hpmp = b.model.player_team[b.info_col]
        return (hpmp_y, enemy_hpmp_y, ui_hp_offset, pokemon_for_hpmp)
    
    def _get_data_dark_overlay(self, 
              b,
              poke_offset,
              target_enemy_pos,
              highlight_player_pos):
        highlight_player_pos = highlight_player_pos
        target_enemy_pos = target_enemy_pos
        if b.menu_mode == MENU_MODE_ITEM_ALLY_TARGET:
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
        if b.menu_mode in (MENU_MODE_DAMAGING_PLAYER,
                         MENU_MODE_ENEMY_DAMAGE):
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
        return (highlight_player_pos, target_enemy_pos)
    
    def _get_data_bounce_index(self,
                               b):
        bounce_index = b.model.turn_index
        if b.menu_mode in (MENU_MODE_ITEM_ALLY_TARGET, MENU_MODE_TARGET_BUFF):
            bounce_index = b.selected_ally
        elif b.menu_mode == MENU_MODE_DAMAGING_PLAYER:
            bounce_index = b.enemy_target_index
        elif b.menu_mode == MENU_MODE_INFO:
            if b.info_row == ROW_PLAYER:
                bounce_index = b.info_col
            else:
                bounce_index = ROW_NOT_INFO_STATE
        return bounce_index


    # ---------------------------------------------------------
    # Main draw function
    # ---------------------------------------------------------
    def draw(self, b, screen):

        scroll_index = int(b.scroll_index)

        self.animation.update()
        blink = self.animation.get_blink()
        poke_offset, hp_offset = self.animation.get_bounce_offsets()

        self.background_renderer.draw_background(screen)
        
        target_enemy_pos = self.background_renderer.draw_enemies(b,
                                                                 screen, 
                                                                 poke_offset)
        
        bounce_index = self._get_data_bounce_index(b)
        
        highlight_player_pos = self.background_renderer.draw_players(
            b, screen, bounce_index, poke_offset
        )

        highlight_player_pos, \
        target_enemy_pos = self._get_data_dark_overlay(
                                      b,
                                      poke_offset,
                                      target_enemy_pos,
                                      highlight_player_pos)

        self.background_renderer.draw_dark_overlay(
            b,
            screen,
            highlight_player_pos,
            target_enemy_pos
        )

        self.background_renderer.draw_affinity_flash(b,
                                                     screen,
                                                     b.model.player_team[b.model.turn_index],
                                                     b.model.enemy_team[b.target_index],
                                                     self.animation.anim_frame, 
                                                     target_enemy_pos)

        hpmp_y, \
        enemy_hpmp_y, \
        ui_hp_offset, \
        pokemon_for_hpmp = self._get_data_hpmp(
                       b, 
                       hp_offset)        

        if self._is_drawn_player_hpmp(b):
            self._draw_player_hpmp(screen,
                                   pokemon_for_hpmp,
                                   hpmp_y,
                                   ui_hp_offset,
                                   blink)        

        if self._is_drawn_mpcost(b):
            self._draw_mpcost(b, screen, ui_hp_offset)

        if self._is_drawn_enemy_hpmp(b):
            self._draw_enemy_hpmp(b,
                                  screen,
                                  enemy_hpmp_y,
                                  ui_hp_offset,
                                  blink)

        screen.blit(self.bframe, COORDS_FRAME)

        # Press Turn icons
        if self._is_drawn_press_turn_icons(b):
            self._draw_press_turn_icons(b,
                                        screen,
                                        hp_offset)

        # Menus + text
        self._call_menu_mode_function(
                                 b,
                                 screen,
                                 scroll_index,
                                 blink)
        
