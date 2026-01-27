from constants import *
from battle.battle_constants import *

def handle_item_use_event(battle, event):

    if battle.item_recover_scroll_done and key_confirm(event.key):

        # 1. Consume the item
        battle.model.consume_item(battle.pending_item_name)

        # 2. Spend a full press turn
        battle.model.handle_action_press_turn_cost(PRESS_TURN_FULL)

        # 3. Advance to next turn
        battle.model.next_turn()

        # 4. Return to main battle menu
        battle.menu_mode = MENU_MODE_MAIN
        battle.menu_index = MENU_INDEX_ITEMS
        return
    
def update_item_use_phase(battle):
    # PHASE 1 — scroll "X uses Y!"
    if not battle.item_use_scroll_done:
        chars_per_second = battle.scroll_delay * 20
        chars_per_frame = chars_per_second / 60
        battle.item_use_scroll_index += chars_per_frame

        if int(battle.item_use_scroll_index) >= len(battle.item_use_text):
            battle.item_use_scroll_index = len(battle.item_use_text)
            battle.item_use_scroll_done = True

        return

    # PHASE 2 — apply healing ONCE, then start animating
    if not battle.item_heal_done and not battle.item_heal_animating:
        apply_item_healing(battle)
        return

    # PHASE 3 — animate HP rising
    if battle.item_heal_animating:
        ally = battle.model.player_team[battle.selected_ally]

        if ally.hp_anim < ally.hp_target:
            diff = ally.hp_target - ally.hp_anim
            step = max(1, int(diff ** 0.7))
            ally.hp_anim += step
            if ally.hp_anim > ally.hp_target:
                ally.hp_anim = ally.hp_target
            return

        # Animation finished
        battle.item_heal_animating = False
        battle.item_heal_done = True

        # Prepare "Recovered X HP!" text
        battle.item_recover_text = f"Recovered {battle.item_heal_amount} HP!"
        battle.item_recover_scroll_index = 0
        battle.item_recover_scroll_done = False
        return

    # PHASE 4 — scroll "Recovered X HP!"
    if battle.item_heal_done and not battle.item_recover_scroll_done:
        chars_per_second = battle.scroll_delay * 20
        chars_per_frame = chars_per_second / 60
        battle.item_recover_scroll_index += chars_per_frame

        if int(battle.item_recover_scroll_index) >= len(battle.item_recover_text):
            battle.item_recover_scroll_index = len(battle.item_recover_text)
            battle.item_recover_scroll_done = True

        return

    # PHASE 5 — wait for confirm (handled in input)
    return

def apply_item_healing(battle):
    item = battle.pending_item_data
    ally = battle.model.player_team[battle.selected_ally]

    # 1) Compute heal amount
    heal = compute_heal_amount(battle, ally, item)

    # 2) Apply heal + get old/new HP
    old_hp, new_hp = apply_heal_to_ally(battle, ally, heal)

    # 3) Set up animation
    setup_heal_animation(battle, ally, old_hp, new_hp)

def compute_heal_amount(battle, ally, item):
    heal_type = item["type"]
    amount = item["amount"]

    if heal_type == "heal_single_fixed":
        return amount

    if heal_type == "heal_single_percent":
        return int(ally.max_hp * (amount / 100))

    return 0

def setup_heal_animation(battle, ally, old_hp, new_hp):
    ally.hp_target = new_hp
    ally.hp_anim = old_hp

    heal_pixels = int(((new_hp - old_hp) / ally.max_hp) * HP_BAR_WIDTH)
    ally.hp_anim_speed = max(1, min(12, heal_pixels // 4))

    battle.item_heal_animating = True

def apply_heal_to_ally(battle, ally, heal):
    old_hp = ally.remaining_hp
    new_hp = min(old_hp + heal, ally.max_hp)

    # Store actual heal amount BEFORE animation
    battle.item_heal_amount = new_hp - old_hp

    # Apply healed HP
    ally.remaining_hp = new_hp

    return old_hp, new_hp