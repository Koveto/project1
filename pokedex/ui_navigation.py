import pygame

def handle_navigation(event, controller, view):
    """
    Handle arrow-key navigation for the Pokédex.
    Disabled while the text input box is active.
    """

    # If typing in the input box, ignore navigation keys
    if view.input_active:
        return

    if event.type != pygame.KEYDOWN:
        return

    # Next Pokémon
    if event.key in (pygame.K_RIGHT, pygame.K_DOWN):
        controller.next()

    # Previous Pokémon
    elif event.key in (pygame.K_LEFT, pygame.K_UP):
        controller.prev()
