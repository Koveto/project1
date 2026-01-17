# pokedex/pokemon.py

class Pokemon:
    def __init__(self, pokedex_number, gen=1, is_shiny=False):
        self.pokedex_number = pokedex_number
        self.gen = gen
        self.is_shiny = is_shiny

    @property
    def is_player(self):
        return self.pokedex_number == -1
