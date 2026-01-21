from constants import *
from battle.battle_constants import *

class PressTurnRenderer:
    def __init__(self, press_turn_blue, press_turn_red):
        self.press_turn_blue = press_turn_blue
        self.press_turn_red = press_turn_red

    def draw_icon(self, screen, state, x, y, anim_frame):
        if state == PT_STATE_TRANSPARENT:
            return

        if state == PT_STATE_SOLIDBLUE:
            screen.blit(self.press_turn_blue, (x, y))
        elif state == PT_STATE_SOLIDRED:
            screen.blit(self.press_turn_red, (x, y))
        elif state == PT_STATE_FLASHBLUE:
            # Flashing: draw only on “on” frames
            if (anim_frame // PT_DURATION_FLASH) % 2 == 0:
                screen.blit(self.press_turn_blue, (x, y))
        elif state == PT_STATE_FLASHRED:
            if (anim_frame // PT_DURATION_FLASH) % 2 == 0:
                screen.blit(self.press_turn_red, (x, y))

    def draw_all(self, screen, press_turn_states, menu_mode, hp_offset, anim_frame):
        for i, state in enumerate(press_turn_states):
            x = PT_X + i * PT_SPACING
            y = PT_Y if menu_mode == MENU_MODE_DAMAGING_ENEMY else PT_Y + hp_offset
            self.draw_icon(screen, state, x, y, anim_frame)
