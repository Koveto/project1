import pygame
from constants import *
from battle.battle_constants import *
from battle.battle_text import start_text_mode
from battle.battle_damage import finish_buff_phase

def handle_main_menu_event(battle, event):
    battle.model.get_active_pokemon().is_guarding = False

    if event.key == pygame.K_RIGHT:
        return move_main_menu_cursor(battle, dx=1, dy=0)

    elif event.key == pygame.K_LEFT:
        return move_main_menu_cursor(battle, dx=-1, dy=0)

    elif event.key == pygame.K_DOWN:
        return move_main_menu_cursor(battle, dx=0, dy=1)

    elif event.key == pygame.K_UP:
        return move_main_menu_cursor(battle, dx=0, dy=-1)

    elif key_confirm(event.key):
        # SKILLS
        if battle.menu_mode == MENU_MODE_MAIN and battle.menu_index == MENU_INDEX_SKILLS:
            battle.menu_mode = MENU_MODE_SKILLS
            battle.previous_menu_index = battle.menu_index
            battle.menu_index = 0
            battle.skills_cursor = 0
            battle.skills_scroll = 0
            return
        
        # ITEM
        if battle.menu_mode == MENU_MODE_MAIN and battle.menu_index == MENU_INDEX_ITEMS:
            battle.menu_mode = MENU_MODE_ITEMS
            battle.item_cursor_x = 0
            battle.item_cursor_y = 0
            return

        # PASS
        if battle.menu_mode == MENU_MODE_MAIN and battle.menu_index == MENU_INDEX_PASS:
            battle.model.handle_action_press_turn_cost(PRESS_TURN_HALF)
            battle.model.next_turn()
            battle.menu_mode = MENU_MODE_MAIN
            battle.menu_index = MENU_INDEX_PASS
            return
        
        # GUARD
        if battle.menu_mode == MENU_MODE_MAIN and battle.menu_index == MENU_INDEX_GUARD:
            active = battle.model.get_active_player_pokemon()
            active.is_guarding = True
            return start_text_mode(battle, f"{active.name} guards!", MENU_MODE_GUARDING)

        # TALK
        if battle.menu_mode == MENU_MODE_MAIN and battle.menu_index == MENU_INDEX_TALK:
            return start_text_mode(battle, TALK_TEXT, MENU_MODE_TALK)

        # ESCAPE
        if battle.menu_mode == MENU_MODE_MAIN and battle.menu_index == MENU_INDEX_ESCAPE:
            return start_text_mode(battle, ESCAPE_TEXT, MENU_MODE_ESCAPE)

        
        if battle.menu_mode == MENU_MODE_MAIN and battle.menu_index == MENU_INDEX_INFO:
            battle.menu_mode = MENU_MODE_INFO
            return

        battle.previous_menu_index = battle.menu_index
        battle.menu_mode = MENU_MODE_SUBMENU

def handle_skills_menu_event(battle, event):
    if event.key == pygame.K_DOWN:
        return move_skill_cursor(battle, direction=1)

    elif event.key == pygame.K_UP:
        return move_skill_cursor(battle, direction=-1)

    elif key_confirm(event.key):
        pokemon = battle.model.get_active_pokemon()
        move_name = pokemon.moves[battle.skills_scroll + battle.skills_cursor]
        move = battle.smt_moves.get(move_name)

        if single_target_attack(battle, move, pokemon):
            battle.menu_mode = MENU_MODE_TARGET_SELECT
            return
        if single_ally_buff(battle, move, pokemon):
            battle.selected_ally = battle.model.turn_index
            battle.menu_mode = MENU_MODE_TARGET_BUFF
            return
        if all_ally_buff(battle, move, pokemon):
            start_player_all_buff_phase(battle)
            battle.menu_mode = MENU_MODE_BUFF_PLAYER_ALL

    elif key_back(event.key):
        battle.menu_mode = MENU_MODE_MAIN

