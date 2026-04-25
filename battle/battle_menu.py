from constants import *

from battle.battle_constants import *

def handle_event_main(b, event):
    if event.key == pygame.K_RIGHT:
        b.menu_cursor_x = (b.menu_cursor_x + 1) % 4
    elif event.key == pygame.K_LEFT:
        b.menu_cursor_x = (b.menu_cursor_x - 1) % 4
    elif event.key == pygame.K_DOWN:
        b.menu_cursor_y = 1 if b.menu_cursor_y == 0 else 0
    elif event.key == pygame.K_UP:
        b.menu_cursor_y = 0 if b.menu_cursor_y == 1 else 0

    if key_confirm(event.key):
        if  b.menu_cursor_x == MENU_CURSOR_SKILLS_X and \
            b.menu_cursor_y == MENU_CURSOR_SKILLS_Y:
            b.enter_state(STATE_SKILLS)

        if  b.menu_cursor_x == MENU_CURSOR_ITEMS_X and \
            b.menu_cursor_y == MENU_CURSOR_ITEMS_Y:
            b.enter_state(STATE_ITEMS)
            # ...


        if  b.menu_cursor_x == MENU_CURSOR_GUARD_X and \
            b.menu_cursor_y == MENU_CURSOR_GUARD_Y:
            b.enter_state(STATE_GUARD)
            # ...


        if  b.menu_cursor_x == MENU_CURSOR_TALK_X and \
            b.menu_cursor_y == MENU_CURSOR_TALK_Y:
            b.enter_state(STATE_TALK)
            # ...


        if  b.menu_cursor_x == MENU_CURSOR_CHANGE_X and \
            b.menu_cursor_y == MENU_CURSOR_CHANGE_Y:
            b.enter_state(STATE_CHANGE)
            # ...


        if  b.menu_cursor_x == MENU_CURSOR_ESCAPE_X and \
            b.menu_cursor_y == MENU_CURSOR_ESCAPE_Y:
            b.enter_state(STATE_ESCAPE)
            # ...


        if  b.menu_cursor_x == MENU_CURSOR_PASS_X and \
            b.menu_cursor_y == MENU_CURSOR_PASS_Y:
            # ...
            pass

        if  b.menu_cursor_x == MENU_CURSOR_INFO_X and \
            b.menu_cursor_y == MENU_CURSOR_INFO_Y:
            b.enter_state(STATE_INFO)
            # ...

def handle_event_skills(b, event):
    pkmn = b.player_team[b.turn_index]
    skill_list_length = len(pkmn.moves)
    if event.key == pygame.K_DOWN:
        if (b.menu_cursor_y == 2) and \
            (b.menu_scroll_y == skill_list_length - 3):
            b.menu_cursor_y = 0
            b.menu_scroll_y = 0
        elif b.menu_cursor_y < 2 and b.menu_cursor_y < skill_list_length - 1:
            b.menu_cursor_y += 1
        elif b.menu_scroll_y + 3 < skill_list_length:
            b.menu_scroll_y += 1
        elif b.menu_cursor_y < 2:
            b.menu_cursor_y += 1
    if event.key == pygame.K_UP:
        if (b.menu_cursor_y == 0) and \
            (b.menu_scroll_y == 0):
            b.menu_cursor_y = 2
            b.menu_scroll_y = skill_list_length - 3
        elif b.menu_cursor_y > 0:
            b.menu_cursor_y -= 1
        elif b.menu_scroll_y > 0:
            b.menu_scroll_y -= 1
        elif b.menu_cursor_y > 0:
            b.menu_cursor_y -= 1
    if key_confirm(event.key):
        move_name = pkmn.moves[b.menu_scroll_y + b.menu_cursor_y]
        move = b.moves.get(move_name)
        if not pkmn.remaining_mp >= move["mp"]:
            return
        if _single_target_attack(move):
            b.enter_state(STATE_SKILLS_TARGET_ENEMY)
            return
        # ...
    if key_back(event.key):
        b.enter_state(STATE_MAIN)
        
def _single_target_attack(move):
    return (
        move["target"] == "Single" and
        move["type"] in ("Physical", "Special")
    )