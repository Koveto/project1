# state/overworld_state.py

import pygame

from state.state_manager import GameState
from overworld.movement import test_movement, update_camera


class OverworldState(GameState):
    """
    Handles overworld gameplay: movement, collisions, camera, and map transitions.
    """

    def __init__(self, map_obj, player, screen_width, screen_height, debug_walls_enabled):
        self.map = map_obj
        self.player = player
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.debug_walls_enabled = debug_walls_enabled

        # Movement state
        self.dx = 0
        self.dy = 0
        self.direction = self.player.direction
        self.moving = False

    # ---------------------------------------------------------
    # State lifecycle
    # ---------------------------------------------------------
    def enter(self):
        """Called when entering the overworld state."""
        pass

    def exit(self):
        """Called when leaving the overworld state."""
        pass

    # ---------------------------------------------------------
    # Event handling
    # ---------------------------------------------------------
    def handle_event(self, event):
        """
        Overworld currently does not use direct event handling.
        Movement is handled in update() via pygame.key.get_pressed().
        """
        pass

    # ---------------------------------------------------------
    # Update logic
    # ---------------------------------------------------------
    def update(self):
        # Get keyboard input
        keys = pygame.key.get_pressed()
        self.dx, self.dy, self.direction, self.moving = self.player.handle_input(keys)
        self.player.direction = self.direction

        # Collision + movement resolution
        self.dx, self.dy = test_movement(self.map, self.player, self.dx, self.dy)
        self.player.update(self.dx, self.dy, self.direction, self.moving)

        # Warp transitions
        warp = self.map.check_warp(
            self.player.x,
            self.player.y,
            self.player.width,
            self.player.height
        )

        if warp is not None:
            # Load new map
            self.map = self.map.__class__(
                warp["to_room"],
                self.screen_width,
                self.screen_height
            )

            # Move player to destination
            self.player.x = warp["dest_x"]
            self.player.y = warp["dest_y"]

            # Optional facing direction
            if warp.get("dest_facing") is not None:
                self.player.direction = warp["dest_facing"]

        # Update camera
        update_camera(self.map, self.player, self.screen_width, self.screen_height)

    # ---------------------------------------------------------
    # Drawing
    # ---------------------------------------------------------
    def draw(self, screen):
        screen.fill((0, 0, 0))
        self.map.draw(screen, self.debug_walls_enabled)
        self.player.draw(screen, self.map.camera_x, self.map.camera_y)
