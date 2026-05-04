# data/smt/smt_stats.py

import json
from dataclasses import dataclass
from typing import List, Dict, Optional

from pokedex.pokemon import Pokemon


# ---------------------------------------------------------
# Data classes
# ---------------------------------------------------------

@dataclass
class Move:
    level: int
    move: str


@dataclass
class SMTStats:
    hp: int
    atk: int
    defense: int
    sp_atk: int
    sp_def: int
    speed: int

    @classmethod
    def from_dict(cls, data: Dict):
        return cls(
            hp=data["HP"],
            atk=data["Atk"],
            defense=data["Def"],
            sp_atk=data["SpAtk"],
            sp_def=data["SpDef"],
            speed=data["Spd"]
        )

    def to_base_stat_dict(self):
        """Convert SMTStats → dict format expected by Pokemon."""
        return {
            "hp": self.hp,
            "atk": self.atk,
            "def": self.defense,
            "spatk": self.sp_atk,
            "spdef": self.sp_def,
            "spd": self.speed,
        }


# ---------------------------------------------------------
# Species Loader (NO Pokémon instances here)
# ---------------------------------------------------------

def load_pkmn_from_json(path: str) -> List[Dict]:
    """
    Load raw species data from JSON.
    Returns a list of dicts, NOT Pokémon objects.
    """
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["pokemon"]


# ---------------------------------------------------------
# Species lookup
# ---------------------------------------------------------

def get_species_by_number(species_list: List[Dict], pokedex_number: int) -> Optional[Dict]:
    """
    Return the species dict matching the given Pokédex number.
    """
    return next((s for s in species_list if s["no"] == pokedex_number), None)


# ---------------------------------------------------------
# Pokémon factory (creates UNIQUE Pokémon instances)
# ---------------------------------------------------------

def create_pokemon_from_species(entry: Dict, level: Optional[int] = None) -> Pokemon:
    """
    Create a fresh Pokémon instance from a species entry.
    This ensures no shared references between player/enemy teams.
    """
    # Convert stats
    raw_stats = SMTStats.from_dict(entry["stats"])
    stats_dict = raw_stats.to_base_stat_dict()

    # Learnset
    learnset = [Move(m["level"], m["move"]) for m in entry.get("learnset", [])]

    # Potential (default 9 zeros)
    potential = entry.get("potential") or [0] * 9

    # Construct a NEW Pokémon instance
    return Pokemon(
        pokedex_number=entry["no"],
        name=entry["name"],
        level=level or entry.get("level", 1),
        stats=stats_dict,
        affinities=entry["affinities"],
        potential=potential,
        learnset=learnset,
        bst=entry["bst"]
    )
