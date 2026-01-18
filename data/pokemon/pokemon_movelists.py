from pokemon_typechart import defensive_profile
from pokemon_stats import load_pokemon_from_json

pokemon_list = load_pokemon_from_json("data/pokemon/pokemon_stats.json")

all_learnset = set()  # use a set to avoid duplicates

for p in pokemon_list:
    for mv in p.learnset:
        all_learnset.add(mv.move)

# Convert to sorted list
sorted_learnset = sorted(all_learnset)

# Print each move on its own line
for move in sorted_learnset:
    print(move)