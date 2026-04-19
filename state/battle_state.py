# state/battle_state_new.py

from constants import *
from state.state_manager import GameState

from battle.battle_constants import *
from battle.battle_renderer import BattleRenderer

class BattleState(GameState):
    def __init__(self, battle_background):
        self.renderer = BattleRenderer(self, battle_background)
    
    def draw(self, screen):
        self.renderer.draw(self, screen)

    def handle_event(self, event):
        pass

    def update(self):
        pass