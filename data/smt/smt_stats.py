import json
from dataclasses import dataclass, field
from typing import List, Dict


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


@dataclass
class SMTPokemon:
    number: int
    name: str
    bst: int
    level: int          # <-- ADD THIS
    affinities: List[int]
    stats: SMTStats
    moves: List[Move] = field(default_factory=list)


    @classmethod
    def from_dict(cls, data: Dict):
        stats = SMTStats.from_dict(data["stats"])
        moves = [Move(m["level"], m["move"]) for m in data.get("moves", [])]

        return cls(
            number=data["no"],
            name=data["name"],
            bst=data["bst"],
            level=data.get("level", 1),   # default to 1 if missing
            affinities=data["affinities"],
            stats=stats,
            moves=moves
        )


    def __str__(self):
        return f"{self.number}: {self.name} | Affinities {self.affinities}"


# ---------------------------------------------------------
# Loader function
# ---------------------------------------------------------

def load_smt_from_json(path: str) -> List[SMTPokemon]:
    """Load all SMT-style Pokémon entries from smt_stats.json."""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return [SMTPokemon.from_dict(entry) for entry in data["pokemon"]]
