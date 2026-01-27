from constants import *
from battle.battle_constants import *
import random
from battle.battle_text import (
    handle_scroll_skip,
    scroll_text_generic
)

def calculate_raw_damage(battle, move, affinity_value):
    """
    Returns the raw damage number for a move, before routing.
    No side effects. No HP changes. No text.
    """

    # Null tier → zero damage
    if AFFINITY_NULL <= affinity_value < AFFINITY_REFLECT:
        return 0

    # Otherwise, base damage = move power (placeholder)
    return move["power"]

def calculate_press_turns_consumed(battle, affinity):
    """
    Returns:
    - 1 for weakness (affinity < AFFINITY_NEUTRAL)
    - 2 for neutral (affinity == AFFINITY_NEUTRAL)
    - PRESS_TURN_WIPE for null or reflect
    """

    # Weakness → half turn
    if affinity < AFFINITY_NEUTRAL:
        return PRESS_TURN_HALF

    # Neutral → full turn
    if (affinity == AFFINITY_NEUTRAL) or \
        (AFFINITY_RESIST <= affinity < AFFINITY_NULL):
        return PRESS_TURN_FULL
    
    # Null or Reflect → wipe all remaining turns
    if affinity >= AFFINITY_NULL:
        return PRESS_TURN_WIPE

    # Fallback
    return PRESS_TURN_FULL

def determine_damage_recipient(battle, attacker, target, affinity_value):
    """
    Determines which Pokémon should receive the damage.
    Does not calculate the damage amount.
    Does not modify HP.
    """

    # Reflect → attacker takes the damage
    if affinity_value == AFFINITY_REFLECT:
        return attacker

    # Otherwise → target takes the damage
    return target

def handle_accuracy(battle, move, defender):
    acc = move.get("accuracy", 100)
    roll = random.randint(1, 100)
    if roll <= acc:
        return False

    # Missed
    battle.missed = True
    battle.damage_amount = 0
    battle.damage_amount = None  # preserve original quirk

    battle.damage_target = defender
    battle.damage_started = True
    battle.damage_animating = False
    battle.damage_done = True

    # Miss text
    battle.affinity_text = None
    battle.affinity_done = True
    battle.affinity_scroll_done = True

    battle.damage_text = "But it missed!"
    battle.damage_scroll_index = 0
    battle.damage_scroll_done = False

    battle.model.consume_miss()
    return True  # miss handled

def compute_affinity_after_damage(battle, attacker, defender, move):
    element = move["element"]
    element_index = ELEMENT_INDEX[element]
    affinity = defender.affinities[element_index]

    # Guarding override (enemy → player only)
    if defender.is_guarding and affinity < AFFINITY_NEUTRAL:
        affinity = AFFINITY_NEUTRAL

    defender.is_guarding = False
    return affinity

def reset_damage_flags(battle):
    battle.damage_started = False
    battle.damage_done = False
    battle.affinity_done = False
    battle.affinity_text = None

def tick_hp_animation(battle, damage_target):
    diff = damage_target.hp_anim - damage_target.hp_target
    step = max(1, int(diff ** TICK_CONSTANT))
    damage_target.hp_anim -= step

    if damage_target.hp_anim < damage_target.hp_target:
        damage_target.hp_anim = damage_target.hp_target

def animate_hp_bar(battle, is_player):
    damage_target = battle.damage_target

    # Continue HP animation
    if damage_target.hp_anim > damage_target.hp_target:
        tick_hp_animation(battle, damage_target)
        return

    # HP animation finished
    battle.damage_animating = False
    battle.damage_done = True

    # Only compute affinity text if the move hit
    if not getattr(battle, "missed", False):
        compute_affinity_text(battle, is_player)

    # Prepare damage text
    setup_damage_text(battle)
    return

def setup_damage_text(battle):
    battle.damage_text = f"Dealt {battle.damage_amount} damage."
    battle.damage_scroll_index = 0
    battle.damage_scroll_done = False

def compute_affinity_text(battle, is_player):
    # Reset affinity scroll state
    battle.affinity_done = False
    battle.affinity_scroll_done = False
    battle.affinity_text = None
    battle.affinity_scroll_index = 0

    # Determine move + defender
    if is_player:
        move = battle.smt_moves[battle.pending_move_name]
        defender = battle.model.enemy_team[battle.target_index]
    else:
        move = battle.smt_moves[battle.pending_enemy_move]
        defender = battle.model.player_team[battle.enemy_target_index]

    # Determine affinity
    element = move["element"]
    element_index = ELEMENT_INDEX[element]
    affinity = defender.affinities[element_index]

    # Guarding override (enemy → player only)
    if not is_player and defender.is_guarding and affinity < AFFINITY_NEUTRAL:
        affinity = AFFINITY_NEUTRAL

    # Select affinity text
    if affinity == 0:
        # Neutral affinity → skip scroll
        battle.affinity_text = None
        battle.affinity_done = True
        battle.affinity_scroll_done = True
    else:
        if affinity < AFFINITY_NEUTRAL:
            battle.affinity_text = AFFINITY_TEXT_WEAK
        elif AFFINITY_RESIST <= affinity < AFFINITY_NULL:
            battle.affinity_text = AFFINITY_TEXT_RESIST
        elif AFFINITY_NULL <= affinity < AFFINITY_REFLECT:
            battle.affinity_text = AFFINITY_TEXT_NULL
        elif affinity == AFFINITY_REFLECT:
            battle.affinity_text = AFFINITY_TEXT_REFLECT

        # Reset scroll state for non‑neutral affinity
        battle.affinity_scroll_index = 0
        battle.affinity_scroll_done = False

