import pygame
from constants import SPEED, TARGET_FPS
from overworld.player_sprite import load_player_frames


class Player:
    def __init__(self, x, y):
        # Position in WORLD space
        self.x = x
        self.y = y

        # Load frames (already scaled + transparent)
        self.frames = load_player_frames(scale=4)

        # Tkinter-style animation state
        self.direction = "down"
        self.anim_cycle = [0, 1, 0, 2]   # EXACT Tkinter cycle
        self.anim_index = 0
        self.step_counter = 0

        # Movement constants
        # Tkinter moved SPEED px per frame at ~60 FPS.
        # To match that feel at 30 FPS, we double it.
        self.speed_per_frame = SPEED * (60 / TARGET_FPS)

        # Current frame
        self.current_frame = self.frames[self.direction][0]

        # Dimensions
        self.width = self.current_frame.get_width()
        self.height = self.current_frame.get_height()

    # ---------------------------------------------------------
    # Input + Movement (Tkinter-style)
    # ---------------------------------------------------------
    def handle_input(self, keys):
        """
        Reproduce Tkinter's EXACT direction priority:
        Up → Down → Left → Right
        """
        dx = dy = 0
        moving = False
        direction = self.direction

        # Tkinter priority order
        if keys[pygame.K_UP]:
            dy -= self.speed_per_frame
            direction = "up"
            moving = True

        if keys[pygame.K_DOWN]:
            dy += self.speed_per_frame
            direction = "down"
            moving = True

        if keys[pygame.K_LEFT]:
            dx -= self.speed_per_frame
            direction = "left"
            moving = True

        if keys[pygame.K_RIGHT]:
            dx += self.speed_per_frame
            direction = "right"
            moving = True

        return dx, dy, direction, moving

    # ---------------------------------------------------------
    # Update (movement + animation)
    # ---------------------------------------------------------
    def update(self, dx, dy, direction, moving):
        # Update direction
        self.direction = direction

        # Move in WORLD space (no dt, discrete movement)
        if moving and (dx != 0 or dy != 0):
            self.x += dx
            self.y += dy

            # Tkinter-style step-based animation
            self.step_counter += 1
            if self.step_counter % 6 == 0:
                self.anim_index = (self.anim_index + 1) % len(self.anim_cycle)
        else:
            # Idle frame
            self.anim_index = 0

        # Select frame
        frame_id = self.anim_cycle[self.anim_index]
        self.current_frame = self.frames[self.direction][frame_id]

    # ---------------------------------------------------------
    # Draw
    # ---------------------------------------------------------
    def draw(self, screen, camera_x, camera_y):
        screen.blit(
            self.current_frame,
            (self.x - camera_x, self.y - camera_y)
        )
