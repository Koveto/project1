import pygame

from constants import TARGET_FPS, ACTUAL_TILE_SIZE

# Overworld subsystem
from overworld.map import Map
from overworld.player import Player

# Pokédex subsystem
from pokedex.pokemon_controller import PokemonController
from pokedex.pokemon_view import PokemonView

# Battle subsystem
from battle.battle_background import load_battle_background

# State system
from state.state_manager import StateManager
from state.overworld_state import OverworldState
from state.pokedex_state import PokedexState
from state.battle_state import BattleState


def main():
    pygame.init()

    # ---------------------------------------------------------
    # Window setup
    # ---------------------------------------------------------
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
    # Pokédex setup
    # ---------------------------------------------------------
    pokedex_controller = PokemonController()
    pokedex_view = PokemonView(pokedex_controller)

    # ---------------------------------------------------------
    # Battle setup
    # ---------------------------------------------------------
    battle_background = load_battle_background(7)

    # ---------------------------------------------------------
    # State Manager + State Registration
    # ---------------------------------------------------------
    state_manager = StateManager()

    state_manager.register(
        "overworld",
        OverworldState(
            map_obj,
            player,
            screen_width,
            screen_height,
            debug_walls_enabled
        )
    )

    state_manager.register(
        "pokedex",
        PokedexState(
            pokedex_controller,
            pokedex_view
        )
    )

    state_manager.register(
        "battle",
        BattleState(
            battle_background
        )
    )

    # Start in overworld
    state_manager.change("overworld")

    # ---------------------------------------------------------
    # Main Loop
    # ---------------------------------------------------------
    running = True
    while running:

        # -----------------------------
        # Event Handling
        # -----------------------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Global state toggles
            if event.type == pygame.KEYDOWN:

                # Toggle Pokédex
                if event.key == pygame.K_p:
                    if state_manager.current is not state_manager.states["pokedex"]:
                        state_manager.change("pokedex")
                    else:
                        state_manager.change("overworld")

                # Toggle Battle
                elif event.key == pygame.K_b:
                    if state_manager.current is not state_manager.states["battle"]:
                        state_manager.change("battle")
                    else:
                        state_manager.change("overworld")

            # Pass event to active state
            state_manager.handle_event(event)

        # -----------------------------
        # Update + Draw
        # -----------------------------
        state_manager.update()
        state_manager.draw(screen)

        pygame.display.flip()
        clock.tick(TARGET_FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