def handle_target_select_event(battle, event):
    enemy_count = len(battle.model.enemy_team)

    # ----------------------------------------
    # LEFT / RIGHT: cycle enemy targets
    # ----------------------------------------
    if event.key == pygame.K_LEFT:
        if enemy_count > 0:
            battle.target_index = (battle.target_index - 1) % enemy_count
        return

    elif event.key == pygame.K_RIGHT:
        if enemy_count > 0:
            battle.target_index = (battle.target_index + 1) % enemy_count
        return

    # ----------------------------------------
    # CONFIRM: lock in move + target
    # ----------------------------------------
    elif key_confirm(event.key):
        return start_player_attack_phase(battle)

    # ----------------------------------------
    # BACK: return to skills menu
    # ----------------------------------------
    elif key_back(event.key):
        battle.menu_mode = MENU_MODE_SKILLS
        return
    
def handle_target_buff_event(battle, event):
    if event.type != pygame.KEYDOWN:
        return
    if key_back(event.key):
        battle.menu_mode = MENU_MODE_SKILLS
        return
    if event.key == pygame.K_LEFT:
        ally_count = len(battle.model.player_team)
        battle.selected_ally = (battle.selected_ally - 1) % ally_count
        return
    if event.key == pygame.K_RIGHT:
        ally_count = len(battle.model.player_team)
        battle.selected_ally = (battle.selected_ally + 1) % ally_count
        return
    if key_confirm(event.key):
        return start_player_buff_phase(battle)
    
def handle_items_event(battle, event):
        
    item_names = list(battle.model.inventory.keys())
    item_count = len(item_names)

    if event.key == pygame.K_LEFT:
        return move_item_cursor(battle, dx=-1, dy=0)

    elif event.key == pygame.K_RIGHT:
        return move_item_cursor(battle, dx=1, dy=0)

    elif event.key == pygame.K_UP:
        return move_item_cursor(battle, dx=0, dy=-1)

    elif event.key == pygame.K_DOWN:
        return move_item_cursor(battle, dx=0, dy=1)

    # BACK
    elif key_back(event.key):
        battle.menu_mode = MENU_MODE_MAIN
        battle.menu_index = MENU_INDEX_ITEMS
        return
    
    # CONFIRM
    elif key_confirm(event.key):
        index = battle.item_cursor_y * 3 + battle.item_cursor_x
        if index < item_count:
            item_name = item_names[index]
            battle.item_data = battle.model.smt_items[item_name]

            if battle.item_data["type"].startswith("heal_single"):
                return select_item(battle, item_name, battle.item_data, MENU_MODE_ITEM_ALLY_TARGET)

            if battle.item_data["type"].startswith("damage"):
                return select_item(battle, item_name, battle.item_data, MENU_MODE_ITEM_TARGET_SELECT)
            
def handle_item_ally_target_event(battle, event):
    if event.type != pygame.KEYDOWN:
        return
    if key_back(event.key):
        battle.menu_mode = MENU_MODE_ITEMS
        return
    if event.key == pygame.K_LEFT:
        ally_count = len(battle.model.player_team)
        battle.selected_ally = (battle.selected_ally - 1) % ally_count
        return
    if event.key == pygame.K_RIGHT:
        ally_count = len(battle.model.player_team)
        battle.selected_ally = (battle.selected_ally + 1) % ally_count
        return
    if key_confirm(event.key):
        # Build the scroll text
        user = battle.model.get_active_pokemon()
        return start_item_use_phase(battle, user.name, battle.pending_item_name)
    
def handle_item_target_select_event(battle, event):
    enemy_count = len(battle.model.enemy_team)

    if event.key == pygame.K_LEFT:
        if enemy_count > 0:
            battle.target_index = (battle.target_index - 1) % enemy_count

    elif event.key == pygame.K_RIGHT:
        if enemy_count > 0:
            battle.target_index = (battle.target_index + 1) % enemy_count

    elif key_confirm(event.key):
        return start_item_attack_phase(battle)

    elif key_back(event.key):
        battle.menu_mode = MENU_MODE_ITEMS
        return
    
def handle_info_event(battle, event):
    if key_back(event.key):
        battle.menu_mode = MENU_MODE_MAIN
    if event.key == pygame.K_LEFT:
        battle.info_col = (battle.info_col - 1) % 4
    if event.key == pygame.K_RIGHT:
        battle.info_col = (battle.info_col + 1) % 4
    if event.key == pygame.K_UP:
        battle.info_row = 0
    if event.key == pygame.K_DOWN:
        battle.info_row = 1

