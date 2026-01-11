import json
from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class Move:
    level: int
    move: str


@dataclass
class PokemonStats:
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
class Pokemon:
    number: int
    name: str
    base_total: int
    types: List[str]
    stats: PokemonStats
    moves: List[Move] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict):
        stats = PokemonStats.from_dict(data["stats"])
        moves = [Move(m["level"], m["move"]) for m in data.get("moves", [])]

        return cls(
            number=data["no"],
            name=data["name"],
            base_total=data["level"],
            types = [t for t in data["types"] if t is not None],
            stats=stats,
            moves=moves
        )

    def __str__(self):
        return f"{self.number}: {self.name} ({'/'.join(self.types)})"

def load_pokemon_from_json(path: str) -> List[Pokemon]:
    """Load all Pokémon entries from stats.json."""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return [Pokemon.from_dict(entry) for entry in data["pokemon"]]
