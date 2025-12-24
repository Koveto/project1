import json
import os
from PIL import Image, ImageTk


class Tileset:
    def __init__(self, name):
        self.name = name

        # Load metadata (tile size, sheet name,  etc.)
        meta = self.load_metadata(name)

        self.tile_width = meta["tile_width"]
        self.tile_height = meta["tile_height"]
        self.columns = meta["columns"]
        self.rows = meta["rows"]
        self.image_name = meta["image"]

        # Global scale factor for tiles
        self.scale = 4

        # Load the tilesheet image
        sheet = self.load_sheet(self.image_name)

        # Extract and scale all tiles
        self.tiles = self.extract_tiles(sheet)

    # ---------------------------------------------------------
    # Loading
    # ---------------------------------------------------------
    def load_metadata(self, name):
        """Load tileset metadata from JSON."""
        meta_path = os.path.join("data", "tilesets", f"{name}.json")
        with open(meta_path, "r") as f:
            return json.load(f)

    def load_sheet(self, image_name):
        """Load the tilesheet image."""
        image_path = os.path.join("data", "tilesets", image_name)
        return Image.open(image_path).convert("RGBA")

    # ---------------------------------------------------------
    # Tile Extraction
    # ---------------------------------------------------------
    def extract_tiles(self, sheet):
        """Cut the tilesheet into individual scaled tiles."""
        tiles = []
        for row in range(self.rows):
            for col in range(self.columns):
                tile = self.crop_tile(sheet, col, row)
                tile = self.scale_tile(tile)
                tiles.append(ImageTk.PhotoImage(tile))
        return tiles

    def crop_tile(self, sheet, col, row):
        """Extract a single tile from the sheet."""
        x = col * self.tile_width
        y = row * self.tile_height
        return sheet.crop((x, y, x + self.tile_width, y + self.tile_height))

    def scale_tile(self, tile):
        """Scale a tile using nearest-neighbor."""
        return tile.resize(
            (self.tile_width * self.scale, self.tile_height * self.scale),
            Image.NEAREST
        )

    # ---------------------------------------------------------
    # Access
    # ---------------------------------------------------------
    def get(self, tile_id):
        """Return the ImageTk tile for a given tile ID."""
        return self.tiles[tile_id]
