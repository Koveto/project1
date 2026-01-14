import json
from pokemon_typechart import defensive_profile
from pokemon_stats import load_pokemon_from_json

# ---------------------------------------------------------
# Element → Pokémon type mapping (your 7-element system)
# ---------------------------------------------------------
ELEMENT_GROUPS = {
    "physical": ["Normal", "Fighting", "Steel"],
    "fire": ["Fire", "Ground", "Rock"],
    "force": ["Flying", "Psychic"],
    "ice": ["Water", "Ice"],
    "electric": ["Electric", "Dragon"],
    "light": ["Grass", "Bug", "Fairy"],
    "dark": ["Poison", "Ghost", "Dark"]
}

# ---------------------------------------------------------
# Scoring rules for a single Pokémon type
# ---------------------------------------------------------
def score_type(poke_type, weak, resist, immune):
    t = poke_type.lower()

    if t in immune:
        return 9

    if t in weak:
        return -2 if weak.count(t) > 1 else -1

    if t in resist:
        return 2 if resist.count(t) > 1 else 1

    return 0


# ---------------------------------------------------------
# Compute the 7-element affinity array for a Pokémon
# ---------------------------------------------------------
def compute_affinities(pokemon):
    weak, resist, immune = defensive_profile(pokemon)
    affinities = []

    for element, type_list in ELEMENT_GROUPS.items():

        # Immunity overrides everything
        if any(t.lower() in immune for t in type_list):
            affinities.append(9)
            continue

        total = 0
        for t in type_list:
            total += score_type(t, weak, resist, immune)

        affinities.append(total)

    return affinities


# ---------------------------------------------------------
# Main conversion script
# ---------------------------------------------------------
def main():
    pokemon_list = load_pokemon_from_json("data/pokemon/pokemon_stats.json")

    new_data = {"pokemon": []}

    for p in pokemon_list:
        affinities = compute_affinities(p)

        entry = {
            "no": p.number,
            "name": p.name,
            "bst": p.base_total,
            "affinities": affinities,
            "stats": {
                "HP": p.stats.hp,
                "Atk": p.stats.atk,
                "Def": p.stats.defense,
                "SpAtk": p.stats.sp_atk,
                "SpDef": p.stats.sp_def,
                "Spd": p.stats.speed
            },
            "moves": [
                {"level": m.level, "move": m.move}
                for m in p.moves
            ]
        }

        new_data["pokemon"].append(entry)

    with open("data/pokemon/smt_stats.json", "w", encoding="utf-8") as f:
        json.dump(new_data, f, indent=2)

    print("smt_stats.json created successfully.")


if __name__ == "__main__":
    main()
