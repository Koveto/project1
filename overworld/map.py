import json
import os
import pygame
from overworld.tileset import Tileset
from constants import SCALE


class Map:
    def __init__(self, name, screen_width, screen_height):
        """
        Pygame version of the Map class.

        - Loads JSON map data
        - Manages tiles, walls, and camera
        - Renders only visible tiles to a given surface
        - Provides collision helpers identical to the Tkinter version
        """
        self.name = name

        data = self.load_map_data(name)

        self.width = data["width"]
        self.height = data["height"]
        self.tiles = data["tiles"]

        self.scrolling = data.get("scrolling", True)

        self.walls = data.get("walls", [])
        scaled_walls = []
        for wx, wy, length, orient in self.walls:
            scaled_walls.append((wx * SCALE, wy * SCALE, length * SCALE, orient))
        self.walls = scaled_walls

        self.tileset = self.load_tileset(data["tileset"])

        self.warps = data.get("warps", [])
        scaled_warps = []
        for warp in self.warps:
            scaled_warps.append({
                "x": warp["x"] * SCALE,
                "y": warp["y"] * SCALE,
                "width": warp["width"] * SCALE,
                "height": warp["height"] * SCALE,
                "to_room": warp["to_room"],
                "dest_x": warp["dest_x"] * SCALE,
                "dest_y": warp["dest_y"] * SCALE,
                "dest_facing": warp.get("dest_facing", None)
            })
        self.warps = scaled_warps

        self.camera_x = 0
        self.camera_y = 0

        self.pixel_width = (
            self.width * self.tileset.tile_width * self.tileset.scale
        )
        self.pixel_height = (
            self.height * self.tileset.tile_height * self.tileset.scale
        )

        # Screen size is needed to compute visible tiles
        self.screen_width = screen_width
        self.screen_height = screen_height

    # ---------------------------------------------------------
    # Loading
    # ---------------------------------------------------------
    def load_map_data(self, name):
        """Load JSON map data from disk."""
        path = os.path.join("data", "maps", f"{name}.json")
        with open(path, "r") as f:
            return json.load(f)

    def load_tileset(self, tileset_name):
        """Load the tileset used by this map."""
        return Tileset(tileset_name)

    # ---------------------------------------------------------
    # Drawing
    # ---------------------------------------------------------
    def draw(self, surface, debug=False):
        """
        Draw the visible portion of the map onto the given surface.
        """
        self.redraw_visible_tiles(surface)

        if debug:
            self.draw_debug_walls(surface)

    def redraw_visible_tiles(self, surface):
        """
        Draw only the tiles that are visible within the current camera.
        """
        tw = self.tileset.tile_width * self.tileset.scale
        th = self.tileset.tile_height * self.tileset.scale

        canvas_w = self.screen_width
        canvas_h = self.screen_height

        # Visible tile range
        start_x = int(max(0, self.camera_x // tw))
        start_y = int(max(0, self.camera_y // th))

        end_x = int(min(self.width, (self.camera_x + canvas_w) // tw + 2))
        end_y = int(min(self.height, (self.camera_y + canvas_h) // th + 2))

        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                tile_id = self.tiles[y][x]
                img = self.tileset.get(tile_id)  # pygame.Surface

                px = x * tw - self.camera_x
                py = y * th - self.camera_y

                surface.blit(img, (px, py))

    def draw_debug_walls(self, surface):
        """Draw debug wall overlays onto the given surface."""
        for x, y, length, orient in self.walls:
            x1, y1, x2, y2 = self.compute_wall_endpoints(x, y, length, orient)

            # Offset by camera to get screen coordinates
            sx1 = x1 - self.camera_x
            sy1 = y1 - self.camera_y
            sx2 = x2 - self.camera_x
            sy2 = y2 - self.camera_y

            # Color by type
            if orient == "h":
                color = (255, 0, 0)      # red
            elif orient == "v":
                color = (0, 0, 255)      # blue
            else:
                color = (0, 255, 0)      # green for diagonals

            # Pygame has no native dashed lines; use solid for now
            pygame.draw.line(surface, color, (sx1, sy1), (sx2, sy2), width=2)
        
        # ---------------------------------------------------------
        # Draw warps as 4 border lines
        # ---------------------------------------------------------
        for warp in self.warps:
            wx = warp["x"] - self.camera_x
            wy = warp["y"] - self.camera_y
            ww = warp["width"]
            wh = warp["height"]

            # Rectangle corners
            x1, y1 = wx, wy
            x2, y2 = wx + ww, wy
            x3, y3 = wx + ww, wy + wh
            x4, y4 = wx, wy + wh

            color = (255, 255, 0)  # yellow

            # Top
            pygame.draw.line(surface, color, (x1, y1), (x2, y2), width=2)
            # Right
            pygame.draw.line(surface, color, (x2, y2), (x3, y3), width=2)
            # Bottom
            pygame.draw.line(surface, color, (x3, y3), (x4, y4), width=2)
            # Left
            pygame.draw.line(surface, color, (x4, y4), (x1, y1), width=2)


    # ---------------------------------------------------------
    # Collision
    # ---------------------------------------------------------
    def test_collision_walls(
        self,
        old_x, old_y,
        new_x, new_y,
        w, h,
        ignore_vertical_walls=False
    ):
        """Return True if movement collides with any wall."""

        # Player bounding boxes
        old_left,  old_right  = old_x, old_x + w
        old_top,   old_bottom = old_y, old_y + h
        new_left,  new_right  = new_x, new_x + w
        new_top,   new_bottom = new_y, new_y + h

        for wx, wy, length, orient in self.walls:

            # -----------------------------------------------------
            # Horizontal wall (blocks vertical movement)
            # -----------------------------------------------------
            if orient == "h":
                wall_x1, wall_x2 = wx, wx + length
                wall_y = wy

                # No horizontal overlap
                if new_right < wall_x1 or new_left > wall_x2:
                    continue

                # Crossing downward
                if old_bottom <= wall_y < new_bottom:
                    return True

                # Crossing upward
                if old_top >= wall_y > new_top:
                    return True

            # -----------------------------------------------------
            # Vertical wall (blocks horizontal movement)
            # -----------------------------------------------------
            elif orient == "v":
                if ignore_vertical_walls:
                    continue

                wall_y1, wall_y2 = wy, wy + length
                wall_x = wx

                # No vertical overlap
                if new_bottom < wall_y1 or new_top > wall_y2:
                    continue

                # Crossing right
                if old_right <= wall_x < new_right:
                    return True

                # Crossing left
                if old_left >= wall_x > new_left:
                    return True

            # -----------------------------------------------------
            # Diagonal walls (45°)
            # -----------------------------------------------------
            elif orient in ("up_right", "up_left", "down_left", "down_right"):
                x1, y1, x2, y2 = self.compute_wall_endpoints(wx, wy, length, orient)
                
                # Player centers
                old_cx = old_x + w / 2
                old_cy = old_y + h / 2
                new_cx = new_x + w / 2
                new_cy = new_y + h / 2

                # Bounding box reject
                min_x, max_x = min(x1, x2), max(x1, x2)
                min_y, max_y = min(y1, y2), max(y1, y2)

                pad = max(w, h) / 2

                if not (min_x - pad <= new_cx <= max_x + pad and
                        min_y - pad <= new_cy <= max_y + pad):
                    continue

                dist = self.point_line_distance(x1, y1, x2, y2, new_cx, new_cy)
                # Thin diagonal distance check
                if dist > 8:
                    continue

                # Blocked side
                if self.diagonal_blocked(x1, y1, x2, y2, new_cx, new_cy, orient):
                    return True

                # Crossing the diagonal
                if self.diagonal_crossed(x1, y1, x2, y2, old_cx, old_cy, new_cx, new_cy):
                    return True

        return False
    
    def check_warp(self, x, y, w, h):
        """Return warp dict if (x, y, w, h) overlaps a warp region, else None."""
        left, right = x, x + w
        top, bottom = y, y + h

        for warp in self.warps:
            wx, wy = warp["x"], warp["y"]
            ww, wh = warp["width"], warp["height"]

            w_left, w_right = wx, wx + ww
            w_top, w_bottom = wy, wy + wh

            if not (right <= w_left or left >= w_right or
                    bottom <= w_top or top >= w_bottom):
                return warp

        return None

    # ---------------------------------------------------------
    # Wall Geometry
    # ---------------------------------------------------------
    def compute_wall_endpoints(self, x, y, length, orient):
        if orient == "h":
            return x, y, x + length, y

        if orient == "v":
            return x, y, x, y + length

        if orient == "up_right":      # ↗
            return x, y, x + length, y - length

        if orient == "up_left":       # ↖
            return x, y, x - length, y - length

        if orient == "down_left":     # ↙
            return x, y, x - length, y + length

        if orient == "down_right":    # ↘
            return x, y, x + length, y + length

        return x, y, x, y  # fallback

    # ---------------------------------------------------------
    # Line Math
    # ---------------------------------------------------------
    def point_side_of_line(self, x1, y1, x2, y2, px, py):
        return (x2 - x1) * (py - y1) - (y2 - y1) * (px - x1)

    def diagonal_crossed(self, x1, y1, x2, y2, old_cx, old_cy, new_cx, new_cy):
        old_side = self.point_side_of_line(x1, y1, x2, y2, old_cx, old_cy)
        new_side = self.point_side_of_line(x1, y1, x2, y2, new_cx, new_cy)

        EPS = 0.01

        # Both nearly on the line → no crossing
        if abs(old_side) < EPS and abs(new_side) < EPS:
            return False

        # Snap near-zero values to the other side
        if abs(old_side) < EPS:
            old_side = new_side
        if abs(new_side) < EPS:
            new_side = old_side

        return (old_side < 0 < new_side) or (old_side > 0 > new_side)

    def diagonal_blocked(self, x1, y1, x2, y2, cx, cy, orient):
        side = self.point_side_of_line(x1, y1, x2, y2, cx, cy)

        # On the line → treat as blocked
        if abs(side) < 0.001:
            return True

        if orient == "up_right":      # ↗ (block below)
            return side > 0

        if orient == "up_left":       # ↖ (block below)
            return side < 0

        if orient == "down_right":    # ↘ (block above)
            return side < 0

        if orient == "down_left":     # ↙ (block above)
            return side > 0

        return False

    def point_line_distance(self, x1, y1, x2, y2, px, py):
        dx, dy = x2 - x1, y2 - y1
        length_sq = dx * dx + dy * dy

        if length_sq == 0:
            return float("inf")

        t = ((px - x1) * dx + (py - y1) * dy) / length_sq
        t = max(0, min(1, t))

        cx = x1 + t * dx
        cy = y1 + t * dy

        return ((px - cx) ** 2 + (py - cy) ** 2) ** 0.5

    def project_point_onto_line(self, x1, y1, x2, y2, px, py):
        dx, dy = x2 - x1, y2 - y1
        length_sq = dx * dx + dy * dy

        if length_sq == 0:
            return x1, y1

        t = ((px - x1) * dx + (py - y1) * dy) / length_sq
        t = max(0, min(1, t))

        return x1 + t * dx, y1 + t * dy

    # ---------------------------------------------------------
    # Camera
    # ---------------------------------------------------------
    def set_camera(self, cx, cy):
        self.camera_x = cx
        self.camera_y = cy
