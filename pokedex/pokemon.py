# pokedex/pokemon.py

class Pokemon:
    def __init__(
        self,
        pokedex_number,
        gen=1,
        is_shiny=False,
        name=None,
        level=1,
        stats=None,
        affinities=None,
        moves=None,
        bst=None
    ):
        self.pokedex_number = pokedex_number
        self.gen = gen
        self.is_shiny = is_shiny

        # SMT data
        self.name = name
        self.level = level
        self.stats = stats
        self.affinities = affinities or []
        self.moves = moves or []
        self.bst = bst

    @property
    def is_player(self):
        return self.pokedex_number == -1
