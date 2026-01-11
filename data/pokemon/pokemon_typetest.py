from pokemon_typechart import defensive_profile
from pokemon_stats import load_pokemon_from_json

pokemon_list = load_pokemon_from_json("data/pokemon/pokemon_stats.json")

while True:
    # Prompt user
    num = int(input("Enter a Pokédex number: "))

    # Find Pokémon
    match = next((p for p in pokemon_list if p.number == num), None)

    if not match:
        print("No Pokémon found with that number.")
    else:
        print(f"\nPokémon #{match.number}: {match.name}")
        print(f"Type(s): {', '.join(match.types)}\n")

        weak, resist, immune = defensive_profile(match)

        print("Weaknesses:")
        for w in weak:
            print("  -", w)

        print("\nResistances:")
        for r in resist:
            print("  -", r)

        print("\nImmunities:")
        for i in immune:
            print("  -", i)
