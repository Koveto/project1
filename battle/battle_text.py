from constants import *
from battle.battle_constants import *

def handle_event_scroll(b, event):
    if not b.scroll_done and key_confirm(event.key):
        b.scroll_index = len(b.scroll_text)
        b.scroll_done = True

def scroll_text_generic(b):
    chars_per_second = SCROLL_SPEED * SCROLL_DELAY_CONSTANT
    chars_per_frame = chars_per_second / (SCROLL_CONSTANT * TARGET_FPS)
    b.scroll_index += chars_per_frame
    if int(b.scroll_index) >= len(b.scroll_text):
        b.scroll_index = len(b.scroll_text)
        b.scroll_done = True
    return

def update_scroll(b):
    if not b.scroll_done:
        return scroll_text_generic(b)
    b.enter_state(b.next_state.pop())

def update_wait(b):
    if not b.delay_started:
        b.delay_started = True
        b.delay_frames = 0
    b.delay_frames += 1
    if b.delay_frames < b.delay_target:
        return
    b.delay_started = False
    b.delay_frames = 0
    b.delay_target = 0
    b.enter_state(b.next_state.pop())