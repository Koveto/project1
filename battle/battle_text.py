from constants import *
from battle.battle_constants import *

def start_text_mode(battle, text, mode):
    battle.scroll_text = text
    battle.scroll_index = 0
    battle.scroll_done = False
    battle.menu_mode = mode

def handle_talk_event(battle, event):
    def finish():
        battle.menu_mode = MENU_MODE_MAIN
        battle.menu_index = MENU_INDEX_TALK
        battle.scroll_text = ""
        battle.scroll_index = 0
        battle.scroll_done = True

    return battle._handle_simple_scroll_event(
        event,
        confirm_keys=(pygame.K_z, pygame.K_RETURN, pygame.K_x),
        on_finish=finish
    )

def handle_escape_event(battle, event):
    def finish():
        battle.menu_mode = MENU_MODE_MAIN
        battle.menu_index = MENU_INDEX_ESCAPE
        battle.scroll_text = ""
        battle.scroll_index = 0
        battle.scroll_done = True

    return battle._handle_simple_scroll_event(
        event,
        confirm_keys=(pygame.K_z, pygame.K_RETURN, pygame.K_x),
        on_finish=finish
    )

def handle_guarding_event(battle, event):
    def finish():
        battle._finish_guard_phase()

    return battle._handle_simple_scroll_event(
        event,
        confirm_keys=(pygame.K_z, pygame.K_RETURN),  # or whatever key_confirm uses
        on_finish=finish
    )

def update_simple_scroll_phase(battle):
    if not battle.scroll_done:
        return scroll_text_generic(
            battle,
            text=battle.scroll_text,
            index_attr="scroll_index",
            done_attr="scroll_done"
        )

def scroll_text_generic(battle, text, index_attr, done_attr, extra_done_attr=None):
    chars_per_second = battle.scroll_delay * SCROLL_DELAY_CONSTANT
    chars_per_frame = chars_per_second / (SCROLL_CONSTANT * TARGET_FPS)

    # Increment index
    index = getattr(battle, index_attr)
    index += chars_per_frame

    # Clamp
    if int(index) >= len(text):
        index = len(text)
        setattr(battle, done_attr, True)
        if extra_done_attr:
            setattr(battle, extra_done_attr, True)

    setattr(battle, index_attr, index)
    return

def handle_scroll_skip(battle, event, text_attr, index_attr, done_attr):
    # If text is still scrolling
    if not getattr(battle, done_attr):
        if key_confirm(event.key):
            # Instantly finish the scroll
            setattr(battle, index_attr, len(getattr(battle, text_attr)))
            setattr(battle, done_attr, True)
        return True   # handled (still in scroll phase)

    return False      # scroll already done, caller should continue