# battle/battle_model.py

class BattleModel:
    """
    Holds all data for a single battle instance.
    """

    def __init__(self, player_team, enemy_team):
        self.player_team = player_team      # list of Pokémon objects
        self.enemy_team = enemy_team        # list of Pokémon objects

        # Future:
        # self.turn = 0
        # self.weather = None
        # self.active_player_index = 0
        # self.active_enemy_index = 0

    def update(self):
        pass
