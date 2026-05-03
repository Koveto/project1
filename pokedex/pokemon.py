import math
import random


class Pokemon:
    """
    Core Pokémon data model used by battle, menus, and the Pokédex.
    """

    def __init__(
        self,
        pokedex_number,
        is_shiny=False,
        name=None,
        level=1,
        stats=None,          # dict: {"hp": X, "atk": X, ...}
        affinities=None,
        potential=None,
        learnset=None,
        moves=None,
        bst=None
    ):
        # Identity
        self.pokedex_number = pokedex_number
        self.name = name
        self.is_shiny = is_shiny

        # Level & stats
        self.level = level
        self.base_stats = stats or {}
        self.bst = bst

        # SMT mechanics
        self.affinities = affinities or []
        self.potential = potential or [0] * 9

        # Moves
        self.learnset = learnset or []
        self.moves = moves or []

        # Battle state
        self.is_guarding = False

        # Stat stage modifiers (range: -2 to +2)
        self.attack_buff = 0
        self.defense_buff = 0
        self.speed_buff = 0
        self.attack_buff_turns = 0
        self.defense_buff_turns = 0
        self.speed_buff_turns = 0

        # Sprite system
        # Default for menus/Pokédex: non‑shiny front pose 0
        self.sprite_column = 0

        self.base_max_hp   = self.base_stats.get("hp", 1)
        self.base_attack  = self.base_stats.get("atk", 1)
        self.base_defense  = self.base_stats.get("def", 1)
        self.base_spattack  = self.base_stats.get("spatk", 1)
        self.base_spdefense  = self.base_stats.get("spdef", 1)
        self.base_speed  = self.base_stats.get("spd", 1)

        # HP formula
        self.max_hp = int(self.level + 10 + math.floor((2 * self.base_max_hp * self.level) / 100))
        self.remaining_hp = self.max_hp

        # MP = HP for now
        self.max_mp = self.max_hp
        self.remaining_mp = self.max_mp

        # Other stats
        self.attack     = int(5 + math.floor((2 * self.base_attack * self.level) / 100))
        self.defense    = int(5 + math.floor((2 * self.base_defense * self.level) / 100))
        self.spattack   = int(5 + math.floor((2 * self.base_spattack * self.level) / 100))
        self.spdefense  = int(5 + math.floor((2 * self.base_spdefense * self.level) / 100))
        self.speed      = int(5 + math.floor((2 * self.base_speed * self.level) / 100))


    # ---------------------------------------------------------
    # Move helpers
    # ---------------------------------------------------------
    def update_current_moves(self):
        """Populate moves based on level and learnset."""
        learned = [entry.move for entry in self.learnset if entry.level <= self.level]
        self.moves = learned[-5:]

    # ---------------------------------------------------------
    # Properties
    # ---------------------------------------------------------  
    @property
    def is_player(self):
        return self.pokedex_number == -1

    @property
    def row(self):
        """Row in the giant sprite sheet."""
        return self.pokedex_number - 1

    @property
    def sprite_col(self):
        """Column in the giant sprite sheet."""
        return self.sprite_column

    @sprite_col.setter
    def sprite_col(self, value):
        self.sprite_column = value