def handle_damaging_enemy_event(battle, event):

    if handle_scroll_skip(battle, event, "scroll_text", "scroll_index", "scroll_done"):
        return
    if not battle.damage_done:
        return
    if battle.affinity_text and not battle.affinity_done:
        if handle_scroll_skip(battle, event, "affinity_text", "affinity_scroll_index", "affinity_scroll_done"):
            return

        if key_confirm(event.key):
            finish_damage_phase(battle)
        return
    if key_confirm(event.key):
        finish_damage_phase(battle)
        return

def handle_enemy_damaging_event(battle, event):
    if event.type == pygame.KEYDOWN and key_confirm(event.key):
        if battle.enemy_waiting_for_confirm:
            battle.menu_mode = MENU_MODE_ENEMY_DAMAGE
            battle.damage_started = False
            battle.affinity_done = False
            battle.affinity_scroll_done = False
            battle.damage_animating = False
            return
        
def finish_damage_phase(battle):
    reset_damage_flags(battle)

    attacker = battle.model.get_active_pokemon()
    defender = battle.model.enemy_team[battle.target_index]
    move = battle.smt_moves[battle.pending_move_name]

    affinity = compute_affinity_after_damage(battle, attacker, defender, move)
    apply_press_turn_cost(battle, affinity)
    handle_side_switch(battle)

    battle.pending_move_name = None

    if battle.model.is_player_turn:
        battle.model.next_turn()

    battle.menu_mode = MENU_MODE_MAIN
    battle.menu_index = 0  

def finish_enemy_damage_phase(battle):
    reset_damage_flags(battle)

    attacker_index = get_current_enemy_attacker(battle)
    attacker = battle.model.enemy_team[attacker_index]
    defender = battle.model.player_team[battle.enemy_target_index]
    move = battle.smt_moves[battle.pending_enemy_move]

    affinity = compute_affinity_after_damage(battle, attacker, defender, move)
    apply_press_turn_cost(battle, affinity)
    handle_side_switch(battle)

    battle.pending_enemy_move = None

    if battle.model.is_player_turn:
        battle.menu_mode = MENU_MODE_MAIN
        battle.menu_index = 0
        return

    if battle.model.has_press_turns_left():
        battle.enemy_turn_index = (battle.enemy_turn_index + 1) % len(battle.enemy_turn_order)
        start_enemy_attack(battle)
        return

    # Safety fallback
    battle.model.next_side()
    battle.menu_mode = MENU_MODE_MAIN
    battle.menu_index = 0

def update_generic_damage_phase(battle, is_player=True):
    if is_player and not battle.scroll_done:
        if not battle.scroll_done:
            return scroll_text_generic(
                battle,
                text=battle.scroll_text,
                index_attr="scroll_index",
                done_attr="scroll_done"
            )

    
    if not battle.damage_started:
        return begin_damage_if_ready(battle, is_player)

    if battle.damage_animating:
        return animate_hp_bar(battle, is_player)

    # PHASE 3a — affinity scroll
    if battle.damage_done and not battle.affinity_done and battle.affinity_text:
        return scroll_text_generic(
            battle,
            text=battle.affinity_text,
            index_attr="affinity_scroll_index",
            done_attr="affinity_scroll_done",
            extra_done_attr="affinity_done"
        )

    # PHASE 3b — damage text scroll
    if battle.damage_done and not battle.damage_scroll_done:
        return scroll_text_generic(
            battle,
            text=battle.damage_text,
            index_attr="damage_scroll_index",
            done_attr="damage_scroll_done"
        )
    
def handle_damage_delay(battle):
    if not battle.delay_started:
        battle.delay_started = True
        battle.delay_frames = 0

    battle.delay_frames += 1
    if battle.delay_frames < WAIT_FRAMES_BEFORE_DAMAGE:
        return False

    # Start damage
    battle.delay_started = False
    battle.delay_frames = 0
    return True

