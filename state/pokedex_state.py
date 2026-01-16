# state/pokedex_state.py

import pygame
from state.state_manager import GameState
from pokedex.ui_navigation import handle_navigation


class PokedexState(GameState):
    """
    Wraps the Pokédex subsystem into a game state.
    Handles:
        - navigation (arrow keys)
        - text input (search bar)
        - drawing the Pokédex UI
    """

    def __init__(self, controller, view):
        """
        controller: PokemonController instance
        view: PokemonView instance
        """
        self.controller = controller
        self.view = view

    # ---------------------------------------------------------
    # State lifecycle
    # ---------------------------------------------------------
    def enter(self):
        """Called when entering the Pokédex."""
        pass

    def exit(self):
        """Called when leaving the Pokédex."""
        pass

    # ---------------------------------------------------------
    # Event handling
    # ---------------------------------------------------------
    def handle_event(self, event):
        """
        The Pokédex has two layers of input:
            1. Navigation (arrow keys, page movement)
            2. Text input (search bar)
        Navigation must run first, just like in your original design.
        """
        handle_navigation(event, self.controller, self.view)
        self.view.handle_event(event, self.controller)

    # ---------------------------------------------------------
    # Update logic
    # ---------------------------------------------------------
    def update(self):
        """
        The Pokédex currently has no per-frame update logic.
        """
        pass

    # ---------------------------------------------------------
    # Drawing
    # ---------------------------------------------------------
    def draw(self, screen):
        """
        Draw the Pokédex UI.
        """
        screen.fill((0, 0, 0))
        self.view.draw(screen)
