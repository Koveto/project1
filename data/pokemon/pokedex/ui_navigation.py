import pygame

def handle_navigation(event, controller):
    """
    Handle arrow-key navigation for the Pokédex.
    controller: PokemonController instance
    """

    if event.type != pygame.KEYDOWN:
        return

    # Next Pokémon
    if event.key in (pygame.K_RIGHT, pygame.K_DOWN):
        controller.next()

    # Previous Pokémon
    elif event.key in (pygame.K_LEFT, pygame.K_UP):
        controller.prev()
