# battle/battle_model.py
from battle.battle_constants import *

class BattleModel:
    """
    Holds all data for a single battle instance.
    """

    def __init__(self, player_team, enemy_team):
        self.player_team = player_team      # list of Pokémon objects
        self.enemy_team = enemy_team        # list of Pokémon objects
        self.turn_index = 0
        # Press Turn system
        self.press_turns = FRESH_PRESS_TURNS   # 4 full turns
        self.is_player_turn = True        # True = blue icons, False = red icons


    def update(self):
        pass

    def get_active_player_pokemon(self):
        return self.player_team[self.turn_index]


    def next_turn(self):
        # Move to the next Pokémon on the player team
        self.turn_index = (self.turn_index + 1) % len(self.player_team)

    def consume_press_turn(self, amount):
        """
        amount = 2 for full turn
        amount = 1 for half turn
        Consumes the leftmost non-zero icon.
        """
        for i in range(4):
            if self.press_turns[i] > 0:
                # Reduce the icon
                self.press_turns[i] -= amount

                # Clamp to zero (never negative)
                if self.press_turns[i] < 0:
                    self.press_turns[i] = 0

                break

    def has_press_turns_left(self):
        return any(v > 0 for v in self.press_turns)
    
    def next_side(self):
        self.is_player_turn = not self.is_player_turn

        # Reset press turns for the new side
        self.press_turns = FRESH_PRESS_TURNS

    def handle_action_press_turn_cost(self, cost):
        """
        cost = 2 for full turn
        cost = 1 for half turn
        """
        self.consume_press_turn(cost)

        if not self.has_press_turns_left():
            self.next_side()

    def get_press_turn_icon_states(self, anim_frame):
        """
        Returns a list of 4 states:
        'transparent', 'solid_blue', 'flash_blue',
        'solid_red', 'flash_red'
        """
        states = []
        color = "blue" if self.is_player_turn else "red"
        flashing_on = (anim_frame // 10) % 2 == 0

        for value in self.press_turns:
            if value == 2:
                states.append(f"solid_{color}")
            elif value == 1:
                states.append(f"flash_{color}" if flashing_on else PT_STATE_TRANSPARENT)
            else:
                states.append(PT_STATE_TRANSPARENT)

        return states

    def get_player_team(self):
        return self.player_team
    
    def get_enemy_team(self):
        return self.enemy_team
    
    def get_turn_index(self):
        return self.turn_index
    
    def get_press_turns(self):
        return self.press_turns
    
    def is_player_turn(self):
        return self.is_player_turn

    def get_active_pokemon(self):
        return self.player_team[self.turn_index]