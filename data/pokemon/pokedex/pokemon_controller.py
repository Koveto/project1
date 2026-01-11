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
        self.max_pokemon = len(self.pokemon_list)

    
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

    def find_by_name(self, text):
        """
        Return the index of the Pokémon whose name best matches the text.
        Matching rules:
        - Exact match (case-insensitive)
        - Startswith match
        - Contains match
        - Fuzzy best guess (very simple scoring)
        """

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

        # 4. Fuzzy: pick the Pokémon with the smallest edit distance
        # (simple heuristic: difference in length + mismatched chars)
        def score(name):
            name = name.lower()
            length_diff = abs(len(name) - len(text))
            mismatch = sum(1 for a, b in zip(name, text) if a != b)
            return length_diff + mismatch

        best_index = min(range(len(self.pokemon_list)), key=lambda i: score(self.pokemon_list[i].name))
        return best_index

