import json
from pokemon_typechart import defensive_profile
from pokemon_stats import load_pokemon_from_json

# ---------------------------------------------------------
# Updated element → Pokémon type mapping
# ---------------------------------------------------------
ELEMENT_GROUPS = {
    "physical": [],  # always 0
    "fire": ["Fire", "Rock", "Ground"],
    "force": ["Normal", "Flying", "Psychic"],
    "ice": ["Fighting", "Water", "Ice"],
    "electric": ["Electric", "Dragon", "Steel"],
    "light": ["Fairy", "Bug", "Grass"],
    "dark": ["Poison", "Ghost", "Dark"]
}

# ---------------------------------------------------------
# Scoring rules
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
# Compute affinities
# ---------------------------------------------------------
def compute_affinities(pokemon):
    weak, resist, immune = defensive_profile(pokemon)
    affinities = []

    for element, type_list in ELEMENT_GROUPS.items():

        # Physical is always 0
        if element == "physical":
            affinities.append(0)
            continue

        # Immunity overrides everything
        if any(t.lower() in immune for t in type_list):
            affinities.append(9)
            continue

        # Sum scores for the 3 mapped types
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
                "HP": p.base_stats.hp,
                "Atk": p.base_stats.atk,
                "Def": p.base_stats.defense,
                "SpAtk": p.base_stats.sp_atk,
                "SpDef": p.base_stats.sp_def,
                "Spd": p.base_stats.speed
            },
            "learnset": [
                {"level": m.level, "move": m.move}
                for m in p.learnset
            ]
        }

        new_data["pokemon"].append(entry)

    with open("data/pokemon/smt_stats.json", "w", encoding="utf-8") as f:
        json.dump(new_data, f, indent=2)

    print("smt_stats.json created successfully.")


if __name__ == "__main__":
    main()
