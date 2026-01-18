from pokemon_typechart import defensive_profile
from pokemon_stats import load_pokemon_from_json

pokemon_list = load_pokemon_from_json("data/pokemon/pokemon_stats.json")
for p in pokemon_list:
    stat_sum = (
        p.base_stats.hp +
        p.base_stats.atk +
        p.base_stats.defense +
        p.base_stats.sp_atk +
        p.base_stats.sp_def +
        p.base_stats.speed
    )

    if stat_sum != p.base_total:
        print(f"Mismatch for {p.name}: calculated {stat_sum}, expected {p.base_total}")