# state/battle_state.py

import pygame
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

    def in_damage_phase(self):
        return self.menu_mode == MENU_MODE_DAMAGING_ENEMY

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

        elif event.key in (pygame.K_z, pygame.K_RETURN):
            if self.menu_mode == MENU_MODE_MAIN and self.menu_index == MENU_INDEX_SKILLS:
                self.menu_mode = MENU_MODE_SKILLS
                self.previous_menu_index = self.menu_index
                self.menu_index = 0
                return

            if self.menu_mode == MENU_MODE_MAIN and self.menu_index == MENU_INDEX_PASS:
                self.model.handle_action_press_turn_cost(PRESS_TURN_HALF)
                self.model.next_turn()
                self.menu_mode = MENU_MODE_MAIN
                self.menu_index = MENU_INDEX_SKILLS
                return

            self.previous_menu_index = self.menu_index
            self.menu_mode = MENU_MODE_SUBMENU


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

        elif event.key in (pygame.K_z, pygame.K_RETURN):
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
                self.target_index = 0
                return

        elif event.key == pygame.K_x:
            self.menu_mode = MENU_MODE_MAIN


    def handle_target_select_event(self, event):
        enemy_count = len(self.model.enemy_team)

        if event.key == pygame.K_LEFT:
            if enemy_count > 0:
                self.target_index = (self.target_index - 1) % enemy_count

        elif event.key == pygame.K_RIGHT:
            if enemy_count > 0:
                self.target_index = (self.target_index + 1) % enemy_count

        elif event.key in (pygame.K_z, pygame.K_RETURN):
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

        elif event.key == pygame.K_x:
            self.menu_mode = MENU_MODE_SKILLS
            return


    def handle_damaging_enemy_event(self, event):
        # 1) If text is still scrolling, allow skip
        if not self.scroll_done:
            if event.key in (pygame.K_z, pygame.K_RETURN):
                self.scroll_index = len(self.scroll_text)
                self.scroll_done = True
            return

        # 2) If damage is still animating, ignore input
        if not self.damage_done:
            return

        # 3) Affinity text phase
        if self.affinity_text and not self.affinity_done:
            if not self.affinity_scroll_done:
                if event.key in (pygame.K_z, pygame.K_RETURN):
                    self.affinity_scroll_index = len(self.affinity_text)
                    self.affinity_scroll_done = True
                return

            if event.key in (pygame.K_z, pygame.K_RETURN):
                self.finish_damage_phase()
            return

        # 4) Everything done → now Z advances the turn
        if event.key in (pygame.K_z, pygame.K_RETURN):
            self.finish_damage_phase()
            return

        # Neutral damage: no affinity text, waiting for Z
        return


    def handle_submenu_event(self, event):
        if event.key == pygame.K_x:
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

        elif self.in_damage_phase():
            self.handle_damaging_enemy_event(event)

        elif self.menu_mode == MENU_MODE_SUBMENU:
            self.handle_submenu_event(event)

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
                           self.affinity_scroll_done)
        
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
        
    def update_damage_phase(self):
        # PHASE 1 — scrolling
        if not self.scroll_done:
            chars_per_second = self.scroll_delay * 20
            chars_per_frame = chars_per_second / 60
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

            return


        # PHASE 3 — affinity scroll
        if self.damage_done and not self.affinity_done and self.affinity_text:
            chars_per_second = self.scroll_delay * 20
            chars_per_frame = chars_per_second / 60
            self.affinity_scroll_index += chars_per_frame
            if int(self.affinity_scroll_index) >= len(self.affinity_text):
                self.affinity_scroll_index = len(self.affinity_text)
                self.affinity_scroll_done = True

        
    def update(self):
        if self.in_damage_phase():
            self.update_damage_phase()
