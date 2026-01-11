import pygame
import os, sys

# Compute project root (3 levels up from pokedex/)
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(ROOT)


from ui_layout import WIDTH, HEIGHT
from pokemon_controller import PokemonController
from pokemon_view import PokemonView
from ui_navigation import handle_navigation


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Pokédex")

    clock = pygame.time.Clock()

    # Core objects
    controller = PokemonController()
    view = PokemonView(controller)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Delegate navigation to its own module
            handle_navigation(event, controller)

        # Draw everything
        screen.fill((40, 40, 40))
        view.draw(screen)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