def handle_buff_player_event(battle, event):
    if key_confirm(event.key) and battle.scroll_done:
        finish_buff_phase(battle)

def handle_submenu_event(battle, event):
    if key_back(event.key):
        battle.menu_mode = MENU_MODE_MAIN

def move_main_menu_cursor(battle, dx, dy):
    row = battle.menu_index // 4
    col = battle.menu_index % 4

    new_row = (row + dy) % 2
    new_col = (col + dx) % 4

    battle.menu_index = new_row * 4 + new_col

def move_skill_cursor(battle, direction):
    """
    direction = +1 for DOWN, -1 for UP
    """
    moves = battle.model.get_active_pokemon().moves
    total = len(moves)

    # Moving down
    if direction == 1:
        if (battle.skills_cursor == 2) and \
            (battle.skills_scroll == total - 3):
            battle.skills_cursor = 0
            battle.skills_scroll = 0
            return

        # Case 1: Move cursor down within visible window
        if battle.skills_cursor < 2 and battle.skills_cursor < total - 1:
            battle.skills_cursor += 1
            return

        # Case 2: Scroll down if more moves exist below
        if battle.skills_scroll + 3 < total:
            battle.skills_scroll += 1
            return

        # Case 3: Fallback — move cursor if possible
        if battle.skills_cursor < 2:
            battle.skills_cursor += 1
            return

    # Moving up
    if direction == -1:
        if (battle.skills_cursor == 0) and \
            (battle.skills_scroll == 0):
            battle.skills_cursor = 2
            battle.skills_scroll = total - 3
            return

        # Case 1: Move cursor up within visible window
        if battle.skills_cursor > 0:
            battle.skills_cursor -= 1
            return

        # Case 2: Scroll up if possible
        if battle.skills_scroll > 0:
            battle.skills_scroll -= 1
            return

        # Case 3: Fallback — move cursor if possible
        if battle.skills_cursor > 0:
            battle.skills_cursor -= 1
            return
        
def single_target_attack(battle, move, pokemon):
    return (
        move["target"] == "Single" and
        move["type"] in ("Physical", "Special") and
        pokemon.remaining_mp >= move["mp"]
    )

def single_ally_buff(battle, move, pokemon):
    return (
        move["target"] == "Single" and
        move["type"] == "Support" and
        pokemon.remaining_mp >= move["mp"]
    )

def all_ally_buff(battle, move, pokemon):
    return (
        move["target"] == "All" and
        move["type"] == "Support" and
        pokemon.remaining_mp >= move["mp"]
    )

def start_player_buff_phase(battle):
    battle.menu_mode = MENU_MODE_BUFF_PLAYER
    active = battle.model.get_active_pokemon()
    move_name = active.moves[battle.skills_scroll + battle.skills_cursor]
    move = battle.smt_moves[move_name]
    ally = battle.model.get_player_team()[battle.selected_ally]
    if active.name == ally.name:
        battle.scroll_text = f"{active.name} uses {move_name}!"
    else:
        battle.scroll_text = f"{active.name} uses {move_name} on {ally.name}!"
    battle.scroll_text += " " + move["use_text"]
    active.remaining_mp = max(0, active.remaining_mp - move["mp"])
    for effect in move["effects"]:
        if effect == "+atk":
            if ally.attack_buff < 2:
                ally.attack_buff += 1
            ally.attack_buff_turns = 3
        if effect == "+def":
            if ally.defense_buff < 2:
                ally.defense_buff += 1
            ally.defense_buff_turns = 3
        if effect == "+spd":
            if ally.speed_buff < 2:
                ally.speed_buff += 1
            ally.speed_buff_turns = 3
    battle.scroll_index = 0
    battle.scroll_done = False

