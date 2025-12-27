import pygame
import os

def load_player_frames(scale=4):
    sheet_path = os.path.join("sprites", "player.png")

    # Load with per‑pixel alpha so subsurfaces extract cleanly
    sheet = pygame.image.load(sheet_path).convert_alpha()

    frame_w = 15
    frame_h = 21

    scaled_w = frame_w * scale
    scaled_h = frame_h * scale

    directions = ["down", "up", "left", "right"]
    frames = {d: [] for d in directions}

    for col, direction in enumerate(directions):
        for row in range(3):
            x0 = col * frame_w
            y0 = row * frame_h

            # Extract frame from sheet
            frame = sheet.subsurface(pygame.Rect(x0, y0, frame_w, frame_h)).copy()

            # Convert to a format that supports colorkey transparency
            frame = frame.convert()

            # Apply colorkey using the exact RGBA value found in your sheet
            frame.set_colorkey((255, 0, 228, 255))

            # Scale the frame
            frame = pygame.transform.scale(frame, (scaled_w, scaled_h))

            frames[direction].append(frame)

    return frames
