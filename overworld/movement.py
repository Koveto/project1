# overworld/movement.py

from constants import SPEED, ACTUAL_WIDTH, ACTUAL_HEIGHT, ACTUAL_TILE_SIZE


# ---------------------------------------------------------
# Collision with screen boundaries
# ---------------------------------------------------------
def test_collision_screen_bounds(map_obj, player, new_x, new_y):
    """
    Prevents the player from walking off the visible screen
    when the map is not scrolling.
    """
    w, h = player.width, player.height

    # If the map does not scroll, clamp to screen size
    if not map_obj.scrolling:
        if new_x < 0 or new_y < 0:
            return True
        if new_x + w > ACTUAL_WIDTH - ACTUAL_TILE_SIZE:
            return True
        if new_y + h > ACTUAL_HEIGHT - ACTUAL_TILE_SIZE:
            return True
        return False

    # If the map scrolls, clamp to map pixel size
    if new_x < 0 or new_y < 0:
        return True
    if new_x + w > map_obj.pixel_width:
        return True
    if new_y + h > map_obj.pixel_height:
        return True

    return False


# ---------------------------------------------------------
# Movement + collision resolution
# ---------------------------------------------------------
def test_movement(map_obj, player, dx, dy):
    """
    Handles movement, collision with walls, and sliding behavior.
    This is your original logic, preserved exactly.
    """
    px, py = player.x, player.y
    w, h = player.width, player.height

    # First attempt: full movement
    nx, ny = px + dx, py + dy
    if not (
        test_collision_screen_bounds(map_obj, player, nx, ny)
        or map_obj.test_collision_walls(px, py, nx, ny, w, h)
    ):
        return dx, dy

    # Try horizontal only
    allowed_dx = 0
    if dx != 0:
        nx = px + dx
        if not (
            test_collision_screen_bounds(map_obj, player, nx, py)
            or map_obj.test_collision_walls(px, py, nx, py, w, h)
        ):
            allowed_dx = dx

    # Try vertical only
    allowed_dy = 0
    if dy != 0:
        ny = py + dy
        if not (
            test_collision_screen_bounds(map_obj, player, px, ny)
            or map_obj.test_collision_walls(px, py, px, ny, w, h)
        ):
            allowed_dy = dy

    # Sliding down along diagonal walls
    if allowed_dx == 0 and dx != 0 and dy >= 0:
        slide_dy = SPEED
        nx, ny = px + dx, py + slide_dy

        if not (
            test_collision_screen_bounds(map_obj, player, nx, ny)
            or map_obj.test_collision_walls(px, py, nx, ny, w, h)
        ):
            allowed_dx = dx
            allowed_dy = slide_dy

    # Sliding up along diagonal walls
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


# ---------------------------------------------------------
# Camera logic
# ---------------------------------------------------------
def update_camera(map_obj, player, screen_width, screen_height):
    """
    Centers the camera on the player, clamped to map bounds.
    """
    # If the map does not scroll, camera stays fixed
    if not map_obj.scrolling:
        map_obj.camera_x = 0
        map_obj.camera_y = 0
        return

    half_w = screen_width // 2
    half_h = screen_height // 2

    # Desired camera position
    cx = player.x - half_w
    cy = player.y - half_h

    # Clamp to map boundaries
    max_x = map_obj.pixel_width - screen_width
    max_y = map_obj.pixel_height - screen_height

    map_obj.camera_x = max(0, min(cx, max_x))
    map_obj.camera_y = max(0, min(cy, max_y))
