# state/battle_state.py

import pygame, random
from constants import *
from battle.battle_constants import *
from state.state_manager import GameState
from battle.battle_model import BattleModel
from battle.battle_scene import BattleRenderer
from pokedex.pokemon import Pokemon
from data.smt.smt_stats import load_smt_from_json, get_smt_pokemon_by_number
from data.smt.smt_moves import load_moves
from battle.battle_menu import (
    handle_main_menu_event,
    handle_skills_menu_event,
    handle_target_select_event,
    handle_items_event,
    handle_item_ally_target_event,
    handle_item_target_select_event,
    handle_info_event,
    handle_submenu_event,
    handle_target_buff_event
)
from battle.battle_text import (
    handle_talk_event,
    handle_escape_event,
    handle_guarding_event,
    update_simple_scroll_phase,
    scroll_then_flag
)
from battle.battle_items import (
    handle_item_use_event,
    update_item_use_phase
)
from battle.battle_damage import (
    handle_damaging_enemy_event,
    handle_enemy_damaging_event,
    update_generic_damage_phase,
    handle_enemy_damage_event,
    start_enemy_turn
)


class BattleState(GameState):

    def __init__(self, background_surface):

        # Load SMT Pokémon data
        self.smt_pokemon = load_smt_from_json(FILENAME_STATS)
        self.smt_moves = load_moves(FILENAME_MOVES)

        # Fetch Bulbasaur (no = 1)
        bulbasaur_data = get_smt_pokemon_by_number(self.smt_pokemon, 1)

        # Create the player Pokémon using Bulbasaur's data
        player_pokemon = Pokemon(
            pokedex_number=PLAYER_DEX_NO,          # special player marker
            name="Brendan",             # override name
            level=99,
            stats=bulbasaur_data.base_stats,
            affinities=bulbasaur_data.affinities,
            learnset=bulbasaur_data.learnset,
            moves=["Attack", "Agi", "Bufu", "Zio", "Hama", "Tarukaja"]
        )

        # Build teams
        player_team = [
            player_pokemon,
            get_smt_pokemon_by_number(self.smt_pokemon, 34),   # Nidoking
            get_smt_pokemon_by_number(self.smt_pokemon, 115),  # Kangaskhan
            get_smt_pokemon_by_number(self.smt_pokemon, 6)     # Charizard
        ]

        player_team[1].moves = ["Attack", "Agi", "Bufu", "Zio", "Hama", "Tarukaja"]
        player_team[2].moves = ["Attack", "Agi", "Bufu", "Zio", "Hama", "Tarukaja"]
        player_team[3].moves = ["Attack", "Agi", "Bufu", "Zio", "Hama", "Tarukaja"]

        enemy_team = [
            get_smt_pokemon_by_number(self.smt_pokemon, 9),    # Blastoise
            get_smt_pokemon_by_number(self.smt_pokemon, 3),    # Venusaur
            get_smt_pokemon_by_number(self.smt_pokemon, 150),  # Mewtwo
            get_smt_pokemon_by_number(self.smt_pokemon, 12)    # Butterfree
        ]

        enemy_team[0].moves = ["Attack", "Agi", "Bufu", "Zio", "Hama"]
        enemy_team[1].moves = ["Attack", "Agi", "Bufu", "Zio", "Hama"]
        enemy_team[2].moves = ["Attack", "Agi", "Bufu", "Zio", "Hama"]
        enemy_team[3].moves = ["Attack", "Agi", "Bufu", "Zio", "Hama"]

        self.model = BattleModel(player_team, enemy_team)
        self.renderer = BattleRenderer(self, background_surface)

        self.menu_index = MENU_INDEX_SKILLS
        self.menu_mode = MENU_MODE_MAIN
        self.previous_menu_index = 0
        self.skills_cursor = 0
        self.skills_scroll = 0
        self.target_index = 0
        self.scroll_text = ""
        self.scroll_index = 0
        self.scroll_speed = 2
        self.scroll_delay = SCROLL_SPEED
        self.scroll_timer = 0
        self.scroll_done = False
        self.pending_move_name = None
        self.damage_animating = False
        self.damage_started = False
        self.damage_done = False
        self.affinity_text = None
        self.affinity_done = False
        self.affinity_scroll_index = 0
        self.affinity_scroll_done = False
        self.delay_started = False
        self.delay_frames = 0
        self.item_cursor_x = 0
        self.item_cursor_y = 0
        self.pending_item_name = None
        self.pending_item_data = None
        self.selected_ally = 0
        self.damage_amount = 0
        self.damage_text = None
        self.damage_scroll_index = 0
        self.damage_scroll_done = False
        self.item_use_text = None
        self.item_use_scroll_index = 0
        self.item_use_scroll_done = False
        self.item_heal_animating = False
        self.item_heal_done = False
        self.item_recover_text = None
        self.item_recover_scroll_index = 0
        self.item_recover_scroll_done = False
        self.item_heal_amount = 0
        self.enemy_target_index = 0
        self.enemy_waiting_for_confirm = False
        self.enemy_turn_index = 0
        self.enemy_turn_order = None
        self.active_enemy_index = 0
        self.missed = False
        self.info_row = 1
        self.info_col = 0
        self.is_crit = False
        self.crit_done = False
        self.crit_scroll_index = 0
        self.crit_scroll_done = False
        self.crit_text = None
        self.affinity_confirm = False
        self.item_data = None

    def draw(self, screen):
        self.renderer.draw(self, screen)

    def handle_event(self, event):
        if event.type != pygame.KEYDOWN:
            return

        if self.menu_mode == MENU_MODE_MAIN:
            handle_main_menu_event(self, event)

        elif self.menu_mode == MENU_MODE_SKILLS:
            handle_skills_menu_event(self, event)

        elif self.menu_mode == MENU_MODE_TARGET_SELECT:
            handle_target_select_event(self, event)

        elif self.menu_mode == MENU_MODE_DAMAGING_ENEMY:
            handle_damaging_enemy_event(self, event)

        elif self.menu_mode == MENU_MODE_GUARDING:
            handle_guarding_event(self, event)

        elif self.menu_mode == MENU_MODE_TALK:
            handle_talk_event(self, event)

        elif self.menu_mode == MENU_MODE_ESCAPE:
            handle_escape_event(self, event)

        elif self.menu_mode == MENU_MODE_ITEMS:
            handle_items_event(self, event)

        elif self.menu_mode == MENU_MODE_ITEM_ALLY_TARGET:
            handle_item_ally_target_event(self, event)

        elif self.menu_mode == MENU_MODE_ITEM_USE:
            handle_item_use_event(self, event)

        elif self.menu_mode == MENU_MODE_ITEM_TARGET_SELECT:
            handle_item_target_select_event(self, event)

        elif self.menu_mode == MENU_MODE_DAMAGING_PLAYER:
            handle_enemy_damaging_event(self, event)

        elif self.menu_mode == MENU_MODE_ENEMY_DAMAGE:
            handle_enemy_damage_event(self, event)

        elif self.menu_mode == MENU_MODE_INFO:
            handle_info_event(self, event)

        elif self.menu_mode == MENU_MODE_TARGET_BUFF:
            handle_target_buff_event(self, event)

        elif self.menu_mode == MENU_MODE_SUBMENU:
            handle_submenu_event(self, event)

    def update(self):
        if not self.model.is_player_turn:
            # Enemy turn state machine
            if self.menu_mode == MENU_MODE_DAMAGING_PLAYER:
                return scroll_then_flag(
                    self,
                    text_attr="scroll_text",
                    index_attr="scroll_index",
                    done_attr="scroll_done",
                    flag_attr="enemy_waiting_for_confirm"
                )
            elif self.menu_mode == MENU_MODE_ENEMY_DAMAGE:
                update_generic_damage_phase(self, False)
                return
            else:
                # Enemy turn just started → set up attack announcement
                start_enemy_turn(self)
                start_enemy_turn(self)
                return
        if self.menu_mode == MENU_MODE_DAMAGING_ENEMY:
            update_generic_damage_phase(self, True)
        elif self.menu_mode == MENU_MODE_GUARDING:
            return update_simple_scroll_phase(self)
        elif self.menu_mode == MENU_MODE_ESCAPE:
            return update_simple_scroll_phase(self)
        elif self.menu_mode == MENU_MODE_TALK:
            return update_simple_scroll_phase(self)
        elif self.menu_mode == MENU_MODE_ITEM_USE:
            update_item_use_phase(self)

