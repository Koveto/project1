import tkinter as tk
from player import Player
from map import Map
from constants import SCALE, ACTUAL_WIDTH, ACTUAL_HEIGHT, ACTUAL_TILE_SIZE, SPEED
from PIL import Image
import os
from pokemon_sprites import load_pokemon_sprite

class Game:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("PyPokemon")

        window_width = ACTUAL_WIDTH - ACTUAL_TILE_SIZE
        window_height = ACTUAL_HEIGHT - ACTUAL_TILE_SIZE

        self.root.geometry(f"{window_width}x{window_height}")

        self.canvas = tk.Canvas(
            self.root,
            width=window_width,
            height=window_height,
            bg="black"
        )
        self.canvas.pack()

        # Load initial map
        self.map = Map(self.canvas, "room0")

        # Player starts at tile (5,5)
        self.player = Player(self.canvas, 5 * ACTUAL_TILE_SIZE, 5 * ACTUAL_TILE_SIZE)

        # Input state
        self.keys = {"Up": False, "Down": False, "Left": False, "Right": False}
        self.root.bind("<KeyPress>", self.key_down)
        self.root.bind("<KeyRelease>", self.key_up)

        # Test 64x64 sprites...
        #self.test_sprite = load_pokemon_sprite(gen=2, index=39, is_shiny=True, is_back=True, scale=SCALE)
        #self.canvas.create_image(100, 100, image=self.test_sprite, anchor="nw")

        # Debug collision
        self.debug_walls = False
        self.root.bind("p", self.toggle_debug_walls)

        self.update()

    # ---------------------------------------------------------
    # Input Handling
    # ---------------------------------------------------------
    def key_down(self, event):
        if event.keysym in self.keys:
            self.keys[event.keysym] = True

    def key_up(self, event):
        if event.keysym in self.keys:
            self.keys[event.keysym] = False

    def get_input(self):
        dx = dy = 0
        moving = False
        direction = self.player.direction

        if self.keys["Up"]:
            dy -= SPEED
            direction = "up"
            moving = True
        if self.keys["Down"]:
            dy += SPEED
            direction = "down"
            moving = True
        if self.keys["Left"]:
            dx -= SPEED
            direction = "left"
            moving = True
        if self.keys["Right"]:
            dx += SPEED
            direction = "right"
            moving = True

        return dx, dy, direction, moving

    # ---------------------------------------------------------
    # Movement
    # ---------------------------------------------------------
    def test_movement(self, dx, dy):
        # First try full diagonal movement
        next_x = self.player.x + dx
        next_y = self.player.y + dy

        diagonal_blocked = (
            self.test_collision_screen_bounds(next_x, next_y) or
            self.map.test_collision_walls(
                self.player.x, self.player.y,
                next_x, next_y,
                self.player.width, self.player.height
            )
        )

        if not diagonal_blocked:
            return dx, dy  # diagonal is fine

        # If diagonal is blocked, try X-only
        allowed_dx = 0
        if dx != 0:
            next_x = self.player.x + dx
            if not (
                self.test_collision_screen_bounds(next_x, self.player.y) or
                self.map.test_collision_walls(
                    self.player.x, self.player.y,
                    next_x, self.player.y,
                    self.player.width, self.player.height
                )
            ):
                allowed_dx = dx

        # Try Y-only
        allowed_dy = 0
        if dy != 0:
            next_y = self.player.y + dy
            if not (
                self.test_collision_screen_bounds(self.player.x, next_y) or
                self.map.test_collision_walls(
                    self.player.x, self.player.y,
                    self.player.x, next_y,
                    self.player.width, self.player.height
                )
            ):
                allowed_dy = dy

        # Horizontal movement blocked — check for diagonal slide
        # Only when we're not trying to move upward
        if allowed_dx == 0 and dx != 0 and dy >= 0:
            # Try sliding down a diagonal
            slide_dy = SPEED  # or 1 for a gentler slide

            next_x = self.player.x + dx
            next_y = self.player.y + slide_dy

            if not self.test_collision_screen_bounds(next_x, next_y) and \
            not self.map.test_collision_walls(
                    self.player.x, self.player.y,
                    next_x, next_y,
                    self.player.width, self.player.height
            ):
                allowed_dx = dx
                allowed_dy = slide_dy

        # Vertical movement blocked — check for diagonal upward slide
        # ONLY if we don't already have allowed horizontal movement
        if allowed_dy == 0 and dy < 0 and allowed_dx == 0:
            # Try sliding up a diagonal
            slide_dx = 0

            for wall in self.map.walls:
                wx, wy, length, orient = wall

                if orient == "up_right":
                    slide_dx = SPEED   # slide right
                elif orient == "up_left":
                    slide_dx = -SPEED  # slide left
                else:
                    continue

                next_x = self.player.x + slide_dx
                next_y = self.player.y + dy  # still trying to go up

                if not self.map.test_collision_walls(
                        self.player.x, self.player.y,
                        next_x, next_y,
                        self.player.width, self.player.height,
                        ignore_vertical_walls=True   # new flag
                    ):
                    allowed_dx = slide_dx
                    allowed_dy = dy
                    break

        return allowed_dx, allowed_dy


    def test_collision_screen_bounds(self, x, y):
        if (x < 0) or (x + self.player.width > ACTUAL_WIDTH - ACTUAL_TILE_SIZE) or \
           (y < 0) or (y + self.player.height > ACTUAL_HEIGHT - ACTUAL_TILE_SIZE):
            return True
        return False
    
    def toggle_debug_walls(self, event=None):
        self.debug_walls = not self.debug_walls
        self.map.draw_debug_walls(self.debug_walls)


    # ---------------------------------------------------------
    # Main Update Loop
    # ---------------------------------------------------------
    def update(self):
        dx, dy, direction, moving = self.get_input()

        # Always update facing direction
        self.player.direction = direction

        dx, dy = self.test_movement(dx, dy)

        if moving and (dx != 0 or dy != 0):
            self.player.move(dx, dy)
        else:
            self.player.idle()

        self.root.after(16, self.update)

    # ---------------------------------------------------------
    # Run Game
    # ---------------------------------------------------------
    def run(self):
        self.root.mainloop()
