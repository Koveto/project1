import pygame
from constants import *
from battle.battle_constants import *
from battle.battle_text import start_text_mode

def handle_main_menu_event(battle, event):
    battle.model.get_active_pokemon().is_guarding = False

    if event.key == pygame.K_RIGHT:
        return battle._move_main_menu_cursor(dx=1, dy=0)

    elif event.key == pygame.K_LEFT:
        return battle._move_main_menu_cursor(dx=-1, dy=0)

    elif event.key == pygame.K_DOWN:
        return battle._move_main_menu_cursor(dx=0, dy=1)

    elif event.key == pygame.K_UP:
        return battle._move_main_menu_cursor(dx=0, dy=-1)

    elif key_confirm(event.key):
        # SKILLS
        if battle.menu_mode == MENU_MODE_MAIN and battle.menu_index == MENU_INDEX_SKILLS:
            battle.menu_mode = MENU_MODE_SKILLS
            battle.previous_menu_index = battle.menu_index
            battle.menu_index = 0
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
        return battle._move_skill_cursor(direction=1)

    elif event.key == pygame.K_UP:
        return battle._move_skill_cursor(direction=-1)

    elif key_confirm(event.key):
        pokemon = battle.model.get_active_pokemon()
        selected_index = battle.skills_scroll + battle.skills_cursor
        move_name = pokemon.moves[selected_index]
        move = battle.smt_moves.get(move_name)

        if battle._can_select_skill(move, pokemon):
            battle.menu_mode = MENU_MODE_TARGET_SELECT
            return

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
        return battle._start_player_attack_phase()

    # ----------------------------------------
    # BACK: return to skills menu
    # ----------------------------------------
    elif key_back(event.key):
        battle.menu_mode = MENU_MODE_SKILLS
        return
    
def handle_items_event(battle, event):
        
    item_names = list(battle.model.inventory.keys())
    item_count = len(item_names)

    if event.key == pygame.K_LEFT:
        return battle._move_item_cursor(dx=-1, dy=0)

    elif event.key == pygame.K_RIGHT:
        return battle._move_item_cursor(dx=1, dy=0)

    elif event.key == pygame.K_UP:
        return battle._move_item_cursor(dx=0, dy=-1)

    elif event.key == pygame.K_DOWN:
        return battle._move_item_cursor(dx=0, dy=1)

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
            item_data = battle.model.smt_items[item_name]

            if item_data["type"].startswith("heal_single"):
                return battle._select_item(item_name, item_data, MENU_MODE_ITEM_INFO)

            if item_data["type"].startswith("damage"):
                return battle._select_item(item_name, item_data, MENU_MODE_ITEM_TARGET_SELECT)
            
def handle_item_info_event(battle, event):
    if event.type != pygame.KEYDOWN:
        return

    # BACK
    if key_back(event.key):
        battle.menu_mode = MENU_MODE_ITEMS
        return

    # LEFT
    if event.key == pygame.K_LEFT:
        ally_count = len(battle.model.player_team)
        battle.selected_ally = (battle.selected_ally - 1) % ally_count
        return

    # RIGHT
    if event.key == pygame.K_RIGHT:
        ally_count = len(battle.model.player_team)
        battle.selected_ally = (battle.selected_ally + 1) % ally_count
        return
    
    # CONFIRM
    if key_confirm(event.key):
        # Build the scroll text
        user = battle.model.get_active_pokemon()
        return battle._start_item_use_phase(user.name, battle.pending_item_name)
    
def handle_item_target_select_event(battle, event):
    enemy_count = len(battle.model.enemy_team)

    if event.key == pygame.K_LEFT:
        if enemy_count > 0:
            battle.target_index = (battle.target_index - 1) % enemy_count

    elif event.key == pygame.K_RIGHT:
        if enemy_count > 0:
            battle.target_index = (battle.target_index + 1) % enemy_count

    elif key_confirm(event.key):
        return battle._start_item_attack_phase()

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

def handle_submenu_event(battle, event):
    if key_back(event.key):
        battle.menu_mode = MENU_MODE_MAIN
