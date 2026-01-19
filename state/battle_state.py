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
                    move_name = self.model.get_active_player_pokemon().moves[selected_index]
                    enemy = self.model.enemy_team[self.target_index]

                    self.scroll_text = f"{self.model.get_active_player_pokemon().name} uses {move_name} on {enemy.name}!"
                    self.scroll_index = 0
                    self.scroll_done = False

                    return

                if event.key == pygame.K_x:
                    self.menu_mode = MENU_MODE_SKILLS
                    return

                
            elif self.menu_mode == MENU_MODE_DAMAGING_ENEMY:

                # If text is still scrolling, Z/Enter should finish it instantly
                if not self.scroll_done:
                    if event.key in (pygame.K_z, pygame.K_RETURN):
                        self.scroll_index = len(self.scroll_text)
                        self.scroll_done = True
                    return

                # If text is finished, allow advancing to next state
                if event.key in (pygame.K_z, pygame.K_RETURN):
                    self.model.handle_action_press_turn_cost(1)
                    self.model.next_turn()
                    # Reset menu state
                    self.menu_mode = MENU_MODE_MAIN
                    self.menu_index = 0
                    return


            # -------------------------
            # SUBMENU MODE
            # -------------------------
            elif self.menu_mode == MENU_MODE_SUBMENU:

                # Return to main menu
                if event.key == pygame.K_x:
                    self.menu_mode = MENU_MODE_MAIN

    def draw(self, screen):
        self.renderer.draw(screen, self.menu_index, 
                           self.menu_mode, self.previous_menu_index,
                           self.skills_cursor, self.skills_scroll,
                           self.target_index, self.scroll_text,
                           self.scroll_index)
        
    def update(self):
        # Update scrolling text ONLY in damaging mode
        if self.menu_mode == MENU_MODE_DAMAGING_ENEMY and not self.scroll_done:
            # Count frames
            self.scroll_timer += 1

            # When enough frames pass, reveal the next character
            if self.scroll_timer >= self.scroll_speed:
                self.scroll_timer = 0
                self.scroll_index += 1

                if self.scroll_index >= len(self.scroll_text):
                    self.scroll_index = len(self.scroll_text)
                    self.scroll_done = True


        

