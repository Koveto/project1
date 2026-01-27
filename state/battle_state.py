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
    handle_item_info_event,
    handle_item_target_select_event,
    handle_info_event,
    handle_submenu_event,
)
from battle.battle_text import (
    start_text_mode,
    handle_talk_event,
    handle_escape_event,
    handle_guarding_event,
    update_simple_scroll_phase,
    scroll_text_generic,
    handle_scroll_skip
)
from battle.battle_items import (
    handle_item_use_event,
    update_item_use_phase,
    apply_item_healing,
    compute_heal_amount,
    setup_heal_animation,
    apply_heal_to_ally
)
from battle.battle_damage import (
    calculate_raw_damage,
    calculate_press_turns_consumed,
    determine_damage_recipient,
    handle_accuracy,
    compute_affinity_after_damage,
    reset_damage_flags,
    tick_hp_animation,
    animate_hp_bar,
    setup_damage_text,
    compute_affinity_text,
    handle_damaging_enemy_event,
    handle_enemy_damaging_event,
    finish_damage_phase,
    finish_enemy_damage_phase,
    update_generic_damage_phase,
    handle_damage_delay,
    begin_damage_if_ready
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
            moves=["Attack", "Agi", "Bufu", "Zio"]
        )

        # Build teams
        player_team = [
            player_pokemon,
            get_smt_pokemon_by_number(self.smt_pokemon, 34),   # Nidoking
            get_smt_pokemon_by_number(self.smt_pokemon, 115),  # Kangaskhan
            get_smt_pokemon_by_number(self.smt_pokemon, 6)     # Charizard
        ]

        player_team[1].moves = ["Attack", "Agi", "Bufu", "Zio"]
        player_team[2].moves = ["Attack", "Agi", "Bufu", "Zio"]
        player_team[3].moves = ["Attack", "Agi", "Bufu", "Zio"]

        enemy_team = [
            get_smt_pokemon_by_number(self.smt_pokemon, 9),    # Blastoise
            get_smt_pokemon_by_number(self.smt_pokemon, 3),    # Venusaur
            get_smt_pokemon_by_number(self.smt_pokemon, 150),  # Mewtwo
            get_smt_pokemon_by_number(self.smt_pokemon, 12)    # Butterfree
        ]

        enemy_team[0].moves = ["Attack", "Agi", "Bufu", "Zio"]
        enemy_team[1].moves = ["Attack", "Agi", "Bufu", "Zio"]
        enemy_team[2].moves = ["Attack", "Agi", "Bufu", "Zio"]
        enemy_team[3].moves = ["Attack", "Agi", "Bufu", "Zio"]

        self.model = BattleModel(player_team, enemy_team)
        self.renderer = BattleRenderer(background_surface, self.model, self.smt_moves)

        self.menu_index = 0
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

    def draw(self, screen):
        self.renderer.draw(screen, self.menu_index, 
                           self.menu_mode, self.previous_menu_index,
                           self.skills_cursor, self.skills_scroll,
                           self.target_index, self.scroll_text,
                           int(self.scroll_index), self.scroll_done,
                           self.damage_done, self.affinity_done,
                           self.affinity_text, self.affinity_scroll_index,
                           self.affinity_scroll_done,
                           self.model.inventory,
                           self.item_cursor_x, self.item_cursor_y,
                           self.pending_item_data, self.selected_ally,
                           self.damage_text, self.damage_scroll_index, self.damage_scroll_done,
                           self.item_use_text, self.item_use_scroll_index,
                           self.item_use_scroll_done,
                           self.item_recover_text,
                           self.item_recover_scroll_index,
                           self.item_recover_scroll_done,
                           self.enemy_target_index,
                           self.active_enemy_index,
                           self.info_row, self.info_col)

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

        elif self.menu_mode == MENU_MODE_ITEM_INFO:
            handle_item_info_event(self, event)

        elif self.menu_mode == MENU_MODE_ITEM_USE:
            handle_item_use_event(self, event)

        elif self.menu_mode == MENU_MODE_ITEM_TARGET_SELECT:
            handle_item_target_select_event(self, event)

        elif self.menu_mode == MENU_MODE_DAMAGING_PLAYER:
            handle_enemy_damaging_event(self, event)

        elif self.menu_mode == MENU_MODE_ENEMY_DAMAGE:
            self._handle_enemy_damage_event(event)

        elif self.menu_mode == MENU_MODE_INFO:
            handle_info_event(self, event)

        elif self.menu_mode == MENU_MODE_SUBMENU:
            handle_submenu_event(self, event)

    def update(self):
        if not self.model.is_player_turn:
            # Enemy turn state machine
            if self.menu_mode == MENU_MODE_DAMAGING_PLAYER:
                return self._scroll_then_flag(
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
                self._start_enemy_turn()
                self._start_enemy_turn()
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


    
    
    

    

    def _move_main_menu_cursor(self, dx, dy):
        row = self.menu_index // 4
        col = self.menu_index % 4

        new_row = (row + dy) % 2
        new_col = (col + dx) % 4

        self.menu_index = new_row * 4 + new_col

    def _start_item_use_phase(self, user_name, item_name):
        # Text scroll for "X uses Y!"
        self.item_use_text = f"{user_name} uses {item_name}!"
        self.item_use_scroll_index = 0
        self.item_use_scroll_done = False

        # Heal animation state
        self.item_heal_animating = False
        self.item_heal_done = False

        # Recovery text (e.g., "Recovered 20 HP!")
        self.item_recover_text = None
        self.item_recover_scroll_index = 0
        self.item_recover_scroll_done = False

        # Switch mode
        self.menu_mode = MENU_MODE_ITEM_USE

    def _move_item_cursor(self, dx, dy):
        item_names = list(self.model.inventory.keys())
        item_count = len(item_names)

        new_x = self.item_cursor_x + dx
        new_y = self.item_cursor_y + dy

        # Clamp to grid bounds (3 columns, 3 rows)
        new_x = max(0, min(2, new_x))
        new_y = max(0, min(2, new_y))

        # Convert to linear index
        new_index = new_y * 3 + new_x

        # Only move if the slot exists
        if new_index < item_count:
            self.item_cursor_x = new_x
            self.item_cursor_y = new_y

    def _select_item(self, item_name, item_data, next_mode):
        self.pending_item_name = item_name
        self.pending_item_data = item_data
        self.menu_mode = next_mode

    def _handle_simple_scroll_event(self, event, confirm_keys, on_finish):
        # Only respond to KEYDOWN
        if event.type != pygame.KEYDOWN:
            return

        # If scroll is still happening
        if not self.scroll_done:
            if event.key in confirm_keys:
                self.scroll_index = len(self.scroll_text)
                self.scroll_done = True
            return

        # Scroll is done — wait for confirm to finish the phase
        if event.key in confirm_keys:
            on_finish()

    def _move_skill_cursor(self, direction):
        """
        direction = +1 for DOWN, -1 for UP
        """
        moves = self.model.get_active_pokemon().moves
        total = len(moves)

        # Moving down
        if direction == 1:
            # Case 1: Move cursor down within visible window
            if self.skills_cursor < 2 and self.skills_cursor < total - 1:
                self.skills_cursor += 1
                return

            # Case 2: Scroll down if more moves exist below
            if self.skills_scroll + 3 < total:
                self.skills_scroll += 1
                return

            # Case 3: Fallback — move cursor if possible
            if self.skills_cursor < 2:
                self.skills_cursor += 1
                return

        # Moving up
        if direction == -1:
            # Case 1: Move cursor up within visible window
            if self.skills_cursor > 0:
                self.skills_cursor -= 1
                return

            # Case 2: Scroll up if possible
            if self.skills_scroll > 0:
                self.skills_scroll -= 1
                return

            # Case 3: Fallback — move cursor if possible
            if self.skills_cursor > 0:
                self.skills_cursor -= 1
                return
            
    def _can_select_skill(self, move, pokemon):
        return (
            move["target"] == "Single" and
            move["type"] in ("Physical", "Special") and
            pokemon.remaining_mp >= move["mp"]
        )

    def _start_player_attack_phase(self):
        # Switch mode
        self.menu_mode = MENU_MODE_DAMAGING_ENEMY

        # Determine move + target
        selected_index = self.skills_scroll + self.skills_cursor
        active = self.model.get_active_pokemon()
        move_name = active.moves[selected_index]
        enemy = self.model.enemy_team[self.target_index]

        # Store pending move
        self.pending_move_name = move_name

        # MP consumption
        move = self.smt_moves[move_name]
        cost = move["mp"]
        active.remaining_mp = max(0, active.remaining_mp - cost)

        # Build announcement text
        if move_name == "Attack":
            self.scroll_text = f"{active.name} attacks {enemy.name}!"
        else:
            self.scroll_text = f"{active.name} uses {move_name} on {enemy.name}!"

        # Reset scroll state
        self.scroll_index = 0
        self.scroll_done = False

        # Reset damage state
        self.damage_started = False
        self.damage_done = False

        # Reset affinity state
        self.affinity_text = None
        self.affinity_done = False
        self.affinity_scroll_index = 0
        self.affinity_scroll_done = False

    def _start_item_attack_phase(self):
        # Consume the item
        self.model.consume_item(self.pending_item_name)

        # Switch to damage phase
        self.menu_mode = MENU_MODE_DAMAGING_ENEMY

        # Determine move + target
        active = self.model.get_active_pokemon()
        enemy = self.model.enemy_team[self.target_index]

        # Item type looks like "damage_fire", "damage_ice", etc.
        move_name = self.pending_item_data["type"].split("damage_")[1]
        self.pending_move_name = move_name

        # Announcement text
        self.scroll_text = f"{active.name} uses {self.pending_item_name}!"
        self.scroll_index = 0
        self.scroll_done = False

        # Reset damage state
        self.damage_started = False
        self.damage_done = False

        # Reset affinity state
        self.affinity_text = None
        self.affinity_done = False
        self.affinity_scroll_index = 0
        self.affinity_scroll_done = False


    def _get_current_enemy_attacker(self):
        return self.enemy_turn_order[self.enemy_turn_index]

    


    

        
    
    
        
    def _handle_enemy_damage_event(self, event):
        if event.type == pygame.KEYDOWN and key_confirm(event.key):
            if self.damage_scroll_done:
                finish_enemy_damage_phase(self)



    
    def _apply_press_turn_cost(self, affinity):
        if not self.missed:
            cost = calculate_press_turns_consumed(self, affinity)
            self.model.handle_action_press_turn_cost(cost)
        else:
            self.missed = False  # reset for next action

    def _handle_side_switch(self):
        if not self.model.has_press_turns_left():
            self.model.next_side()


    def _finish_guard_phase(self):
        self.model.handle_action_press_turn_cost(PRESS_TURN_FULL)
        self.model.next_turn()
        self.menu_mode = MENU_MODE_MAIN
        self.menu_index = MENU_INDEX_GUARD
        self.scroll_text = ""
        self.scroll_index = 0
        self.scroll_done = True


    


      
        
    
    
    


    
    
    
    def _begin_enemy_action(self, attacker_index, move_name, target_index):
        attacker = self.model.enemy_team[attacker_index]

        # Sync active index
        self.active_enemy_index = attacker_index

        # Store pending move + target
        self.pending_enemy_move = move_name
        self.enemy_target_index = target_index

        # Subtract MP
        move = self.smt_moves[move_name]
        cost = move["mp"]
        attacker.remaining_mp = max(0, attacker.remaining_mp - cost)

        # Build announcement text
        target = self.model.player_team[target_index]
        if move_name == "Attack":
            self.scroll_text = f"{attacker.name} attacks {target.name}!"
        else:
            self.scroll_text = f"{attacker.name} uses {move_name} on {target.name}!"

        # Reset scroll state
        self.scroll_index = 0
        self.scroll_done = False

        # Reset damage flags
        self.damage_started = False
        self.damage_done = False
        self.affinity_text = None
        self.affinity_done = False
        self.affinity_scroll_index = 0
        self.affinity_scroll_done = False

        # Enter announcement phase
        self.menu_mode = MENU_MODE_DAMAGING_PLAYER
        self.enemy_waiting_for_confirm = False

    
    def _start_enemy_attack(self):
        attacker_index = self._get_current_enemy_attacker()
        attacker = self.model.enemy_team[attacker_index]

        move_name = attacker.choose_random_move()
        target_index = self.model.choose_random_player_target()

        return self._begin_enemy_action(attacker_index, move_name, target_index)
    
    def _start_enemy_turn(self):
        # Enter announcement mode immediately
        self.menu_mode = MENU_MODE_DAMAGING_PLAYER

        # Build SPD‑sorted order
        self.enemy_turn_order = sorted(
            range(len(self.model.enemy_team)),
            key=lambda i: self.model.enemy_team[i].speed,
            reverse=True
        )
        self.enemy_turn_index = 0

        attacker_index = self.enemy_turn_order[self.enemy_turn_index]
        attacker = self.model.enemy_team[attacker_index]

        move_name = random.choice(attacker.moves)
        target_index = random.randrange(len(self.model.player_team))

        return self._begin_enemy_action(attacker_index, move_name, target_index)
        
    

    
    
    def _select_combatants(self, is_player):
        if is_player:
            attacker = self.model.get_active_pokemon()
            defender = self.model.enemy_team[self.target_index]
            move = self.smt_moves[self.pending_move_name]
        else:
            attacker = self.model.enemy_team[self.active_enemy_index]
            defender = self.model.player_team[self.enemy_target_index]
            move = self.smt_moves[self.pending_enemy_move]

        return attacker, defender, move
    
    
    
    def _compute_and_apply_damage(self, attacker, defender, move, is_player):
        # Affinity
        element = move["element"]
        element_index = ELEMENT_INDEX[element]
        affinity = defender.affinities[element_index]

        # Crit (still no side effects)
        if move["type"] == "Physical":
            if random.random() < CRIT_CHANCE:
                print("CRITICAL HIT!")

        # Guarding override (enemy → player only)
        if not is_player and defender.is_guarding and affinity < AFFINITY_NEUTRAL:
            affinity = AFFINITY_NEUTRAL

        # Damage calculation
        self.damage_amount = calculate_raw_damage(self, move, affinity)

        # Reflect / redirect
        damage_target = determine_damage_recipient(self, attacker, defender, affinity)

        # HP animation setup
        damage_target.hp_target = max(0, damage_target.remaining_hp - self.damage_amount)
        damage_target.hp_anim = damage_target.remaining_hp

        damage_pixels = int((self.damage_amount / damage_target.max_hp) * HP_BAR_WIDTH)
        damage_target.hp_anim_speed = max(1, min(12, damage_pixels // 4))

        damage_target.remaining_hp = damage_target.hp_target

        self.damage_target = damage_target
        self.damage_started = True
        self.damage_animating = True
        
    
    
    

    
    
    
    
    
    
    def _scroll_then_flag(self, text_attr, index_attr, done_attr, flag_attr):
        if not getattr(self, done_attr):
            return scroll_text_generic(
                self,
                text=getattr(self, text_attr),
                index_attr=index_attr,
                done_attr=done_attr
            )

        if not getattr(self, flag_attr):
            setattr(self, flag_attr, True)

        return

    
    



    
        
    

        
    
