# battle/battle_model.py

class BattleModel:
    """
    Holds all data for a single battle instance.
    """

    def __init__(self, player_team, enemy_team):
        self.player_team = player_team      # list of Pokémon objects
        self.enemy_team = enemy_team        # list of Pokémon objects
        self.turn_index = 0

    def update(self):
        pass

    def get_active_player_pokemon(self):
        # Always return the special player Pokémon (-1)
        for p in self.player_team:
            if p.pokedex_number == -1:
                return p

        # Fallback: first real Pokémon
        for p in self.player_team:
            if p.pokedex_number != -1:
                return p

        return None