def start_player_all_buff_phase(battle):
    battle.menu_mode = MENU_MODE_BUFF_PLAYER_ALL
    active = battle.model.get_active_pokemon()
    move_name = active.moves[battle.skills_scroll + battle.skills_cursor]
    move = battle.smt_moves[move_name]
    battle.scroll_text = f"{active.name} uses {move_name}!"
    battle.scroll_text += " " + move["use_text"]
    active.remaining_mp = max(0, active.remaining_mp - move["mp"])
    for pkmn in battle.model.get_player_team():
        for effect in move["effects"]:
            if effect == "+atk":
                if pkmn.attack_buff < 2:
                    pkmn.attack_buff += 1
                pkmn.attack_buff_turns = 3
            if effect == "+def":
                if pkmn.defense_buff < 2:
                    pkmn.defense_buff += 1
                pkmn.defense_buff_turns = 3
            if effect == "+spd":
                if pkmn.speed_buff < 2:
                    pkmn.speed_buff += 1
                pkmn.speed_buff_turns = 3
    battle.scroll_index = 0
    battle.scroll_done = False

def start_player_attack_phase(battle):
    # Switch mode
    battle.menu_mode = MENU_MODE_DAMAGING_ENEMY

    # Determine move + target
    selected_index = battle.skills_scroll + battle.skills_cursor
    active = battle.model.get_active_pokemon()
    move_name = active.moves[selected_index]
    enemy = battle.model.enemy_team[battle.target_index]

    # Store pending move
    battle.pending_move_name = move_name

    # MP consumption
    move = battle.smt_moves[move_name]
    cost = move["mp"]
    active.remaining_mp = max(0, active.remaining_mp - cost)

    # Build announcement text
    if move_name == "Attack":
        battle.scroll_text = f"{active.name} attacks {enemy.name}!"
    else:
        battle.scroll_text = f"{active.name} uses {move_name} on {enemy.name}!"

    # Reset scroll state
    battle.scroll_index = 0
    battle.scroll_done = False

    # Reset damage state
    battle.damage_started = False
    battle.damage_done = False

    # Reset affinity state
    battle.affinity_text = None
    battle.affinity_done = False
    battle.affinity_scroll_index = 0
    battle.affinity_scroll_done = False

def move_item_cursor(battle, dx, dy):
    item_names = list(battle.model.inventory.keys())
    item_count = len(item_names)

    new_x = battle.item_cursor_x + dx
    new_y = battle.item_cursor_y + dy

    # Clamp to grid bounds (3 columns, 3 rows)
    new_x = max(0, min(2, new_x))
    new_y = max(0, min(2, new_y))

    # Convert to linear index
    new_index = new_y * 3 + new_x

    # Only move if the slot exists
    if new_index < item_count:
        battle.item_cursor_x = new_x
        battle.item_cursor_y = new_y

def select_item(battle, item_name, item_data, next_mode):
    battle.pending_item_name = item_name
    battle.pending_item_data = item_data
    battle.menu_mode = next_mode

def start_item_use_phase(battle, user_name, item_name):
    # Text scroll for "X uses Y!"
    battle.item_use_text = f"{user_name} uses {item_name}!"
    battle.item_use_scroll_index = 0
    battle.item_use_scroll_done = False

    # Heal animation state
    battle.item_heal_animating = False
    battle.item_heal_done = False

    # Recovery text (e.g., "Recovered 20 HP!")
    battle.item_recover_text = None
    battle.item_recover_scroll_index = 0
    battle.item_recover_scroll_done = False

    # Switch mode
    battle.menu_mode = MENU_MODE_ITEM_USE

def start_item_attack_phase(battle):
    # Consume the item
    battle.model.consume_item(battle.pending_item_name)

    # Switch to damage phase
    battle.menu_mode = MENU_MODE_DAMAGING_ENEMY

    # Determine move + target
    active = battle.model.get_active_pokemon()
    enemy = battle.model.enemy_team[battle.target_index]

    # Item type looks like "damage_fire", "damage_ice", etc.
    move_name = battle.pending_item_data["type"].split("damage_")[1]
    battle.pending_move_name = move_name

    # Announcement text
    battle.scroll_text = f"{active.name} uses {battle.pending_item_name}!"
    battle.scroll_index = 0
    battle.scroll_done = False

    # Reset damage state
    battle.damage_started = False
    battle.damage_done = False

    # Reset affinity state
    battle.affinity_text = None
    battle.affinity_done = False
    battle.affinity_scroll_index = 0
    battle.affinity_scroll_done = False