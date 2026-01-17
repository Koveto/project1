import os
from data.smt.smt_stats import load_smt_from_json


class PokemonController:
    """
    Manages the list of Pokémon, the current index, and navigation.
    """

    def __init__(self):
        # Path to smt_stats.json relative to this file
        json_path = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),  # pokedex/
                "..",                       # data/
                "data",
                "smt",
                "smt_stats.json"
            )
        )

        # Load Pokémon list
        self.pokemon_list = load_smt_from_json(json_path)
        self.max_pokemon = len(self.pokemon_list)

        # Sort by Pokédex number
        self.pokemon_list.sort(key=lambda p: p.pokedex_number)

        # Current index (0-based)
        self.index = 0

        # Placeholder for future filters
        self.filtered_list = None

    # ---------------------------------------------------------
    # Navigation
    # ---------------------------------------------------------
    def next(self):
        """Move to the next Pokémon, wrapping around."""
        self.index = (self.index + 1) % len(self.pokemon_list)

    def prev(self):
        """Move to the previous Pokémon, wrapping around."""
        self.index = (self.index - 1) % len(self.pokemon_list)

    # ---------------------------------------------------------
    # Accessors
    # ---------------------------------------------------------
    def get_current_pokemon(self):
        return self.pokemon_list[self.index]

    def get_current_index(self):
        return self.index + 1

    def get_total_count(self):
        return len(self.pokemon_list)

    # ---------------------------------------------------------
    # Filtering
    # ---------------------------------------------------------
    def apply_filter(self, filter_func):
        self.filtered_list = [p for p in self.pokemon_list if filter_func(p)]
        self.index = 0

    def clear_filter(self):
        self.filtered_list = None
        self.index = 0

    # ---------------------------------------------------------
    # Searching
    # ---------------------------------------------------------
    def find_by_name(self, text):
        text = text.lower()

        # 1. Exact match
        for i, p in enumerate(self.pokemon_list):
            if p.name.lower() == text:
                return i

        # 2. Startswith match
        for i, p in enumerate(self.pokemon_list):
            if p.name.lower().startswith(text):
                return i

        # 3. Contains match
        for i, p in enumerate(self.pokemon_list):
            if text in p.name.lower():
                return i

        # 4. Fuzzy match
        def score(name):
            name = name.lower()
            length_diff = abs(len(name) - len(text))
            mismatch = sum(1 for a, b in zip(name, text) if a != b)
            return length_diff + mismatch

        return min(range(len(self.pokemon_list)), key=lambda i: score(self.pokemon_list[i].name))

    # ---------------------------------------------------------
    # Sorting
    # ---------------------------------------------------------
    def get_bst(self, pokemon):
        return pokemon.bst

    def sort_by_bst_ascending(self):
        self.pokemon_list.sort(key=lambda p: p.bst)
        self.index = 0

    def sort_by_bst_descending(self):
        self.pokemon_list.sort(key=lambda p: p.bst, reverse=True)
        self.index = 0

    def sort_by_number(self):
        self.pokemon_list.sort(key=lambda p: p.pokedex_number)
        self.index = 0

    def sort_by_stat(self, stat_name):
        self.pokemon_list.sort(
            key=lambda p: getattr(p.stats, stat_name),
            reverse=True
        )
        self.index = 0

    def sort_by_affinity(self, index):
        self.pokemon_list.sort(
            key=lambda p: p.affinities[index],
            reverse=True
        )
        self.index = 0
