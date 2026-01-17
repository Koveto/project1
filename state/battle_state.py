# state/battle_state.py

import pygame
from state.state_manager import GameState
from battle.battle_model import BattleModel
from battle.battle_renderer import BattleRenderer
from pokedex.pokemon import Pokemon

class BattleState(GameState):

    def __init__(self, background_surface):
        player_team = [
            Pokemon(-1),    # Player
            Pokemon(34),    # Nidoking
            Pokemon(115),   # Kangaskhan
            Pokemon(6)      # Charizard
        ]

        enemy_team = [
            Pokemon(9),     # Blastoise
            Pokemon(3),     # Venusaur
            Pokemon(150),   # Mewtwo
            Pokemon(12)     # Butterfree
        ]

        self.model = BattleModel(player_team, enemy_team)
        self.renderer = BattleRenderer(background_surface, self.model)

        self.menu_index = 0

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:

            # -------------------------
            # RIGHT
            # -------------------------
            if event.key == pygame.K_RIGHT:
                if 0 <= self.menu_index <= 2:
                    self.menu_index += 1
                elif self.menu_index == 3:
                    self.menu_index = 0
                elif 4 <= self.menu_index <= 6:
                    # cycle among 4,5,6
                    self.menu_index = 4 + ((self.menu_index - 4 + 1) % 3)

            # -------------------------
            # LEFT
            # -------------------------
            elif event.key == pygame.K_LEFT:
                if 1 <= self.menu_index <= 3:
                    self.menu_index -= 1
                elif self.menu_index == 0:
                    self.menu_index = 3
                elif 4 <= self.menu_index <= 6:
                    # cycle among 4,5,6
                    self.menu_index = 4 + ((self.menu_index - 4 - 1) % 3)

            # -------------------------
            # DOWN
            # -------------------------
            elif event.key == pygame.K_DOWN:
                if self.menu_index in (0, 1, 2):
                    self.menu_index += 4
                elif self.menu_index in (4, 5, 6):
                    self.menu_index -= 4
                # index 3 does nothing

            # -------------------------
            # UP
            # -------------------------
            elif event.key == pygame.K_UP:
                if self.menu_index in (4, 5, 6):
                    self.menu_index -= 4
                elif self.menu_index in (0, 1, 2):
                    self.menu_index += 4
                # index 3 does nothing



    def draw(self, screen):
        self.renderer.draw(screen, self.menu_index)

