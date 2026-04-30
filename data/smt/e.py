import json

def expand_potentials():
    # Load the existing JSON
    with open("data\\smt\\smt_stats.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    # Modify each Pokémon entry
    for mon in data.get("pokemon", []):
        pot = mon.get("potential")
        if isinstance(pot, list):
            pot.append(0)  # add one new zero at the end

    # Write the updated JSON
    with open("smt_stats_new.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    expand_potentials()
