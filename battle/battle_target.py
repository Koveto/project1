from constants import *

from battle.battle_constants import *

def handle_event_skills_target_enemy(b, event):
    if event.key == pygame.K_LEFT:
        b.target_index = (b.target_index - 1) % len(b.enemy_team)
        return
    elif event.key == pygame.K_RIGHT:
        b.target_index = (b.target_index + 1) % len(b.enemy_team)
        return
    elif key_confirm(event.key):
        b.enter_state(STATE_SCROLL)
        b.next_state.push(STATE_ANIMATE_ENEMY_HP)
        b.next_state.push(STATE_WAIT)
        pkmn = b.player_team[b.turn_index]
        target = b.enemy_team[b.target_index]
        b.pending_move_name = pkmn.moves[b.menu_cursor_y + b.menu_scroll_y]
        move = b.moves[b.pending_move_name]
        cost = move["mp"]
        pkmn.remaining_mp = max(0, pkmn.remaining_mp - cost)

        b.menu_cursor_y = 0
        b.menu_scroll_y = 0
        b.scroll_index = 0
        b.scroll_done = False
        b.delay_target = WAIT_FRAMES_BEFORE_DAMAGE
        b.delay_frames = 0
        b.delay_started = False

        if b.pending_move_name == "Attack":
            b.scroll_text = f"{pkmn.name} attacks {target.name}"
        else:
            b.scroll_text = f"{pkmn.name} uses {b.pending_move_name} on {target.name}!"

    elif key_back(event.key):
        b.enter_state(STATE_SKILLS)