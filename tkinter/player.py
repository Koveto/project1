from PIL import Image, ImageTk
import os
from constants import SCALE


class Player:
    def __init__(self, canvas, x, y):
        self.canvas = canvas
        self.scale = SCALE

        # Load all animation frames
        self.frames = self.load_all_frames()

        # Animation state
        self.direction = "down"
        self.frame_index = 0
        self.step_counter = 0

        # Position
        self.x = x
        self.y = y

        # Sprite dimensions (after scaling)
        self.width = 15 * self.scale
        self.height = 21 * self.scale

        # Create sprite on canvas
        self.sprite = canvas.create_image(
            x, y,
            image=self.frames[self.direction][0],
            anchor="nw",
            tags=("player",)
        )


    # ---------------------------------------------------------
    # Sprite Loading
    # ---------------------------------------------------------
    def load_all_frames(self):
        """Load frames from a 4x3 spritesheet (player.png)."""

        sheet_path = os.path.join("sprites", "player.png")
        sheet = Image.open(sheet_path).convert("RGBA")

        frame_w = 15
        frame_h = 21

        scaled_w = frame_w * self.scale
        scaled_h = frame_h * self.scale

        directions = ["down", "up", "left", "right"]
        frames = {d: [] for d in directions}

        for col, direction in enumerate(directions):
            for row in range(3):
                x0 = col * frame_w
                y0 = row * frame_h
                x1 = x0 + frame_w
                y1 = y0 + frame_h

                frame = sheet.crop((x0, y0, x1, y1))

                # --- transparency cleanup for FF00E4 ---
                data = frame.getdata()
                cleaned = []
                for r, g, b, a in data:
                    if (r, g, b) == (255, 0, 228):  # FF00E4
                        cleaned.append((255, 0, 228, 0))
                    else:
                        cleaned.append((r, g, b, a))
                frame.putdata(cleaned)
                # ----------------------------------------

                frame = frame.resize((scaled_w, scaled_h), Image.NEAREST)
                frames[direction].append(ImageTk.PhotoImage(frame))

        return frames

    # ---------------------------------------------------------
    # Animation
    # ---------------------------------------------------------
    def animate(self):
        """Advance to the next animation frame."""
        cycle = [0, 1, 0, 2]
        self.frame_index = (self.frame_index + 1) % len(cycle)
        frame = cycle[self.frame_index]
        self.canvas.itemconfig(self.sprite, image=self.frames[self.direction][frame])

    def idle(self):
        """Show idle frame for current direction."""
        self.frame_index = 0
        self.canvas.itemconfig(self.sprite, image=self.frames[self.direction][0])

    # ---------------------------------------------------------
    # Movement
    # ---------------------------------------------------------
    def move(self, dx, dy):
        """Move the player and animate walking."""
        self.x += dx
        self.y += dy

        self.step_counter += 1
        if self.step_counter % 8 == 0:
            self.animate()

