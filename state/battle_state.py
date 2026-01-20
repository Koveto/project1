# state/battle_state.py

import pygame
from constants import *
from battle.battle_constants import *
from state.state_manager import GameState
from battle.battle_model import BattleModel
from battle.battle_renderer import BattleRenderer
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
        self.menu_mode = "main"
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






    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:

            # -------------------------
            # MAIN MENU NAVIGATION
            # -------------------------
            if self.menu_mode == "main":

                # -------------------------
                # RIGHT
                # -------------------------
                if event.key == pygame.K_RIGHT:
                    # Top row: 0→1→2→3→0
                    if 0 <= self.menu_index <= 2:
                        self.menu_index += 1
                    elif self.menu_index == 3:
                        self.menu_index = 0

                    # Bottom row: 4→5→6→7→4
                    elif 4 <= self.menu_index <= 6:
                        self.menu_index += 1
                    elif self.menu_index == 7:
                        self.menu_index = 4

                # -------------------------
                # LEFT
                # -------------------------
                elif event.key == pygame.K_LEFT:
                    # Top row: 3→2→1→0→3
                    if 1 <= self.menu_index <= 3:
                        self.menu_index -= 1
                    elif self.menu_index == 0:
                        self.menu_index = 3

                    # Bottom row: 5→4, 6→5, 7→6, 4→7
                    elif 5 <= self.menu_index <= 7:
                        self.menu_index -= 1
                    elif self.menu_index == 4:
                        self.menu_index = 7

                # -------------------------
                # DOWN
                # -------------------------
                elif event.key == pygame.K_DOWN:
                    # 0↔4, 1↔5, 2↔6, 3↔7
                    if 0 <= self.menu_index <= 3:
                        self.menu_index += 4
                    # bottom row goes back up
                    elif 4 <= self.menu_index <= 7:
                        self.menu_index -= 4

                # -------------------------
                # UP
                # -------------------------
                elif event.key == pygame.K_UP:
                    # 4↔0, 5↔1, 6↔2, 7↔3
                    if 4 <= self.menu_index <= 7:
                        self.menu_index -= 4
                    elif 0 <= self.menu_index <= 3:
                        self.menu_index += 4


                # -------------------------
                # SELECT (Z or ENTER)
                # -------------------------
                elif event.key in (pygame.K_z, pygame.K_RETURN):

                    # SKILLS OPTION (index 0)
                    if self.menu_mode == MENU_MODE_MAIN and self.menu_index == 0:
                        # Reset menu state
                        self.menu_mode = MENU_MODE_SKILLS
                        self.previous_menu_index = self.menu_index
                        self.menu_index = 0
                        return

                    # PASS OPTION (index 6)
                    if self.menu_mode == MENU_MODE_MAIN and self.menu_index == 6:
                        # End the turn immediately
                        self.model.handle_action_press_turn_cost(1)
                        self.model.next_turn()
                        # Reset menu state
                        self.menu_mode = MENU_MODE_MAIN
                        self.menu_index = 0
                        return

                    # Otherwise go to submenu
                    self.previous_menu_index = self.menu_index
                    self.menu_mode = MENU_MODE_SUBMENU

            elif self.menu_mode == MENU_MODE_SKILLS:

                if event.key == pygame.K_DOWN:
                    total = len(self.model.get_active_pokemon().moves)

                    # Case 1: cursor can move down within the visible window
                    if self.skills_cursor < 2 and self.skills_cursor < total - 1:
                        self.skills_cursor += 1

                    # Case 2: cursor is at bottom, but we can scroll
                    elif self.skills_scroll + 3 < total:
                        self.skills_scroll += 1

                    # Case 3: cursor moves again after scrolling is maxed out
                    elif self.skills_cursor < 2:
                        self.skills_cursor += 1
                
                if event.key == pygame.K_UP:
                    total = len(self.model.get_active_pokemon().moves)

                    # Case 1: cursor can move up within the visible window
                    if self.skills_cursor > 0:
                        self.skills_cursor -= 1

                    # Case 2: cursor is at top, but we can scroll up
                    elif self.skills_scroll > 0:
                        self.skills_scroll -= 1

                    # Case 3: cursor moves again after scrolling is maxed out
                    elif self.skills_cursor > 0:
                        self.skills_cursor -= 1

                elif event.key in (pygame.K_z, pygame.K_RETURN):
                    pokemon = self.model.get_active_pokemon()

                    # Determine selected move
                    selected_index = self.skills_scroll + self.skills_cursor
                    move_name = pokemon.moves[selected_index]
                    move = self.smt_moves.get(move_name)

                    # --- Assumption checks ---
                    if (
                        move["target"] == "Single" and
                        move["type"] in ("Physical", "Special") and
                        pokemon.remaining_mp >= move["mp"]
                    ):
                        # Enter target selection mode
                        self.menu_mode = MENU_MODE_TARGET_SELECT
                        self.target_index = 0
                        return

                    # Otherwise: do nothing yet (future cases)


                if event.key == pygame.K_x:
                    self.menu_mode = MENU_MODE_MAIN


            elif self.menu_mode == MENU_MODE_TARGET_SELECT:

                enemy_count = len(self.model.enemy_team)

                if event.key == pygame.K_LEFT:
                    if enemy_count > 0:
                        self.target_index = (self.target_index - 1) % enemy_count

                if event.key == pygame.K_RIGHT:
                    if enemy_count > 0:
                        self.target_index = (self.target_index + 1) % enemy_count

                if event.key in (pygame.K_z, pygame.K_RETURN):

                    # Switch to damaging state
                    self.menu_mode = MENU_MODE_DAMAGING_ENEMY

                    # Build the scrolling message
                    selected_index = self.skills_scroll + self.skills_cursor
                    active_pokemon = self.model.get_active_pokemon()
                    move_name = active_pokemon.moves[selected_index]
                    enemy = self.model.enemy_team[self.target_index]

                    # Remember which move will be used for damage
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

                if event.key == pygame.K_x:
                    self.menu_mode = MENU_MODE_SKILLS
                    return


                
            elif self.menu_mode == MENU_MODE_DAMAGING_ENEMY:

                enemy = self.model.enemy_team[self.target_index]

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
                    # If still scrolling, Z finishes it
                    if not self.affinity_scroll_done:
                        if event.key in (pygame.K_z, pygame.K_RETURN):
                            self.affinity_scroll_index = len(self.affinity_text)
                            self.affinity_scroll_done = True
                        return

                    # Scrolling is done — Z should advance the turn immediately
                    if event.key in (pygame.K_z, pygame.K_RETURN):
                        self.finish_damage_phase()
                    return



                # 4) Everything done → now Z advances the turn
                if event.key in (pygame.K_z, pygame.K_RETURN):
                    self.damage_started = False
                    self.damage_done = False
                    self.affinity_done = False
                    self.affinity_text = None
                    self.pending_move_name = None

                    self.model.handle_action_press_turn_cost(1)
                    self.model.next_turn()
                    self.menu_mode = MENU_MODE_MAIN
                    self.menu_index = 0
                    return

                # Neutral damage: no affinity text, waiting for Z
                # Do nothing — renderer will keep drawing the attack text
                return






            # -------------------------
            # SUBMENU MODE
            # -------------------------
            elif self.menu_mode == MENU_MODE_SUBMENU:

                # Return to main menu
                if event.key == pygame.K_x:
                    self.menu_mode = MENU_MODE_MAIN


    def finish_damage_phase(self):
        self.damage_started = False
        self.damage_done = False
        self.affinity_done = False
        self.affinity_text = None
        self.pending_move_name = None

        self.model.handle_action_press_turn_cost(1)
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
        
    def update(self):

        # ---------------------------------------------------------
        # PHASE 1 — ATTACK TEXT SCROLLING
        # ---------------------------------------------------------
        if self.menu_mode == MENU_MODE_DAMAGING_ENEMY and not self.scroll_done:

            chars_per_second = self.scroll_delay * 20
            chars_per_frame = chars_per_second / 60

            self.scroll_index += chars_per_frame
            visible_chars = int(self.scroll_index)

            if visible_chars >= len(self.scroll_text):
                self.scroll_index = len(self.scroll_text)
                self.scroll_done = True


        # ---------------------------------------------------------
        # PHASE 1.5 — DELAY BEFORE DAMAGE ANIMATION
        # ---------------------------------------------------------
        if (self.menu_mode == MENU_MODE_DAMAGING_ENEMY and
            self.scroll_done and
            not self.damage_started):

            if not self.delay_started:
                self.delay_started = True
                self.delay_frames = 0

            self.delay_frames += 1
            if self.delay_frames < WAIT_FRAMES_BEFORE_DAMAGE:
                return

            # Delay finished → start damage
            self.delay_started = False
            self.delay_frames = 0

            enemy = self.model.enemy_team[self.target_index]
            attacker = self.model.get_active_pokemon()
            move = self.smt_moves[self.pending_move_name]
            damage = move["power"]

            enemy.hp_target = max(0, enemy.remaining_hp - damage)
            enemy.hp_anim = enemy.remaining_hp

            damage_pixels = int((damage / enemy.max_hp) * HP_BAR_WIDTH)
            enemy.hp_anim_speed = max(1, min(12, damage_pixels // 4))

            enemy.remaining_hp = enemy.hp_target

            self.damage_started = True
            self.damage_animating = True


        # ---------------------------------------------------------
        # PHASE 2 — HP ANIMATION
        # ---------------------------------------------------------
        if self.damage_animating:
            enemy = self.model.enemy_team[self.target_index]

            if enemy.hp_anim > enemy.hp_target:
                diff = enemy.hp_anim - enemy.hp_target
                step = max(1, int(diff ** 0.7))
                enemy.hp_anim -= step

                if enemy.hp_anim < enemy.hp_target:
                    enemy.hp_anim = enemy.hp_target

            else:
                # HP animation finished
                self.damage_animating = False
                self.damage_done = True

                # Reset affinity state
                self.affinity_done = False
                self.affinity_scroll_done = False
                self.affinity_text = None
                self.affinity_scroll_index = 0   # <-- REQUIRED FIX

                # Determine affinity text
                attacker = self.model.get_active_pokemon()
                move = self.smt_moves[self.pending_move_name]
                element = move["element"]
                element_index = ELEMENT_INDEX[element]
                affinity = enemy.affinities[element_index]

                if affinity == 0:
                    # Neutral hit
                    self.affinity_text = None
                    self.affinity_done = True
                    self.affinity_scroll_done = True
                else:
                    # Non-neutral hit
                    if affinity < 0:
                        self.affinity_text = "It's super effective!"
                    elif affinity in (1, 2):
                        self.affinity_text = "It's not very effective..."
                    elif 3 <= affinity <= 8:
                        self.affinity_text = "But it had no effect!"
                    elif affinity == 9:
                        self.affinity_text = "But it was reflected back!"

                    # Start scrolling affinity text
                    self.affinity_scroll_index = 0
                    self.affinity_scroll_done = False



        # ---------------------------------------------------------
        # PHASE 3 — AFFINITY TEXT SCROLLING
        # ---------------------------------------------------------
        if (self.menu_mode == MENU_MODE_DAMAGING_ENEMY and
            self.damage_done and
            not self.affinity_done and
            self.affinity_text):

            chars_per_second = self.scroll_delay * 20
            chars_per_frame = chars_per_second / 60

            self.affinity_scroll_index += chars_per_frame
            visible = int(self.affinity_scroll_index)

            if visible >= len(self.affinity_text):
                self.affinity_scroll_index = len(self.affinity_text)
                self.affinity_scroll_done = True
