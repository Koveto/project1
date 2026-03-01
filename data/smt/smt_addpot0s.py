import json

def add_healing_support_potentials(in_path="data/smt/smt_stats.json",
                                   out_path="data/smt/smt_stats_new.json"):
    with open(in_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    for entry in data["pokemon"]:
        # Existing potential list (7 values)
        old_potential = entry.get("potential", [])

        # Ensure correct length before extending
        if len(old_potential) != 7:
            print(f"Warning: Pokémon #{entry.get('no')} has unexpected potential length {len(old_potential)}")

        # Append two zeros: Healing, Support
        new_potential = old_potential + [0, 0]

        entry["potential"] = new_potential

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


if __name__ == "__main__":
    add_healing_support_potentials()
