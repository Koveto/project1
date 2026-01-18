# state/battle_state.py

import pygame
from state.state_manager import GameState
from battle.battle_model import BattleModel
from battle.battle_renderer import BattleRenderer
from pokedex.pokemon import Pokemon
from data.smt.smt_stats import load_smt_from_json, get_smt_pokemon_by_number


class BattleState(GameState):

    def __init__(self, background_surface):

        # Load SMT Pokémon data
        smt_pokemon = load_smt_from_json("data/smt/smt_stats.json")

        # Fetch Bulbasaur (no = 1)
        bulbasaur_data = get_smt_pokemon_by_number(smt_pokemon, 1)

        # Create the player Pokémon using Bulbasaur's data
        player_pokemon = Pokemon(
            pokedex_number=-1,          # special player marker
            name="Brendan",             # override name
            level=bulbasaur_data.level,
            stats=bulbasaur_data.stats,
            affinities=bulbasaur_data.affinities,
            moves=bulbasaur_data.moves
        )

        # Build teams
        player_team = [
            player_pokemon,
            get_smt_pokemon_by_number(smt_pokemon, 34),   # Nidoking
            get_smt_pokemon_by_number(smt_pokemon, 115),  # Kangaskhan
            get_smt_pokemon_by_number(smt_pokemon, 6)     # Charizard
        ]

        enemy_team = [
            get_smt_pokemon_by_number(smt_pokemon, 9),    # Blastoise
            get_smt_pokemon_by_number(smt_pokemon, 3),    # Venusaur
            get_smt_pokemon_by_number(smt_pokemon, 150),  # Mewtwo
            get_smt_pokemon_by_number(smt_pokemon, 12)    # Butterfree
        ]

        self.model = BattleModel(player_team, enemy_team)
        self.renderer = BattleRenderer(background_surface, self.model)

        self.menu_index = 0
        self.menu_mode = "main"
        self.previous_menu_index = 0


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

                    # PASS OPTION (index 2)
                    if self.menu_mode == "main" and self.menu_index == 6:
                        # End the turn immediately
                        self.model.handle_action_press_turn_cost(1)
                        self.model.next_turn()
                        # Reset menu state
                        self.menu_mode = "main"
                        self.menu_index = 0
                        return

                    # Otherwise go to submenu
                    self.previous_menu_index = self.menu_index
                    self.menu_mode = "submenu"


            # -------------------------
            # SUBMENU MODE
            # -------------------------
            elif self.menu_mode == "submenu":

                # Return to main menu
                if event.key == pygame.K_x:
                    self.menu_mode = "main"




    def draw(self, screen):
        self.renderer.draw(screen, self.menu_index, self.menu_mode, self.previous_menu_index)


