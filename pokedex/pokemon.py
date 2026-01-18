# pokedex/pokemon.py

import math

class Pokemon:
    def __init__(
        self,
        pokedex_number,
        gen=1,
        is_shiny=False,
        name=None,
        level=1,
        stats=None,        # dict: {"hp": X, "atk": X, ...}
        affinities=None,
        learnset=None,
        bst=None
    ):
        self.pokedex_number = pokedex_number
        self.gen = gen
        self.is_shiny = is_shiny

        self.name = name
        self.level = level
        self.base_stats = stats or {}
        self.affinities = affinities or []
        self.learnset = learnset or []
        self.moves = []
        self.bst = bst

        # Compute actual stats
        self.recalculate_stats()
        self.update_current_moves()

    # ---------------------------------------------------------
    # Stat calculation logic
    # ---------------------------------------------------------
    def recalculate_stats(self):
        lvl = self.level

        base_hp   = self.base_stats.get("hp", 1)
        base_atk  = self.base_stats.get("atk", 1)
        base_def  = self.base_stats.get("def", 1)
        base_spa  = self.base_stats.get("spatk", 1)
        base_spd  = self.base_stats.get("spdef", 1)
        base_spe  = self.base_stats.get("spd", 1)

        # HP formula
        self.max_hp = math.floor((base_hp * 2 * lvl) / 100) + lvl + 10
        self.remaining_hp = self.max_hp

        # For now, MP = HP
        self.max_mp = self.max_hp
        self.remaining_mp = self.max_mp


        # Other stats
        self.actual_atk  = math.floor(5 + math.floor((base_atk * lvl) / 100))
        self.actual_def  = math.floor(5 + math.floor((base_def * lvl) / 100))
        self.actual_spatk = math.floor(5 + math.floor((base_spa * lvl) / 100))
        self.actual_spdef = math.floor(5 + math.floor((base_spd * lvl) / 100))
        self.actual_spd   = math.floor(5 + math.floor((base_spe * lvl) / 100))

    def update_current_moves(self):
        """Populate current_moves based on level and learnset."""
        learned = []

        for entry in self.learnset:
            if entry.level <= self.level:
                learned.append(entry.move)

        # Keep only the last 5 moves learned
        self.moves = learned[-5:]

    @property
    def is_player(self):
        return self.pokedex_number == -1
