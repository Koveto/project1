import pygame
from constants import TARGET_FPS, SPEED, ACTUAL_WIDTH, ACTUAL_HEIGHT, ACTUAL_TILE_SIZE
from player import Player
from map import Map

# Import Pokédex subsystem using your real folder structure
from data.smt.pokedex.pokemon_controller import PokemonController
from data.smt.pokedex.pokemon_view import PokemonView


def test_collision_screen_bounds(map_obj, player, new_x, new_y):
    w, h = player.width, player.height

    if not map_obj.scrolling:
        if new_x < 0 or new_y < 0:
            return True
        if new_x + w > ACTUAL_WIDTH - ACTUAL_TILE_SIZE:
            return True
        if new_y + h > ACTUAL_HEIGHT - ACTUAL_TILE_SIZE:
            return True
        return False

    if new_x < 0 or new_y < 0:
        return True
    if new_x + w > map_obj.pixel_width:
        return True
    if new_y + h > map_obj.pixel_height:
        return True

    return False


def test_movement(map_obj, player, dx, dy):
    px, py = player.x, player.y
    w, h = player.width, player.height

    nx, ny = px + dx, py + dy
    if not (
        test_collision_screen_bounds(map_obj, player, nx, ny)
        or map_obj.test_collision_walls(px, py, nx, ny, w, h)
    ):
        return dx, dy

    allowed_dx = 0
    if dx != 0:
        nx = px + dx
        if not (
            test_collision_screen_bounds(map_obj, player, nx, py)
            or map_obj.test_collision_walls(px, py, nx, py, w, h)
        ):
            allowed_dx = dx

    allowed_dy = 0
    if dy != 0:
        ny = py + dy
        if not (
            test_collision_screen_bounds(map_obj, player, px, ny)
            or map_obj.test_collision_walls(px, py, px, ny, w, h)
        ):
            allowed_dy = dy

    if allowed_dx == 0 and dx != 0 and dy >= 0:
        slide_dy = SPEED
        nx, ny = px + dx, py + slide_dy

        if not (
            test_collision_screen_bounds(map_obj, player, nx, ny)
            or map_obj.test_collision_walls(px, py, nx, ny, w, h)
        ):
            allowed_dx = dx
            allowed_dy = slide_dy

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
    if not map_obj.scrolling:
        map_obj.camera_x = 0
        map_obj.camera_y = 0
        return

    half_w = screen_width // 2
    half_h = screen_height // 2

    cx = player.x - half_w
    cy = player.y - half_h

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

    # ---------------------------------------------------------
    # Overworld setup
    # ---------------------------------------------------------
    map_obj = Map("room0", screen_width, screen_height)

    player = Player(
        x=5 * ACTUAL_TILE_SIZE,
        y=5 * ACTUAL_TILE_SIZE
    )

    debug_walls_enabled = False

    # ---------------------------------------------------------
    # Pokédex subsystem setup
    # ---------------------------------------------------------
    pokedex_controller = PokemonController()
    pokedex_view = PokemonView(pokedex_controller)

    # ---------------------------------------------------------
    # Game state
    # ---------------------------------------------------------
    game_state = "overworld"

    running = True
    while running:

        # ---------------------------------------------------------
        # Event handling
        # ---------------------------------------------------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Toggle Pokédex
            if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                if game_state == "overworld":
                    game_state = "pokedex"
                elif game_state == "pokedex":
                    game_state = "overworld"
            # Toggle Battle
            if event.type == pygame.KEYDOWN and event.key == pygame.K_b:
                if game_state == "overworld":
                    game_state = "battle"
                elif game_state == "battle":
                    game_state = "overworld"

            # State-specific event handling
            if game_state == "pokedex":
                # 1. Navigation first
                from data.smt.pokedex.ui_navigation import handle_navigation
                handle_navigation(event, pokedex_controller, pokedex_view)

                # 2. Then text input / clicks
                pokedex_view.handle_event(event, pokedex_controller)

        # ---------------------------------------------------------
        # UPDATE LOGIC
        # ---------------------------------------------------------
        if game_state == "overworld":
            if game_state == "overworld":
                keys = pygame.key.get_pressed()
                dx, dy, direction, moving = player.handle_input(keys)
                player.direction = direction
            else:
                dx = dy = 0

            dx, dy = test_movement(map_obj, player, dx, dy)
            player.update(dx, dy, direction, moving)

            warp = map_obj.check_warp(player.x, player.y, player.width, player.height)
            if warp is not None:
                map_obj = Map(warp["to_room"], screen_width, screen_height)
                player.x = warp["dest_x"]
                player.y = warp["dest_y"]
                if warp.get("dest_facing") is not None:
                    player.direction = warp["dest_facing"]

            update_camera(map_obj, player, screen_width, screen_height)
        elif game_state == "battle":
            # No update logic yet — placeholder for future battle system
            pass


        # ---------------------------------------------------------
        # DRAWING
        # ---------------------------------------------------------
        screen.fill((0, 0, 0))

        if game_state == "overworld":
            map_obj.draw(screen, debug_walls_enabled)
            player.draw(screen, map_obj.camera_x, map_obj.camera_y)

        elif game_state == "pokedex":
            pokedex_view.draw(screen)

        elif game_state == "battle":
            # For now, just draw a blank screen (dark gray)
            screen.fill((40, 40, 40))


        pygame.display.flip()
        clock.tick(TARGET_FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
