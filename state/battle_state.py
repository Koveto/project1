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
            moves=["Lunge", "Agi", "Bufu", "Zio"]
        )

        # Build teams
        player_team = [
            player_pokemon,
            get_smt_pokemon_by_number(self.smt_pokemon, 34),   # Nidoking
            get_smt_pokemon_by_number(self.smt_pokemon, 115),  # Kangaskhan
            get_smt_pokemon_by_number(self.smt_pokemon, 6)     # Charizard
        ]

        player_team[1].moves = ["Lunge", "Agi", "Bufu", "Zio"]
        player_team[2].moves = ["Lunge", "Agi", "Bufu", "Zio"]
        player_team[3].moves = ["Lunge", "Agi", "Bufu", "Zio"]

        enemy_team = [
            get_smt_pokemon_by_number(self.smt_pokemon, 9),    # Blastoise
            get_smt_pokemon_by_number(self.smt_pokemon, 3),    # Venusaur
            get_smt_pokemon_by_number(self.smt_pokemon, 150),  # Mewtwo
            get_smt_pokemon_by_number(self.smt_pokemon, 12)    # Butterfree
        ]

        enemy_team[0].moves = ["Lunge", "Agi", "Bufu", "Zio"]
        enemy_team[1].moves = ["Lunge", "Agi", "Bufu", "Zio"]
        enemy_team[2].moves = ["Lunge", "Agi", "Bufu", "Zio"]
        enemy_team[3].moves = ["Lunge", "Agi", "Bufu", "Zio"]

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

    def handle_main_menu_event(self, event):
        if event.key == pygame.K_RIGHT:
            if 0 <= self.menu_index <= 2:
                self.menu_index += 1
            elif self.menu_index == 3:
                self.menu_index = 0
            elif 4 <= self.menu_index <= 6:
                self.menu_index += 1
            elif self.menu_index == 7:
                self.menu_index = 4

        elif event.key == pygame.K_LEFT:
            if 1 <= self.menu_index <= 3:
                self.menu_index -= 1
            elif self.menu_index == 0:
                self.menu_index = 3
            elif 5 <= self.menu_index <= 7:
                self.menu_index -= 1
            elif self.menu_index == 4:
                self.menu_index = 7

        elif event.key == pygame.K_DOWN:
            if 0 <= self.menu_index <= 3:
                self.menu_index += 4
            elif 4 <= self.menu_index <= 7:
                self.menu_index -= 4

        elif event.key == pygame.K_UP:
            if 4 <= self.menu_index <= 7:
                self.menu_index -= 4
            elif 0 <= self.menu_index <= 3:
                self.menu_index += 4

        elif key_confirm(event.key):
            # SKILLS
            if self.menu_mode == MENU_MODE_MAIN and self.menu_index == MENU_INDEX_SKILLS:
                self.menu_mode = MENU_MODE_SKILLS
                self.previous_menu_index = self.menu_index
                self.menu_index = 0
                return
            
            # ITEM
            if self.menu_mode == MENU_MODE_MAIN and self.menu_index == MENU_INDEX_ITEMS:
                self.menu_mode = MENU_MODE_ITEMS
                self.item_cursor_x = 0
                self.item_cursor_y = 0
                return
            
            # GUARD
            if self.menu_mode == MENU_MODE_MAIN and self.menu_index == MENU_INDEX_GUARD:
                active = self.model.get_active_player_pokemon()
                active.is_guarding = True
                self.scroll_text = f"{active.name} guards!"
                self.scroll_index = 0
                self.scroll_done = False
                self.menu_mode = MENU_MODE_GUARDING
                return

            # PASS
            if self.menu_mode == MENU_MODE_MAIN and self.menu_index == MENU_INDEX_PASS:
                self.model.handle_action_press_turn_cost(PRESS_TURN_HALF)
                self.model.next_turn()
                self.menu_mode = MENU_MODE_MAIN
                self.menu_index = MENU_INDEX_PASS
                return
            
            # TALK
            if self.menu_mode == MENU_MODE_MAIN and self.menu_index == MENU_INDEX_TALK:
                self.scroll_text = TALK_TEXT
                self.scroll_index = 0
                self.scroll_done = False
                self.menu_mode = MENU_MODE_TALK
                return

            # ESCAPE
            if self.menu_mode == MENU_MODE_MAIN and self.menu_index == MENU_INDEX_ESCAPE:
                self.scroll_text = ESCAPE_TEXT
                self.scroll_index = 0
                self.scroll_done = False
                self.menu_mode = MENU_MODE_ESCAPE
                return


            self.previous_menu_index = self.menu_index
            self.menu_mode = MENU_MODE_SUBMENU

    def handle_item_info_event(self, event):
        if event.type != pygame.KEYDOWN:
            return

        # BACK
        if key_back(event.key):
            self.menu_mode = MENU_MODE_ITEMS
            return

        # LEFT
        if event.key == pygame.K_LEFT:
            ally_count = len(self.model.player_team)
            self.selected_ally = (self.selected_ally - 1) % ally_count
            return

        # RIGHT
        if event.key == pygame.K_RIGHT:
            ally_count = len(self.model.player_team)
            self.selected_ally = (self.selected_ally + 1) % ally_count
            return
        
        # CONFIRM
        if key_confirm(event.key):
            # Build the scroll text
            user = self.model.get_active_pokemon()
            item_name = self.pending_item_name

            self.item_use_text = f"{user.name} uses {item_name}!"
            self.item_use_scroll_index = 0
            self.item_use_scroll_done = False

            self.item_heal_animating = False
            self.item_heal_done = False

            self.item_recover_text = None
            self.item_recover_scroll_index = 0
            self.item_recover_scroll_done = False

            self.menu_mode = MENU_MODE_ITEM_USE
            return


    def handle_items_event(self, event):
        
        item_names = list(self.model.inventory.keys())
        item_count = len(item_names)

        # LEFT
        if event.key == pygame.K_LEFT:
            new_x = max(0, self.item_cursor_x - 1)
            new_index = self.item_cursor_y * 3 + new_x
            if new_index < item_count:
                self.item_cursor_x = new_x

        # RIGHT
        elif event.key == pygame.K_RIGHT:
            new_x = min(2, self.item_cursor_x + 1)
            new_index = self.item_cursor_y * 3 + new_x
            if new_index < item_count:
                self.item_cursor_x = new_x

        # UP
        elif event.key == pygame.K_UP:
            new_y = max(0, self.item_cursor_y - 1)
            new_index = new_y * 3 + self.item_cursor_x
            if new_index < item_count:
                self.item_cursor_y = new_y

        # DOWN
        elif event.key == pygame.K_DOWN:
            new_y = min(2, self.item_cursor_y + 1)
            new_index = new_y * 3 + self.item_cursor_x
            if new_index < item_count:
                self.item_cursor_y = new_y

        # BACK
        elif key_back(event.key):
            self.menu_mode = MENU_MODE_MAIN
            self.menu_index = MENU_INDEX_ITEMS
            return
        
        # CONFIRM
        elif key_confirm(event.key):
            index = self.item_cursor_y * 3 + self.item_cursor_x
            if index < item_count:
                item_name = item_names[index]
                item_data = self.model.smt_items[item_name]
                if item_data["type"].startswith("heal_single"):
                    self.pending_item_name = item_name
                    self.pending_item_data = item_data
                    self.menu_mode = MENU_MODE_ITEM_INFO
                    return
                if item_data["type"].startswith("damage"):
                    self.pending_item_name = item_name
                    self.pending_item_data = item_data
                    self.menu_mode = MENU_MODE_ITEM_TARGET_SELECT
                    return



    def handle_talk_event(self, event):
        if event.type != pygame.KEYDOWN:
            return

        if not self.scroll_done:
            if event.key in (pygame.K_z, pygame.K_RETURN, pygame.K_x):
                self.scroll_index = len(self.scroll_text)
                self.scroll_done = True
            return

        if event.key in (pygame.K_z, pygame.K_RETURN, pygame.K_x):
            self.menu_mode = MENU_MODE_MAIN
            self.menu_index = MENU_INDEX_TALK
            self.scroll_text = ""
            self.scroll_index = 0
            self.scroll_done = True

    def handle_escape_event(self, event):
        if event.type != pygame.KEYDOWN:
            return

        if not self.scroll_done:
            if event.key in (pygame.K_z, pygame.K_RETURN, pygame.K_x):
                self.scroll_index = len(self.scroll_text)
                self.scroll_done = True
            return

        if event.key in (pygame.K_z, pygame.K_RETURN, pygame.K_x):
            self.menu_mode = MENU_MODE_MAIN
            self.menu_index = MENU_INDEX_ESCAPE
            self.scroll_text = ""
            self.scroll_index = 0
            self.scroll_done = True

    def handle_guarding_event(self, event):
        if event.type != pygame.KEYDOWN:
            return
        if not self.scroll_done:
            if key_confirm(event.key):
                self.scroll_index = len(self.scroll_text)
                self.scroll_done = True
            return
        if key_confirm(event.key):
            self.finish_guard_phase()

    def handle_skills_menu_event(self, event):
        if event.key == pygame.K_DOWN:
            total = len(self.model.get_active_pokemon().moves)
            if self.skills_cursor < 2 and self.skills_cursor < total - 1:
                self.skills_cursor += 1
            elif self.skills_scroll + 3 < total:
                self.skills_scroll += 1
            elif self.skills_cursor < 2:
                self.skills_cursor += 1

        elif event.key == pygame.K_UP:
            total = len(self.model.get_active_pokemon().moves)
            if self.skills_cursor > 0:
                self.skills_cursor -= 1
            elif self.skills_scroll > 0:
                self.skills_scroll -= 1
            elif self.skills_cursor > 0:
                self.skills_cursor -= 1

        elif key_confirm(event.key):
            pokemon = self.model.get_active_pokemon()
            selected_index = self.skills_scroll + self.skills_cursor
            move_name = pokemon.moves[selected_index]
            move = self.smt_moves.get(move_name)

            if (
                move["target"] == "Single" and
                move["type"] in ("Physical", "Special") and
                pokemon.remaining_mp >= move["mp"]
            ):
                self.menu_mode = MENU_MODE_TARGET_SELECT
                return

        elif key_back(event.key):
            self.menu_mode = MENU_MODE_MAIN


    def handle_target_select_event(self, event):
        enemy_count = len(self.model.enemy_team)

        if event.key == pygame.K_LEFT:
            if enemy_count > 0:
                self.target_index = (self.target_index - 1) % enemy_count

        elif event.key == pygame.K_RIGHT:
            if enemy_count > 0:
                self.target_index = (self.target_index + 1) % enemy_count

        elif key_confirm(event.key):
            self.menu_mode = MENU_MODE_DAMAGING_ENEMY

            selected_index = self.skills_scroll + self.skills_cursor
            active_pokemon = self.model.get_active_pokemon()
            move_name = active_pokemon.moves[selected_index]
            enemy = self.model.enemy_team[self.target_index]

            self.pending_move_name = move_name

            self.scroll_text = f"{active_pokemon.name} uses {move_name} on {enemy.name}!"
            self.scroll_index = 0
            self.scroll_done = False

            self.damage_started = False
            self.damage_done = False

            self.affinity_text = None
            self.affinity_done = False
            self.affinity_scroll_index = 0
            self.affinity_scroll_done = False
            return

        elif key_back(event.key):
            self.menu_mode = MENU_MODE_SKILLS
            return
        
    def handle_item_target_select_event(self, event):
        enemy_count = len(self.model.enemy_team)

        if event.key == pygame.K_LEFT:
            if enemy_count > 0:
                self.target_index = (self.target_index - 1) % enemy_count

        elif event.key == pygame.K_RIGHT:
            if enemy_count > 0:
                self.target_index = (self.target_index + 1) % enemy_count

        elif key_confirm(event.key):
            self.model.consume_item(self.pending_item_name)
            
            self.menu_mode = MENU_MODE_DAMAGING_ENEMY

            active_pokemon = self.model.get_active_pokemon()
            move_name = self.pending_item_data["type"].split("damage_")[1]
            enemy = self.model.enemy_team[self.target_index]

            self.pending_move_name = move_name

            self.scroll_text = f"{active_pokemon.name} uses {self.pending_item_name}!"
            self.scroll_index = 0
            self.scroll_done = False

            self.damage_started = False
            self.damage_done = False

            self.affinity_text = None
            self.affinity_done = False
            self.affinity_scroll_index = 0
            self.affinity_scroll_done = False
            return

        elif key_back(event.key):
            self.menu_mode = MENU_MODE_ITEMS
            return


    def handle_damaging_enemy_event(self, event):
        # 1) If text is still scrolling, allow skip
        if not self.scroll_done:
            if key_confirm(event.key):
                self.scroll_index = len(self.scroll_text)
                self.scroll_done = True
            return

        # 2) If damage is still animating, ignore input
        if not self.damage_done:
            return

        # 3) Affinity text phase
        if self.affinity_text and not self.affinity_done:
            if not self.affinity_scroll_done:
                if key_confirm(event.key):
                    self.affinity_scroll_index = len(self.affinity_text)
                    self.affinity_scroll_done = True
                return

            if key_confirm(event.key):
                self.finish_damage_phase()
            return

        # 4) Everything done → now Z advances the turn
        if key_confirm(event.key):
            self.finish_damage_phase()
            return

        # Neutral damage: no affinity text, waiting for Z
        return
    
    
    def handle_item_use_event(self, event):

        if self.item_recover_scroll_done and key_confirm(event.key):

            # 1. Consume the item
            self.model.consume_item(self.pending_item_name)

            # 2. Spend a full press turn
            self.model.handle_action_press_turn_cost(PRESS_TURN_FULL)

            # 3. Advance to next turn
            self.model.next_turn()

            # 4. Return to main battle menu
            self.menu_mode = MENU_MODE_MAIN
            self.menu_index = MENU_INDEX_ITEMS
            return

    def handle_enemy_damaging_event(self, event):
        if event.type == pygame.KEYDOWN and key_confirm(event.key):
            if self.enemy_waiting_for_confirm:
                # Later: apply damage, affinity, press turn logic
                # For now: end enemy turn and return to player
                self.model.handle_action_press_turn_cost(PRESS_TURN_FULL)

                # If enemy has no turns left, switch back to player
                if not self.model.is_player_turn:
                    self.model.next_side()

                self.menu_mode = MENU_MODE_MAIN
                return



    def handle_submenu_event(self, event):
        if key_back(event.key):
            self.menu_mode = MENU_MODE_MAIN

    def handle_event(self, event):
        if event.type != pygame.KEYDOWN:
            return

        if self.menu_mode == MENU_MODE_MAIN:
            self.handle_main_menu_event(event)

        elif self.menu_mode == MENU_MODE_SKILLS:
            self.handle_skills_menu_event(event)

        elif self.menu_mode == MENU_MODE_TARGET_SELECT:
            self.handle_target_select_event(event)

        elif self.menu_mode == MENU_MODE_DAMAGING_ENEMY:
            self.handle_damaging_enemy_event(event)

        elif self.menu_mode == MENU_MODE_GUARDING:
            self.handle_guarding_event(event)

        elif self.menu_mode == MENU_MODE_TALK:
            self.handle_talk_event(event)

        elif self.menu_mode == MENU_MODE_ESCAPE:
            self.handle_escape_event(event)

        elif self.menu_mode == MENU_MODE_ITEMS:
            self.handle_items_event(event)

        elif self.menu_mode == MENU_MODE_ITEM_INFO:
            self.handle_item_info_event(event)

        elif self.menu_mode == MENU_MODE_ITEM_USE:
            self.handle_item_use_event(event)

        elif self.menu_mode == MENU_MODE_ITEM_TARGET_SELECT:
            self.handle_item_target_select_event(event)

        elif self.menu_mode == MENU_MODE_DAMAGING_PLAYER:
            self.handle_enemy_damaging_event(event)

        elif self.menu_mode == MENU_MODE_SUBMENU:
            self.handle_submenu_event(event)

            
    def apply_item_healing(self):
        item = self.pending_item_data
        ally = self.model.player_team[self.selected_ally]

        heal_type = item["type"]
        amount = item["amount"]

        if heal_type == "heal_single_fixed":
            heal = amount
        elif heal_type == "heal_single_percent":
            heal = int(ally.max_hp * (amount / 100))
        else:
            heal = 0

        old_hp = ally.remaining_hp
        new_hp = min(old_hp + heal, ally.max_hp)

        # Store actual heal amount BEFORE animation
        self.item_heal_amount = new_hp - old_hp

        # Apply the healed HP
        ally.remaining_hp = new_hp

        # Set up animation
        ally.hp_target = new_hp
        ally.hp_anim = old_hp

        heal_pixels = int(((new_hp - old_hp) / ally.max_hp) * HP_BAR_WIDTH)
        ally.hp_anim_speed = max(1, min(12, heal_pixels // 4))

        self.item_heal_animating = True





    def finish_guard_phase(self):
        self.model.handle_action_press_turn_cost(PRESS_TURN_FULL)
        self.model.next_turn()
        self.menu_mode = MENU_MODE_MAIN
        self.menu_index = MENU_INDEX_GUARD
        self.scroll_text = ""
        self.scroll_index = 0
        self.scroll_done = True

    def finish_damage_phase(self):
        self.damage_started = False
        self.damage_done = False
        self.affinity_done = False
        self.affinity_text = None

        # We need the affinity of the move that just resolved
        attacker = self.model.get_active_pokemon()
        move = self.smt_moves[self.pending_move_name]
        element = move["element"]
        element_index = ELEMENT_INDEX[element]

        enemy = self.model.enemy_team[self.target_index]
        affinity = enemy.affinities[element_index]

        # NEW: determine press turn cost based on affinity
        cost = self.calculate_press_turns_consumed(affinity)

        # Apply press turn cost
        cost = self.calculate_press_turns_consumed(affinity)
        self.model.handle_action_press_turn_cost(cost)

        # Cleanup
        self.pending_move_name = None
        self.model.next_turn()
        self.menu_mode = MENU_MODE_MAIN
        self.menu_index = 0


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
                           self.enemy_target_index)
        
    def calculate_raw_damage(self, move, affinity_value):
        """
        Returns the raw damage number for a move, before routing.
        No side effects. No HP changes. No text.
        """

        # Null tier → zero damage
        if AFFINITY_NULL <= affinity_value < AFFINITY_REFLECT:
            return 0

        # Otherwise, base damage = move power (placeholder)
        return move["power"]
    
    def calculate_press_turns_consumed(self, affinity):
        """
        Returns:
        - 1 for weakness (affinity < AFFINITY_NEUTRAL)
        - 2 for neutral (affinity == AFFINITY_NEUTRAL)
        - PRESS_TURN_WIPE for null or reflect
        """

        # Weakness → half turn
        if affinity < AFFINITY_NEUTRAL:
            return PRESS_TURN_HALF

        # Neutral → full turn
        if (affinity == AFFINITY_NEUTRAL) or \
           (AFFINITY_RESIST <= affinity < AFFINITY_NULL):
            return PRESS_TURN_FULL
        
        # Null or Reflect → wipe all remaining turns
        if affinity >= AFFINITY_NULL:
            return PRESS_TURN_WIPE

        # Fallback
        return PRESS_TURN_FULL


    
    def determine_damage_recipient(self, attacker, target, affinity_value):
        """
        Determines which Pokémon should receive the damage.
        Does not calculate the damage amount.
        Does not modify HP.
        """

        # Reflect → attacker takes the damage
        if affinity_value == AFFINITY_REFLECT:
            return attacker

        # Otherwise → target takes the damage
        return target
    
    def start_enemy_turn(self):
        self.menu_mode = MENU_MODE_DAMAGING_PLAYER

        # Pick the enemy who is acting (for now, always index 0)
        self.active_enemy_index = 0
        enemy = self.model.enemy_team[self.active_enemy_index]

        # Pick a random move
        self.pending_enemy_move = random.choice(enemy.moves)

        # Pick a random player target
        self.enemy_target_index = random.randrange(len(self.model.player_team))
        target = self.model.player_team[self.enemy_target_index]

        # Prepare scroll text
        self.scroll_text = f"{enemy.name} uses {self.pending_enemy_move} on {target.name}!"
        self.scroll_index = 0
        self.scroll_done = False

        # Reset damage flags
        self.damage_started = False
        self.damage_done = False
        self.affinity_text = None
        self.affinity_done = False
        self.affinity_scroll_index = 0
        self.affinity_scroll_done = False

        # Reset confirm flag
        self.enemy_waiting_for_confirm = False


    
    def update_talk_phase(self):
        if not self.scroll_done:
            chars_per_second = self.scroll_delay * 20
            chars_per_frame = chars_per_second / (SCROLL_CONSTANT * TARGET_FPS)
            self.scroll_index += chars_per_frame
            if int(self.scroll_index) >= len(self.scroll_text):
                self.scroll_index = len(self.scroll_text)
                self.scroll_done = True

    def update_escape_phase(self):
        if not self.scroll_done:
            chars_per_second = self.scroll_delay * 20
            chars_per_frame = chars_per_second / (SCROLL_CONSTANT * TARGET_FPS)
            self.scroll_index += chars_per_frame
            if int(self.scroll_index) >= len(self.scroll_text):
                self.scroll_index = len(self.scroll_text)
                self.scroll_done = True
    
    def update_guard_phase(self):
        if not self.scroll_done:
            chars_per_second = self.scroll_delay * 20
            chars_per_frame = chars_per_second / (SCROLL_CONSTANT * TARGET_FPS)
            self.scroll_index += chars_per_frame
            if int(self.scroll_index) >= len(self.scroll_text):
                self.scroll_index = len(self.scroll_text)
                self.scroll_done = True
        
    def update_damage_phase(self):
        # PHASE 1 — scrolling
        if not self.scroll_done:
            chars_per_second = self.scroll_delay * 20
            chars_per_frame = chars_per_second / (SCROLL_CONSTANT * TARGET_FPS)
            self.scroll_index += chars_per_frame
            if int(self.scroll_index) >= len(self.scroll_text):
                self.scroll_index = len(self.scroll_text)
                self.scroll_done = True
            return

        # PHASE 1.5 — delay before damage
        if not self.damage_started:
            if not self.delay_started:
                self.delay_started = True
                self.delay_frames = 0

            self.delay_frames += 1
            if self.delay_frames < WAIT_FRAMES_BEFORE_DAMAGE:
                return

            # Start damage
            self.delay_started = False
            self.delay_frames = 0

            enemy = self.model.enemy_team[self.target_index]
            attacker = self.model.get_active_pokemon()
            move = self.smt_moves[self.pending_move_name]

            # Determine affinity
            element = move["element"]
            element_index = ELEMENT_INDEX[element]
            affinity = enemy.affinities[element_index]

            # NEW: calculate raw damage
            raw_damage = self.calculate_raw_damage(move, affinity)
            self.damage_amount = raw_damage

            # NEW: determine who takes the damage (reflect support)
            damage_target = self.determine_damage_recipient(attacker, enemy, affinity)

            # Apply damage to the correct Pokémon
            damage_target.hp_target = max(0, damage_target.remaining_hp - raw_damage)
            damage_target.hp_anim = damage_target.remaining_hp

            damage_pixels = int((raw_damage / damage_target.max_hp) * HP_BAR_WIDTH)
            damage_target.hp_anim_speed = max(1, min(12, damage_pixels // 4))

            damage_target.remaining_hp = damage_target.hp_target

            # Store for renderer (important for reflect)
            self.damage_target = damage_target


            self.damage_started = True
            self.damage_animating = True
            return


        # PHASE 2 — HP animation
        if self.damage_animating:
            damage_target = self.damage_target

            if damage_target.hp_anim > damage_target.hp_target:
                diff = damage_target.hp_anim - damage_target.hp_target
                step = max(1, int(diff ** 0.7))
                damage_target.hp_anim -= step
                if damage_target.hp_anim < damage_target.hp_target:
                    damage_target.hp_anim = damage_target.hp_target
            else:
                self.damage_animating = False
                self.damage_done = True

                # Reset affinity state
                self.affinity_done = False
                self.affinity_scroll_done = False
                self.affinity_text = None
                self.affinity_scroll_index = 0

                # Determine affinity (still based on enemy)
                attacker = self.model.get_active_pokemon()
                move = self.smt_moves[self.pending_move_name]
                element = move["element"]
                element_index = ELEMENT_INDEX[element]

                # IMPORTANT: affinity is always based on the enemy's affinities,
                # not the damage target.
                enemy = self.model.enemy_team[self.target_index]
                affinity = enemy.affinities[element_index]

                if affinity == 0:
                    self.affinity_text = None
                    self.affinity_done = True
                    self.affinity_scroll_done = True
                else:
                    if affinity < AFFINITY_NEUTRAL:
                        self.affinity_text = AFFINITY_TEXT_WEAK
                    elif AFFINITY_RESIST <= affinity < AFFINITY_NULL:
                        self.affinity_text = AFFINITY_TEXT_RESIST
                    elif AFFINITY_NULL <= affinity < AFFINITY_REFLECT:
                        self.affinity_text = AFFINITY_TEXT_NULL
                    elif affinity == AFFINITY_REFLECT:
                        self.affinity_text = AFFINITY_TEXT_REFLECT

                    self.affinity_scroll_index = 0
                    self.affinity_scroll_done = False

            # Prepare damage text for the next phase
            self.damage_text = f"Dealt {self.damage_amount} damage."
            self.damage_scroll_index = 0
            self.damage_scroll_done = False

            return



        # PHASE 3a — affinity scroll (only if there IS affinity text)
        if self.damage_done and not self.affinity_done and self.affinity_text:
            chars_per_second = self.scroll_delay * 20
            chars_per_frame = chars_per_second / 60
            self.affinity_scroll_index += chars_per_frame

            if int(self.affinity_scroll_index) >= len(self.affinity_text):
                self.affinity_scroll_index = len(self.affinity_text)
                self.affinity_scroll_done = True
                self.affinity_done = True

            return

        # PHASE 3b — damage text scroll
        if self.damage_done and not self.damage_scroll_done:
            chars_per_second = self.scroll_delay * 20
            chars_per_frame = chars_per_second / 60
            self.damage_scroll_index += chars_per_frame

            if int(self.damage_scroll_index) >= len(self.damage_text):
                self.damage_scroll_index = len(self.damage_text)
                self.damage_scroll_done = True

            return
        
    def update_item_use_phase(self):
        # PHASE 1 — scroll "X uses Y!"
        if not self.item_use_scroll_done:
            chars_per_second = self.scroll_delay * 20
            chars_per_frame = chars_per_second / 60
            self.item_use_scroll_index += chars_per_frame

            if int(self.item_use_scroll_index) >= len(self.item_use_text):
                self.item_use_scroll_index = len(self.item_use_text)
                self.item_use_scroll_done = True

            return

        # PHASE 2 — apply healing ONCE, then start animating
        if not self.item_heal_done and not self.item_heal_animating:
            self.apply_item_healing()
            return

        # PHASE 3 — animate HP rising
        if self.item_heal_animating:
            ally = self.model.player_team[self.selected_ally]

            if ally.hp_anim < ally.hp_target:
                diff = ally.hp_target - ally.hp_anim
                step = max(1, int(diff ** 0.7))
                ally.hp_anim += step
                if ally.hp_anim > ally.hp_target:
                    ally.hp_anim = ally.hp_target
                return

            # Animation finished
            self.item_heal_animating = False
            self.item_heal_done = True

            # Prepare "Recovered X HP!" text
            self.item_recover_text = f"Recovered {self.item_heal_amount} HP!"
            self.item_recover_scroll_index = 0
            self.item_recover_scroll_done = False
            return

        # PHASE 4 — scroll "Recovered X HP!"
        if self.item_heal_done and not self.item_recover_scroll_done:
            chars_per_second = self.scroll_delay * 20
            chars_per_frame = chars_per_second / 60
            self.item_recover_scroll_index += chars_per_frame

            if int(self.item_recover_scroll_index) >= len(self.item_recover_text):
                self.item_recover_scroll_index = len(self.item_recover_text)
                self.item_recover_scroll_done = True

            return

        # PHASE 5 — wait for confirm (handled in input)
        return
    
    def update_enemy_damaging_phase(self):
        # For now, do nothing except scroll the text
        if not self.scroll_done:
            chars_per_second = self.scroll_delay * 20
            chars_per_frame = chars_per_second / 60
            self.scroll_index += chars_per_frame

            if int(self.scroll_index) >= len(self.scroll_text):
                self.scroll_index = len(self.scroll_text)
                self.scroll_done = True

            return
        
        if not self.enemy_waiting_for_confirm:
            self.enemy_waiting_for_confirm = True

        # Later: animate damage, apply damage, handle press turns, etc.
        # For now: immediately end the enemy turn
        #self.model.handle_action_press_turn_cost(PRESS_TURN_FULL)
        #self.model.next_side()  # back to player
        #self.menu_mode = MENU_MODE_MAIN



        
    def update(self):
        if not self.model.is_player_turn:
            # Enemy turn begins → enter damaging-player phase
            if self.menu_mode != MENU_MODE_DAMAGING_PLAYER:
                self.start_enemy_turn()
            elif self.menu_mode == MENU_MODE_DAMAGING_PLAYER:
                self.update_enemy_damaging_phase()
        if self.menu_mode == MENU_MODE_DAMAGING_ENEMY:
            self.update_damage_phase()
        elif self.menu_mode == MENU_MODE_GUARDING:
            self.update_guard_phase()
        elif self.menu_mode == MENU_MODE_ESCAPE:
            self.update_escape_phase()
        elif self.menu_mode == MENU_MODE_TALK:
            self.update_talk_phase()
        elif self.menu_mode == MENU_MODE_ITEM_USE:
            self.update_item_use_phase()

