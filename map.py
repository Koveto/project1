import json
import os
from tileset import Tileset


class Map:
    def __init__(self, canvas, name):
        self.canvas = canvas
        self.name = name

        data = self.load_map_data(name)

        self.width = data["width"]
        self.height = data["height"]
        self.tiles = data["tiles"]

        # Keep scrolling flag if you still want camera maps
        self.scrolling = data.get("scrolling", True)
        self.walls = data.get("walls", [])

        self.tileset = self.load_tileset(data["tileset"])

        self.debug_wall_ids = []
        self.player_sprite_tag = "player"

        self.draw_map()

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
    def draw_map(self):
        """Draw all tiles to the canvas."""
        scaled_w = self.tileset.tile_width * self.tileset.scale
        scaled_h = self.tileset.tile_height * self.tileset.scale

        for y in range(self.height):
            for x in range(self.width):
                tile_id = self.tiles[y][x]
                img = self.tileset.get(tile_id)
                px = x * scaled_w
                py = y * scaled_h
                self.canvas.create_image(px, py, image=img, anchor="nw", tags="tile")

    def draw_debug_walls(self, enabled):
        # Remove old debug lines
        for line_id in self.debug_wall_ids:
            self.canvas.delete(line_id)
        self.debug_wall_ids.clear()

        if not enabled:
            return

        for wall in self.walls:
            x, y, length, orient = wall

            if orient == "h":
                # Horizontal wall (blocks vertical movement)
                line = self.canvas.create_line(
                    x, y, x + length, y,
                    fill="red",
                    width=2,
                    dash=(4, 2),
                    tags="debug_wall"
                )
            else:  # "v"
                # Vertical wall (blocks horizontal movement)
                line = self.canvas.create_line(
                    x, y, x, y + length,
                    fill="blue",
                    width=2,
                    dash=(4, 2),
                    tags="debug_wall"
                )

            self.debug_wall_ids.append(line)

        # Ensure walls draw below the player but above tiles
        self.canvas.tag_lower("debug_wall", self.player_sprite_tag)

    def draw_debug_walls(self, enabled):
        # Remove old debug lines
        for line_id in self.debug_wall_ids:
            self.canvas.delete(line_id)
        self.debug_wall_ids.clear()

        if not enabled:
            return

        for wall in self.walls:
            x, y, length, orient = wall

            # Compute endpoints for ANY wall type
            x1, y1, x2, y2 = self.compute_wall_endpoints(x, y, length, orient)

            # Pick a color based on orientation
            if orient in ("h", "v"):
                color = "red" if orient == "h" else "blue"
            else:
                # Diagonals get a different color
                color = "green"

            line = self.canvas.create_line(
                x1, y1, x2, y2,
                fill=color,
                width=2,
                dash=(4, 2),
                tags="debug_wall"
            )

            self.debug_wall_ids.append(line)

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
        """
        Returns True if movement from (old_x, old_y) to (new_x, new_y)
        collides with any wall.
        """

        # Player bounding boxes
        old_left   = old_x
        old_right  = old_x + w
        old_top    = old_y
        old_bottom = old_y + h

        new_left   = new_x
        new_right  = new_x + w
        new_top    = new_y
        new_bottom = new_y + h

        for wall in self.walls:
            wx, wy, length, orient = wall

            # -----------------------------------------------------
            # Horizontal wall: blocks vertical movement
            # -----------------------------------------------------
            if orient == "h":
                wall_x1 = wx
                wall_x2 = wx + length
                wall_y  = wy

                # Check horizontal overlap
                if new_right < wall_x1 or new_left > wall_x2:
                    continue  # no overlap

                # Moving DOWN across the wall
                if old_bottom <= wall_y < new_bottom:
                    return True

                # Moving UP across the wall
                if old_top >= wall_y > new_top:
                    return True

            # -----------------------------------------------------
            # Vertical wall: blocks horizontal movement
            # -----------------------------------------------------
            elif orient == "v":
                wall_y1 = wy
                wall_y2 = wy + length
                wall_x  = wx

                # Check vertical overlap
                if new_bottom < wall_y1 or new_top > wall_y2:
                    continue  # no overlap

                # Moving RIGHT across the wall
                if old_right <= wall_x < new_right:
                    return True

                # Moving LEFT across the wall
                if old_left >= wall_x > new_left:
                    return True
        
            # -----------------------------------------------------
            # Diagonal walls (45 degrees)
            # -----------------------------------------------------
            elif orient in ("up_right", "up_left", "down_left", "down_right"):
                x1, y1, x2, y2 = self.compute_wall_endpoints(wx, wy, length, orient)

                old_cx = old_x + w/2
                old_cy = old_y + h/2
                new_cx = new_x + w/2
                new_cy = new_y + h/2

                # Bounding box reject
                min_x = min(x1, x2)
                max_x = max(x1, x2)
                min_y = min(y1, y2)
                max_y = max(y1, y2)

                if new_cx < min_x or new_cx > max_x or new_cy < min_y or new_cy > max_y:
                    continue

                # Distance reject
                dist = self.point_line_distance(x1, y1, x2, y2, new_cx, new_cy)
                if dist > 4:
                    continue

                # Blocked side
                if self.diagonal_blocked(x1, y1, x2, y2, new_cx, new_cy, orient):
                    return True

                # Crossing
                if self.diagonal_crossed(x1, y1, x2, y2, old_cx, old_cy, new_cx, new_cy):
                    return True

        return False
    
    def compute_wall_endpoints(self, x, y, length, orient):
        # Horizontal
        if orient == "h":
            return x, y, x + length, y

        # Vertical
        if orient == "v":
            return x, y, x, y + length

        # Diagonal 45° directions
        if orient == "up_right":      # ↗
            return x, y, x + length, y - length

        if orient == "up_left":       # ↖
            return x, y, x - length, y - length

        if orient == "down_left":     # ↙
            return x, y, x - length, y + length

        if orient == "down_right":    # ↘
            return x, y, x + length, y + length

        # Fallback (should never happen)
        return x, y, x, y

    def point_side_of_line(self, x1, y1, x2, y2, px, py):
        return (x2 - x1) * (py - y1) - (y2 - y1) * (px - x1)
    
    def diagonal_crossed(self, x1, y1, x2, y2, old_cx, old_cy, new_cx, new_cy):
        old_side = self.point_side_of_line(x1, y1, x2, y2, old_cx, old_cy)
        new_side = self.point_side_of_line(x1, y1, x2, y2, new_cx, new_cy)

        EPS = 0.01  # small tolerance

        # If both sides are very close to zero, treat as no crossing
        if abs(old_side) < EPS and abs(new_side) < EPS:
            return False

        # If one side is near zero, treat it as the same sign as the other
        if abs(old_side) < EPS:
            old_side = new_side
        if abs(new_side) < EPS:
            new_side = old_side

        # Now check for sign change
        return (old_side < 0 and new_side > 0) or (old_side > 0 and new_side < 0)
    
    def diagonal_blocked(self, x1, y1, x2, y2, cx, cy, orient):
        side = self.point_side_of_line(x1, y1, x2, y2, cx, cy)

        # Treat exactly-on-the-line as blocked
        if abs(side) < 0.001:
            return True

        if orient == "up_right":
            return side > 0   # below diagonal is blocked

        if orient == "up_left":
            return side < 0   # below diagonal is blocked

        if orient == "down_right":
            return side < 0   # above diagonal is blocked

        if orient == "down_left":
            return side > 0   # above diagonal is blocked

        return False

    def point_line_distance(self, x1, y1, x2, y2, px, py):
        # Line segment length squared
        dx = x2 - x1
        dy = y2 - y1
        length_sq = dx*dx + dy*dy

        if length_sq == 0:
            return float('inf')

        # Project point onto the line segment
        t = ((px - x1)*dx + (py - y1)*dy) / length_sq
        t = max(0, min(1, t))

        # Closest point on the segment
        cx = x1 + t*dx
        cy = y1 + t*dy

        # Distance from P to closest point
        return ((px - cx)**2 + (py - cy)**2)**0.5
    
    def project_point_onto_line(self, x1, y1, x2, y2, px, py):
        dx = x2 - x1
        dy = y2 - y1
        length_sq = dx*dx + dy*dy

        if length_sq == 0:
            return x1, y1

        t = ((px - x1)*dx + (py - y1)*dy) / length_sq
        t = max(0, min(1, t))

        return x1 + t*dx, y1 + t*dy

