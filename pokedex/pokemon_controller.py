import os
import random

from data.smt.smt_stats import (
    load_pkmn_from_json,
    get_species_by_number,
    create_pokemon_from_species
)


class PokemonController:
    """
    Manages the list of Pokémon species, creates Pokémon instances for display,
    and handles navigation, sorting, and searching.
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

        # Load raw species data (NOT Pokémon instances)
        self.species_list = load_pkmn_from_json(json_path)

        # Sort species by Pokédex number
        self.species_list.sort(key=lambda s: s["no"])

        # Current index (0-based)
        self.index = 0

        # Optional filtered list
        self.filtered_list = None

    # ---------------------------------------------------------
    # Internal helpers
    # ---------------------------------------------------------

    def _active_list(self):
        """Return filtered list if active, otherwise full species list."""
        return self.filtered_list if self.filtered_list is not None else self.species_list

    def _current_species(self):
        """Return the species dict at the current index."""
        return self._active_list()[self.index]

    # ---------------------------------------------------------
    # Navigation
    # ---------------------------------------------------------

    def next(self):
        lst = self._active_list()
        self.index = (self.index + 1) % len(lst)

    def prev(self):
        lst = self._active_list()
        self.index = (self.index - 1) % len(lst)

    # ---------------------------------------------------------
    # Accessors
    # ---------------------------------------------------------

    def get_current_pokemon(self):
        """
        Return a *fresh* Pokémon instance for the current species.
        This ensures the Pokédex never shares Pokémon objects.
        """
        species = self._current_species()
        return create_pokemon_from_species(species, level=species.get("level", 1))

    def get_current_index(self):
        return self.index + 1

    def get_total_count(self):
        return len(self._active_list())

    # ---------------------------------------------------------
    # Filtering
    # ---------------------------------------------------------

    def apply_filter(self, filter_func):
        self.filtered_list = [s for s in self.species_list if filter_func(s)]
        self.index = 0

    def clear_filter(self):
        self.filtered_list = None
        self.index = 0

    # ---------------------------------------------------------
    # Searching
    # ---------------------------------------------------------

    def find_by_name(self, text):
        text = text.lower()
        lst = self._active_list()

        # 1. Exact match
        for i, s in enumerate(lst):
            if s["name"].lower() == text:
                return i

        # 2. Startswith match
        for i, s in enumerate(lst):
            if s["name"].lower().startswith(text):
                return i

        # 3. Contains match
        for i, s in enumerate(lst):
            if text in s["name"].lower():
                return i

        # 4. Fuzzy match
        def score(name):
            name = name.lower()
            length_diff = abs(len(name) - len(text))
            mismatch = sum(1 for a, b in zip(name, text) if a != b)
            return length_diff + mismatch

        return min(range(len(lst)), key=lambda i: score(lst[i]["name"]))

    # ---------------------------------------------------------
    # Sorting
    # ---------------------------------------------------------

    def sort_by_bst_ascending(self):
        self.species_list.sort(key=lambda s: s["bst"])
        self.index = 0

    def sort_by_bst_descending(self):
        self.species_list.sort(key=lambda s: s["bst"], reverse=True)
        self.index = 0

    def sort_by_number(self):
        self.species_list.sort(key=lambda s: s["no"])
        self.index = 0

    def sort_by_stat(self, stat_name):
        self.species_list.sort(
            key=lambda s: s["stats"].get(stat_name.upper(), 0),
            reverse=True
        )
        self.index = 0

    def sort_by_affinity(self, index):
        self.species_list.sort(
            key=lambda s: s["affinities"][index],
            reverse=True
        )
        self.index = 0

    def sort_by_potential(self, index):
        self.species_list.sort(
            key=lambda s: s.get("potential", [0] * 9)[index],
            reverse=True
        )
        self.index = 0
