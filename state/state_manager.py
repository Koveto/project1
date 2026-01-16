# state/state_manager.py

class GameState:
    """
    Base class for all game states.
    Each state may override:
        - enter()
        - exit()
        - handle_event(event)
        - update()
        - draw(screen)
    """

    def enter(self):
        pass

    def exit(self):
        pass

    def handle_event(self, event):
        pass

    def update(self):
        pass

    def draw(self, screen):
        pass


class StateManager:
    """
    Holds all registered states and manages transitions.
    """

    def __init__(self):
        self.states = {}     # name → GameState instance
        self.current = None  # currently active state

    def register(self, name, state):
        """
        Register a state instance under a name.
        Example:
            state_manager.register("overworld", OverworldState(...))
        """
        self.states[name] = state

    def change(self, name):
        """
        Switch to a different registered state.
        Calls exit() on the old state and enter() on the new one.
        """
        if name not in self.states:
            raise ValueError(f"State '{name}' is not registered.")

        if self.current:
            self.current.exit()

        self.current = self.states[name]
        self.current.enter()

    def handle_event(self, event):
        """
        Forward events to the active state.
        """
        if self.current:
            self.current.handle_event(event)

    def update(self):
        """
        Update the active state.
        """
        if self.current:
            self.current.update()

    def draw(self, screen):
        """
        Draw the active state.
        """
        if self.current:
            self.current.draw(screen)
