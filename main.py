import pygame
from constants import TARGET_FPS, SPEED, ACTUAL_WIDTH, ACTUAL_HEIGHT, ACTUAL_TILE_SIZE
from player import Player
from map import Map


def test_collision_screen_bounds(map_obj, player, new_x, new_y):
    """
    Pygame version of Tkinter's screen-bound collision.
    Matches your Tkinter logic exactly.
    """

    w, h = player.width, player.height

    # Non-scrolling maps: clamp to screen
    if not map_obj.scrolling:
        if new_x < 0 or new_y < 0:
            return True
        if new_x + w > ACTUAL_WIDTH - ACTUAL_TILE_SIZE:
            return True
        if new_y + h > ACTUAL_HEIGHT - ACTUAL_TILE_SIZE:
            return True
        return False

    # Scrolling maps: clamp to MAP edges
    if new_x < 0 or new_y < 0:
        return True
    if new_x + w > map_obj.pixel_width:
        return True
    if new_y + h > map_obj.pixel_height:
        return True

    return False


def test_movement(map_obj, player, dx, dy):
    """
    Direct port of Tkinter Game.test_movement().
    """

    px, py = player.x, player.y
    w, h = player.width, player.height

    # --- 1. Try full movement ---------------------------------
    nx, ny = px + dx, py + dy
    if not (
        test_collision_screen_bounds(map_obj, player, nx, ny)
        or map_obj.test_collision_walls(px, py, nx, ny, w, h)
    ):
        return dx, dy

    # --- 2. Try X-only -----------------------------------------
    allowed_dx = 0
    if dx != 0:
        nx = px + dx
        if not (
            test_collision_screen_bounds(map_obj, player, nx, py)
            or map_obj.test_collision_walls(px, py, nx, py, w, h)
        ):
            allowed_dx = dx

    # --- 3. Try Y-only -----------------------------------------
    allowed_dy = 0
    if dy != 0:
        ny = py + dy
        if not (
            test_collision_screen_bounds(map_obj, player, px, ny)
            or map_obj.test_collision_walls(px, py, px, ny, w, h)
        ):
            allowed_dy = dy

    # --- 4. Horizontal blocked → try sliding DOWN a diagonal ---
    if allowed_dx == 0 and dx != 0 and dy >= 0:
        slide_dy = SPEED
        nx, ny = px + dx, py + slide_dy

        if not (
            test_collision_screen_bounds(map_obj, player, nx, ny)
            or map_obj.test_collision_walls(px, py, nx, ny, w, h)
        ):
            allowed_dx = dx
            allowed_dy = slide_dy

    # --- 5. Vertical blocked → try sliding UP a diagonal -------
    if allowed_dy == 0 and dy < 0 and allowed_dx == 0:
        for wx, wy, length, orient in map_obj.walls:

            if orient == "up_right":
                slide_dx = SPEED
            elif orient == "up_left":
                slide_dx = -SPEED
            else:
                continue

            nx, ny = px + slide_dx, py + dy

            if not map_obj.test_collision_walls(
                px, py, nx, ny, w, h,
                ignore_vertical_walls=True
            ):
                allowed_dx = slide_dx
                allowed_dy = dy
                break

    return allowed_dx, allowed_dy


def update_camera(map_obj, player, screen_width, screen_height):
    """
    Pygame version of Tkinter's update_camera().
    """

    if not map_obj.scrolling:
        map_obj.camera_x = 0
        map_obj.camera_y = 0
        return

    half_w = screen_width // 2
    half_h = screen_height // 2

    cx = player.x - half_w
    cy = player.y - half_h

    # Clamp camera to map bounds
    max_x = map_obj.pixel_width - screen_width
    max_y = map_obj.pixel_height - screen_height

    map_obj.camera_x = max(0, min(cx, max_x))
    map_obj.camera_y = max(0, min(cy, max_y))


def main():
    pygame.init()

    screen_width = 896
    screen_height = 576
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("PyPokemon (Pygame)")

    clock = pygame.time.Clock()

    # Load map
    map_obj = Map("room0", screen_width, screen_height)

    # Create player at a starting world position
    player = Player(
        x=5 * ACTUAL_TILE_SIZE,
        y=5 * ACTUAL_TILE_SIZE
    )

    debug_walls_enabled = False

    running = True
    while running:
        # ---------------------------------------------------------
        # Event handling
        # ---------------------------------------------------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    debug_walls_enabled = not debug_walls_enabled

        # ---------------------------------------------------------
        # Input (Tkinter-style priority)
        # ---------------------------------------------------------
        keys = pygame.key.get_pressed()
        dx, dy, direction, moving = player.handle_input(keys)
        player.direction = direction

        # ---------------------------------------------------------
        # Update player (movement + animation)
        # ---------------------------------------------------------
        # 1. resolve movement first
        dx, dy = test_movement(map_obj, player, dx, dy)

        # 2. THEN update player position + animation
        player.update(dx, dy, direction, moving)

        # 2.5. Check warps after movement
        warp = map_obj.check_warp(player.x, player.y, player.width, player.height)
        if warp is not None:
            # Load new map
            map_obj = Map(warp["to_room"], screen_width, screen_height)

            # Place player
            player.x = warp["dest_x"]
            player.y = warp["dest_y"]
            if warp.get("dest_facing") is not None:
                player.direction = warp["dest_facing"]


        # ---------------------------------------------------------
        # Camera update
        # ---------------------------------------------------------
        update_camera(map_obj, player, screen_width, screen_height)

        # ---------------------------------------------------------
        # Drawing
        # ---------------------------------------------------------
        screen.fill((0, 0, 0))

        # Draw map tiles
        map_obj.draw(screen, debug_walls_enabled)

        # Draw player relative to camera
        player.draw(screen, map_obj.camera_x, map_obj.camera_y)

        pygame.display.flip()

        # ---------------------------------------------------------
        # Frame timing (fixed 30 FPS)
        # ---------------------------------------------------------
        clock.tick(TARGET_FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
