# pokedex/pokemon.py

import math, random

class Pokemon:
    def __init__(
        self,
        pokedex_number,
        gen=1,
        is_shiny=False,
        name=None,
        level=1,
        stats=None,        # dict: {"hp": X, "atk": X, ...}
        affinities=None,
        learnset=None,
        moves=None,
        bst=None
    ):
        self.pokedex_number = pokedex_number
        self.gen = gen
        self.is_shiny = is_shiny

        self.name = name
        self.level = level
        self.base_stats = stats or {}
        self.affinities = affinities or []
        self.learnset = learnset or []
        if moves is not None: 
            self.moves = moves 
        else: 
            self.moves = []
        self.bst = bst
        self.is_guarding = False
        # Stat stage modifiers (range: -2 to +2)
        self.attack_buff = 0
        self.defense_buff = 0
        self.speed_buff = 0
        self.attack_buff_turns = 0
        self.defense_buff_turns = 0
        self.speed_buff_turns = 0


        # Compute actual stats
        self.recalculate_stats()
        #self.update_current_moves()

    # ---------------------------------------------------------
    # Stat calculation logic
    # ---------------------------------------------------------
    def recalculate_stats(self):
        lvl = self.level

        base_hp   = self.base_stats.get("hp", 1)
        base_atk  = self.base_stats.get("atk", 1)
        base_def  = self.base_stats.get("def", 1)
        base_spa  = self.base_stats.get("spatk", 1)
        base_spd  = self.base_stats.get("spdef", 1)
        base_spe  = self.base_stats.get("spd", 1)   # SPEED

        # HP formula
        self.max_hp = math.floor((base_hp * 2 * lvl) / 100) + lvl + 10
        self.remaining_hp = self.max_hp

        # MP = HP for now
        self.max_mp = self.max_hp
        self.remaining_mp = self.max_mp

        # Other stats
        self.actual_atk    = math.floor(5 + math.floor((base_atk * lvl) / 100))
        self.actual_def    = math.floor(5 + math.floor((base_def * lvl) / 100))
        self.actual_spatk  = math.floor(5 + math.floor((base_spa * lvl) / 100))
        self.actual_spdef  = math.floor(5 + math.floor((base_spd * lvl) / 100))
        self.actual_speed  = math.floor(5 + math.floor((base_spe * lvl) / 100))

    def update_current_moves(self):
        """Populate current_moves based on level and learnset."""
        learned = []

        for entry in self.learnset:
            if entry.level <= self.level:
                learned.append(entry.move)

        # Keep only the last 5 moves learned
        self.moves = learned[-5:]

    def format_move_for_menu(self, move_name, smt_moves):
        m = smt_moves.get(move_name)
        if not m:
            return f"{move_name[:11]:<11} {'---':>3}  {'----':<5}  {'---':>3}  {'---':<12}"

        name = move_name[:11]

        if m['element'] in ("Support", "Healing"):
            mp = f"{m['mp']:>3}"

            element_short = f"{m['element'][:7]:<7}"

            desc = m.get("description", "")[:15]
            desc = f"{desc:<15}"

            return f"{name:<11} {mp}  {element_short}  {desc}"
        else:
            # Right‑align numbers in 3 spaces
            mp = f"{m['mp']:>3}"
            power = f"{m['power']:>3}" if m["power"] is not None else "---"

            element_short = f"{m['element'][:5]:<5}"

            desc = m.get("description", "")[:12]
            desc = f"{desc:<12}"

            return f"{name:<11} {mp}  {element_short}  {power}  {desc}"

    def choose_random_move(self):
        """
        Returns a random move name from this Pokémon's move list.
        If the Pokémon has no moves, returns None.
        """
        if not self.moves:
            return None
        return random.choice(self.moves)


    @property
    def speed(self):
        return self.actual_speed

    @property
    def is_player(self):
        return self.pokedex_number == -1
