# data/smt/smt_stats.py

import json
from dataclasses import dataclass
from typing import List, Dict

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


# ---------------------------------------------------------
# Loader
# ---------------------------------------------------------

def load_smt_from_json(path: str) -> List[Pokemon]:
    """Load Pokémon from SMT-style JSON and return real Pokemon objects."""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    result = []

    for entry in data["pokemon"]:
        stats = SMTStats.from_dict(entry["stats"])
        moves = [Move(m["level"], m["move"]) for m in entry.get("moves", [])]

        p = Pokemon(
            pokedex_number=entry["no"],
            name=entry["name"],
            level=entry.get("level", 1),
            stats=stats,
            affinities=entry["affinities"],
            moves=moves,
            bst=entry["bst"]
        )

        result.append(p)

    return result

def get_smt_pokemon_by_number(smt_list, number):
    return next((p for p in smt_list if p.pokedex_number == number), None)
