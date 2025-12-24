import tkinter as tk
from player import Player
from map import Map
from constants import (
    SCALE, ACTUAL_WIDTH, ACTUAL_HEIGHT,
    ACTUAL_TILE_SIZE, SPEED
)
from pokemon_sprites import load_pokemon_sprite


class Game:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("PyPokemon")

        # Window size (map is slightly larger than visible area)
        window_width = ACTUAL_WIDTH - ACTUAL_TILE_SIZE
        window_height = ACTUAL_HEIGHT - ACTUAL_TILE_SIZE
        self.root.geometry(f"{window_width}x{window_height}")

        # Canvas
        self.canvas = tk.Canvas(
            self.root,
            width=window_width,
            height=window_height,
            bg="black"
        )
        self.canvas.pack()

        # Map + Player
        self.room0_drawn = False
        self.map = Map(self.canvas, "room1")
        self.camera_x = 0
        self.camera_y = 0

        self.player = Player(
            self.canvas,
            5 * ACTUAL_TILE_SIZE,
            5 * ACTUAL_TILE_SIZE
        )

        # Input state
        self.keys = {"Up": False, "Down": False, "Left": False, "Right": False}
        self.root.bind("<KeyPress>", self.key_down)
        self.root.bind("<KeyRelease>", self.key_up)

        # Debug toggle
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
    # Movement Resolver
    # ---------------------------------------------------------
    def test_movement(self, dx, dy):
        px, py = self.player.x, self.player.y
        w, h = self.player.width, self.player.height

        # --- 1. Try full movement ---------------------------------
        nx, ny = px + dx, py + dy
        if not (
            self.test_collision_screen_bounds(nx, ny) or
            self.map.test_collision_walls(px, py, nx, ny, w, h)
        ):
            return dx, dy

        # --- 2. Try X-only -----------------------------------------
        allowed_dx = 0
        if dx != 0:
            nx = px + dx
            if not (
                self.test_collision_screen_bounds(nx, py) or
                self.map.test_collision_walls(px, py, nx, py, w, h)
            ):
                allowed_dx = dx

        # --- 3. Try Y-only -----------------------------------------
        allowed_dy = 0
        if dy != 0:
            ny = py + dy
            if not (
                self.test_collision_screen_bounds(px, ny) or
                self.map.test_collision_walls(px, py, px, ny, w, h)
            ):
                allowed_dy = dy

        # --- 4. Horizontal blocked → try sliding DOWN a diagonal ---
        # Only when not trying to move upward
        if allowed_dx == 0 and dx != 0 and dy >= 0:
            slide_dy = SPEED
            nx, ny = px + dx, py + slide_dy

            if not (
                self.test_collision_screen_bounds(nx, ny) or
                self.map.test_collision_walls(px, py, nx, ny, w, h)
            ):
                allowed_dx = dx
                allowed_dy = slide_dy

        # --- 5. Vertical blocked → try sliding UP a diagonal -------
        # Only if we don't already have horizontal movement
        if allowed_dy == 0 and dy < 0 and allowed_dx == 0:
            for wx, wy, length, orient in self.map.walls:

                if orient == "up_right":
                    slide_dx = SPEED
                elif orient == "up_left":
                    slide_dx = -SPEED
                else:
                    continue

                nx, ny = px + slide_dx, py + dy

                if not self.map.test_collision_walls(
                    px, py, nx, ny, w, h,
                    ignore_vertical_walls=True
                ):
                    allowed_dx = slide_dx
                    allowed_dy = dy
                    break

        return allowed_dx, allowed_dy

    # ---------------------------------------------------------
    # Screen Bounds
    # ---------------------------------------------------------
    def test_collision_screen_bounds(self, x, y):
        # Non-scrolling maps: clamp to screen
        if not self.map.scrolling:
            if x < 0 or y < 0:
                return True
            if x + self.player.width > ACTUAL_WIDTH - ACTUAL_TILE_SIZE:
                return True
            if y + self.player.height > ACTUAL_HEIGHT - ACTUAL_TILE_SIZE:
                return True
            return False

        # Scrolling maps: clamp to MAP edges, not screen edges
        if x < 0 or y < 0:
            return True
        if x + self.player.width > self.map.pixel_width:
            return True
        if y + self.player.height > self.map.pixel_height:
            return True

        return False

    # ---------------------------------------------------------
    # Camera
    # ---------------------------------------------------------
    def update_camera(self):
        # If this map doesn't scroll, keep camera at (0,0)
        if not self.map.scrolling:
            self.camera_x = 0
            self.camera_y = 0
            # Only draw once for non-scrolling maps
            if not hasattr(self, "_room0_drawn"):
                self.map.set_camera(0, 0)
                self._room0_drawn = True
            return

        # Canvas may not be initialized yet
        canvas_w = self.canvas.winfo_width()
        canvas_h = self.canvas.winfo_height()

        if canvas_w < 10 or canvas_h < 10:
            return  # wait until window is fully realized

        # Center camera on player
        half_w = canvas_w // 2
        half_h = canvas_h // 2

        self.camera_x = self.player.x - half_w
        self.camera_y = self.player.y - half_h

        # Clamp camera to map bounds
        max_x = self.map.pixel_width  - canvas_w
        max_y = self.map.pixel_height - canvas_h

        self.camera_x = max(0, min(self.camera_x, max_x))
        self.camera_y = max(0, min(self.camera_y, max_y))

        # Redraw visible tiles
        old_x, old_y = self.map.camera_x, self.map.camera_y

        self.map.camera_x = self.camera_x
        self.map.camera_y = self.camera_y

        # Only redraw if camera actually moved
        if self.map.camera_x != old_x or self.map.camera_y != old_y:
            self.map.redraw_visible_tiles()

    # ---------------------------------------------------------
    # Debug Toggle
    # ---------------------------------------------------------
    def toggle_debug_walls(self, event=None):
        self.debug_walls = not self.debug_walls
        self.map.draw_debug_walls(self.debug_walls)

    # ---------------------------------------------------------
    # Main Update Loop
    # ---------------------------------------------------------
    def update(self):
        # Draw room0 once after canvas is ready
        if not self.map.scrolling and not self.room0_drawn:
            if self.canvas.winfo_width() > 10:
                self.map.set_camera(0, 0)
                self.room0_drawn = True

        dx, dy, direction, moving = self.get_input()
        self.player.direction = direction

        # Resolve collisions in WORLD space
        dx, dy = self.test_movement(dx, dy)

        # Update player position in WORLD space
        if moving and (dx != 0 or dy != 0):
            self.player.move(dx, dy)
        else:
            self.player.idle()

        # Update camera based on player WORLD position
        self.update_camera()
        self.canvas.tag_raise("debug_wall")
        self.canvas.tag_raise("player")

        # Position player sprite relative to camera
        self.canvas.coords(
            self.player.sprite,
            self.player.x - self.camera_x,
            self.player.y - self.camera_y
        )

        #print(len(self.canvas.find_all()))

        self.root.after(16, self.update)

    # ---------------------------------------------------------
    # Run Game
    # ---------------------------------------------------------
    def run(self):
        self.root.mainloop()
