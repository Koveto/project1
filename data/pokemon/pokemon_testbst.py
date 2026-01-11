from pokemon_typechart import defensive_profile
from pokemon_stats import load_pokemon_from_json

pokemon_list = load_pokemon_from_json("data/pokemon/pokemon_stats.json")
for p in pokemon_list:
    stat_sum = (
        p.stats.hp +
        p.stats.atk +
        p.stats.defense +
        p.stats.sp_atk +
        p.stats.sp_def +
        p.stats.speed
    )

    if stat_sum != p.base_total:
        print(f"Mismatch for {p.name}: calculated {stat_sum}, expected {p.base_total}")