from constants import *
from battle.battle_constants import *
from data.smt.smt_items import SMT_ITEMS

# For clarity, these should be defined in battle_constants.py,
# but we’ll assume they are:
# SOLID = 2
# FLASH = 1
# NULL  = 0
# FRESH_PRESS_TURNS = [SOLID, SOLID, SOLID, SOLID]

class BattleModel:
    """
    Holds all data for a single battle instance.
    """

    def __init__(self, player_team, enemy_team):
        self.player_team = player_team      # list of Pokémon objects
        self.enemy_team = enemy_team        # list of Pokémon objects
        self.turn_index = 0

        self.smt_items = SMT_ITEMS
        self.inventory = {
            "Medicine": 2,
            "Bead": 1,
            "Fire Gem": 1,
            "Ice Gem": 1,
            "Elec Gem": 1,
            "Force Gem": 1,
            "Light Gem": 1,
            "Dark Gem": 1
        }

        # Press Turn system
        # IMPORTANT: always copy the template list
        self.press_turns = FRESH_PRESS_TURNS.copy()
        self.is_player_turn = True  # True = blue icons, False = red icons

    def update(self):
        pass

    def consume_item(self, item_name):
        if item_name in self.inventory:
            self.inventory[item_name] -= 1
            if self.inventory[item_name] <= 0:
                del self.inventory[item_name]


    def get_active_player_pokemon(self):
        return self.player_team[self.turn_index]

    def get_active_pokemon(self):
        # For now, only player side is implemented as active
        return self.player_team[self.turn_index]

    def next_turn(self):
        # Move to the next Pokémon on the player team
        self.turn_index = (self.turn_index + 1) % len(self.player_team)
        active = self.get_active_pokemon()
        active.is_guarding = False

    # -----------------------------
    # Press Turn core logic
    # -----------------------------

    def _consume_half_turn(self):
        """
        Half turn (cost = 1):
        - If any SOLID exists, convert the leftmost SOLID to FLASH.
        - Else, if any FLASH exists, convert the leftmost FLASH to NULL.
        """

        # First, try to downgrade a SOLID to FLASH
        for i in range(4):
            if self.press_turns[i] == SOLID:
                self.press_turns[i] = FLASH
                return

        # If no SOLID, downgrade a FLASH to NULL
        for i in range(4):
            if self.press_turns[i] == FLASH:
                self.press_turns[i] = NULL
                return

        # If no SOLID or FLASH, nothing to consume

    def _consume_full_turn(self):
        """
        Full turn (cost = 2):
        - Convert the leftmost non-NULL icon (SOLID or FLASH) to NULL.
        """

        for i in range(4):
            if self.press_turns[i] != NULL:
                self.press_turns[i] = NULL
                return

    def consume_press_turn(self, cost):
        """
        cost = 1 for half turn (weakness, pass)
        cost = 2 for full turn (neutral, guard, miss)
        """
        if cost == PRESS_TURN_HALF:
            self._consume_half_turn()
        elif cost == PRESS_TURN_FULL:
            self._consume_full_turn()
        else:
            # Safety: ignore invalid costs
            return
        
    def consume_miss(self):
        """
        SMT miss penalty:
        - First: consume one full turn (leftmost non-NULL → NULL)
        - Second: consume another icon, but FLASH behaves differently.
        """

        # --- First consumption: always full ---
        self._consume_full_turn()

        # --- Second consumption: special miss rule ---
        # Find the next non-NULL icon
        idx = None
        for i in range(4):
            if self.press_turns[i] != NULL:
                idx = i
                break

        if idx is None:
            return  # no icons left

        # If it's SOLID → NULL
        if self.press_turns[idx] == SOLID:
            self.press_turns[idx] = NULL
            return

        # If it's FLASH:
        # Check if there is another non-NULL after it
        for j in range(idx + 1, 4):
            if self.press_turns[j] != NULL:
                # There is another icon → FLASH becomes NULL
                self.press_turns[idx] = NULL
                return

        # If no non-NULL after it → leave FLASH as FLASH
        # (SMT rule: last FLASH survives)
        return


    def has_press_turns_left(self):
        return any(v > 0 for v in self.press_turns)

    def next_side(self):
        self.is_player_turn = not self.is_player_turn
        # Reset press turns for the new side
        self.press_turns = FRESH_PRESS_TURNS.copy()
        if self.is_player_turn:
            self.turn_index = 0

    def handle_action_press_turn_cost(self, cost):
        # Special case: wipe all remaining press turns
        if cost == PRESS_TURN_WIPE:
            self.press_turns = [NULL, NULL, NULL, NULL]
            self.next_side()
            return

        # Normal half/full turn consumption
        self.consume_press_turn(cost)

        if not self.has_press_turns_left():
            self.next_side()


    # -----------------------------
    # UI helpers
    # -----------------------------

    def get_press_turn_icon_states(self, anim_frame):
        """
        Returns a list of 4 states:
        'transparent', 'solid_blue', 'flash_blue',
        'solid_red', 'flash_red'
        """
        states = []
        color = "blue" if self.is_player_turn else "red"
        flashing_on = (anim_frame // 10) % 2 == 0

        for value in self.press_turns:
            if value == SOLID:
                states.append(f"solid_{color}")
            elif value == FLASH:
                # You can alternate between two flash sprites if you want,
                # but it should never be transparent.
                states.append(f"flash_{color}")
            else:
                states.append(PT_STATE_TRANSPARENT)

        return states
    
    def choose_random_player_target(self):
        """
        Returns a random *living* player Pokémon index.
        If all are KO'd (shouldn't happen), returns 0 as fallback.
        """
        import random

        living = [i for i, p in enumerate(self.player_team) if p.remaining_hp > 0]

        if not living:
            return 0

        return random.choice(living)


    # -----------------------------
    # Accessors
    # -----------------------------

    def get_player_team(self):
        return self.player_team

    def get_enemy_team(self):
        return self.enemy_team

    def get_turn_index(self):
        return self.turn_index

    def get_press_turns(self):
        return self.press_turns