def begin_damage_if_ready(battle, is_player):

    # PHASE 1.5 — wait for delay
    if not handle_damage_delay(battle):
        return

    # Select attacker, defender, move
    attacker, defender, move = select_combatants(battle, is_player)

    # Accuracy check (miss ends phase)
    if handle_accuracy(battle, move, defender):
        return

    # Compute damage, affinity, guarding, reflect, HP animation
    compute_and_apply_damage(battle, attacker, defender, move, is_player)
    return

def apply_press_turn_cost(battle, affinity):
    if not battle.missed:
        cost = calculate_press_turns_consumed(battle, affinity)
        battle.model.handle_action_press_turn_cost(cost)
    else:
        battle.missed = False  # reset for next action

def handle_side_switch(battle):
    if not battle.model.has_press_turns_left():
        battle.model.next_side()

def get_current_enemy_attacker(battle):
    return battle.enemy_turn_order[battle.enemy_turn_index]

def start_enemy_attack(battle):
    attacker_index = get_current_enemy_attacker(battle)
    attacker = battle.model.enemy_team[attacker_index]

    move_name = attacker.choose_random_move()
    target_index = battle.model.choose_random_player_target()

    return begin_enemy_action(battle, attacker_index, move_name, target_index)

def select_combatants(battle, is_player):
    if is_player:
        attacker = battle.model.get_active_pokemon()
        defender = battle.model.enemy_team[battle.target_index]
        move = battle.smt_moves[battle.pending_move_name]
    else:
        attacker = battle.model.enemy_team[battle.active_enemy_index]
        defender = battle.model.player_team[battle.enemy_target_index]
        move = battle.smt_moves[battle.pending_enemy_move]

    return attacker, defender, move

def compute_and_apply_damage(battle, attacker, defender, move, is_player):
    # Affinity
    element = move["element"]
    element_index = ELEMENT_INDEX[element]
    affinity = defender.affinities[element_index]

    # Crit (still no side effects)
    if move["type"] == "Physical":
        if random.random() < CRIT_CHANCE:
            print("CRITICAL HIT!")

    # Guarding override (enemy → player only)
    if not is_player and defender.is_guarding and affinity < AFFINITY_NEUTRAL:
        affinity = AFFINITY_NEUTRAL

    # Damage calculation
    battle.damage_amount = calculate_raw_damage(battle, move, affinity)

    # Reflect / redirect
    damage_target = determine_damage_recipient(battle, attacker, defender, affinity)

    # HP animation setup
    damage_target.hp_target = max(0, damage_target.remaining_hp - battle.damage_amount)
    damage_target.hp_anim = damage_target.remaining_hp

    damage_pixels = int((battle.damage_amount / damage_target.max_hp) * HP_BAR_WIDTH)
    damage_target.hp_anim_speed = max(1, min(12, damage_pixels // 4))

    damage_target.remaining_hp = damage_target.hp_target

    battle.damage_target = damage_target
    battle.damage_started = True
    battle.damage_animating = True

def handle_enemy_damage_event(battle, event):
    if event.type == pygame.KEYDOWN and key_confirm(event.key):
        if battle.damage_scroll_done:
            finish_enemy_damage_phase(battle)

def begin_enemy_action(battle, attacker_index, move_name, target_index):
    attacker = battle.model.enemy_team[attacker_index]

    # Sync active index
    battle.active_enemy_index = attacker_index

    # Store pending move + target
    battle.pending_enemy_move = move_name
    battle.enemy_target_index = target_index

    # Subtract MP
    move = battle.smt_moves[move_name]
    cost = move["mp"]
    attacker.remaining_mp = max(0, attacker.remaining_mp - cost)

    # Build announcement text
    target = battle.model.player_team[target_index]
    if move_name == "Attack":
        battle.scroll_text = f"{attacker.name} attacks {target.name}!"
    else:
        battle.scroll_text = f"{attacker.name} uses {move_name} on {target.name}!"

    # Reset scroll state
    battle.scroll_index = 0
    battle.scroll_done = False

    # Reset damage flags
    battle.damage_started = False
    battle.damage_done = False
    battle.affinity_text = None
    battle.affinity_done = False
    battle.affinity_scroll_index = 0
    battle.affinity_scroll_done = False

    # Enter announcement phase
    battle.menu_mode = MENU_MODE_DAMAGING_PLAYER
    battle.enemy_waiting_for_confirm = False

def start_enemy_turn(battle):
    # Enter announcement mode immediately
    battle.menu_mode = MENU_MODE_DAMAGING_PLAYER

    # Build SPD‑sorted order
    battle.enemy_turn_order = sorted(
        range(len(battle.model.enemy_team)),
        key=lambda i: battle.model.enemy_team[i].speed,
        reverse=True
    )
    battle.enemy_turn_index = 0

    attacker_index = battle.enemy_turn_order[battle.enemy_turn_index]
    attacker = battle.model.enemy_team[attacker_index]

    move_name = random.choice(attacker.moves)
    target_index = random.randrange(len(battle.model.player_team))

    return begin_enemy_action(battle, attacker_index, move_name, target_index)