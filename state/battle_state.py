# state/battle_state.py

import pygame
from state.state_manager import GameState


class BattleState(GameState):
    """
    Simple battle state that displays a background.
    Future expansion: UI, enemy sprites, menus, animations.
    """

    def __init__(self, background_surface):
        """
        background_surface: a pygame.Surface returned by load_battle_background()
        """
        self.background = background_surface

    # ---------------------------------------------------------
    # State lifecycle
    # ---------------------------------------------------------
    def enter(self):
        """Called when entering the battle state."""
        pass

    def exit(self):
        """Called when leaving the battle state."""
        pass

    # ---------------------------------------------------------
    # Event handling
    # ---------------------------------------------------------
    def handle_event(self, event):
        """
        Battle currently has no interactive UI.
        Future: menu navigation, attack selection, etc.
        """
        pass

    # ---------------------------------------------------------
    # Update logic
    # ---------------------------------------------------------
    def update(self):
        """
        No battle logic yet.
        Future: animations, turn system, enemy AI.
        """
        pass

    # ---------------------------------------------------------
    # Drawing
    # ---------------------------------------------------------
    def draw(self, screen):
        """
        Draw the battle background.
        """
        screen.fill((0, 0, 0))
        screen.blit(self.background, (0, 0))
