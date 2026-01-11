import os, sys

# Add the parent folder (project1/data/pokemon) to sys.path
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(ROOT)

from pokemon_stats import load_pokemon_from_json

class PokemonController:
    """
    Manages the list of Pokémon, the current index, and navigation.
    """

    def __init__(self):
        # Path to the JSON file relative to this folder
        root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        json_path = os.path.join(root, "pokemon_stats.json")

        # Load Pokémon list
        self.pokemon_list = load_pokemon_from_json(json_path)

        # Sort by Pokédex number just to be safe
        self.pokemon_list.sort(key=lambda p: p.number)

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
        """Return the currently selected Pokémon object."""
        return self.pokemon_list[self.index]

    def get_current_index(self):
        """Return the current Pokédex index (1-based)."""
        return self.index + 1

    def get_total_count(self):
        """Return total number of Pokémon loaded."""
        return len(self.pokemon_list)

    # ---------------------------------------------------------
    # Future expansion: filtering
    # ---------------------------------------------------------
    def apply_filter(self, filter_func):
        """
        Apply a filter function to the Pokémon list.
        filter_func should accept a Pokémon object and return True/False.
        """
        self.filtered_list = [p for p in self.pokemon_list if filter_func(p)]
        self.index = 0

    def clear_filter(self):
        """Remove any active filters."""
        self.filtered_list = None
        self.index = 0
