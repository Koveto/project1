import json
import os
import pygame
from PIL import Image


class Tileset:
    def __init__(self, name):
        self.name = name

        # Load metadata (tile size, sheet name, etc.)
        meta = self.load_metadata(name)

        self.tile_width = meta["tile_width"]
        self.tile_height = meta["tile_height"]
        self.columns = meta["columns"]
        self.rows = meta["rows"]
        self.image_name = meta["image"]

        # Global scale factor for tiles
        self.scale = meta.get("scale", 4)

        # Load the tilesheet image (PIL)
        self.sheet = self.load_sheet(self.image_name)

        # Preload + cache all tiles as pygame.Surface
        self.cache = {}
        self.load_all_tiles()

    # ---------------------------------------------------------
    # Loading
    # ---------------------------------------------------------
    def load_metadata(self, name):
        """Load tileset metadata from JSON."""
        meta_path = os.path.join("data", "tilesets", f"{name}.json")
        with open(meta_path, "r") as f:
            return json.load(f)

    def load_sheet(self, image_name):
        """Load the tilesheet image using PIL."""
        image_path = os.path.join("data", "tilesets", image_name)
        return Image.open(image_path).convert("RGBA")

    # ---------------------------------------------------------
    # Tile Extraction + Caching
    # ---------------------------------------------------------
    def load_all_tiles(self):
        """Slice, scale, and cache every tile as a pygame.Surface."""
        tw = self.tile_width
        th = self.tile_height
        sw = tw * self.scale
        sh = th * self.scale

        tile_id = 0

        for row in range(self.rows):
            for col in range(self.columns):
                x = col * tw
                y = row * th

                # Crop tile (PIL)
                tile = self.sheet.crop((x, y, x + tw, y + th))

                # Scale tile (PIL)
                tile = tile.resize((sw, sh), Image.NEAREST)

                # Convert PIL → pygame.Surface
                mode = tile.mode
                size = tile.size
                data = tile.tobytes()

                if mode == "RGBA":
                    surface = pygame.image.fromstring(data, size, mode).convert_alpha()
                else:
                    surface = pygame.image.fromstring(data, size, mode).convert()

                # Store in cache
                self.cache[tile_id] = surface
                tile_id += 1

    # ---------------------------------------------------------
    # Access
    # ---------------------------------------------------------
    def get(self, tile_id):
        """Return a cached pygame.Surface tile."""
        return self.cache[tile_id]
