from constants import *
from battle.battle_constants import *
import random
from battle.battle_text import (
    handle_scroll_skip,
    scroll_text_generic
)

# ===================================
# HELPERS (NO BATTLE)
# ===================================

def choose_enemy_move(moves):
    """
    For now, randomly choose move.
    """
    return random.choice(moves)

def calculate_raw_damage(move, affinity_value):
    """
    Returns raw damage value of move, 0 if immune.
    """
    if AFFINITY_NULL <= affinity_value < AFFINITY_REFLECT:
        return 0
    return move["power"]

def calculate_press_turns_consumed(affinity):
    """
    Returns:
    - PRESS_TURN_HALF for weakness (affinity < AFFINITY_NEUTRAL)
    - PRESS_TURN_FULL for neutral (affinity == AFFINITY_NEUTRAL)
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

def roll_accuracy(move):
    """
    Rolls accuracy check.
    Returns true for miss
    -       false for hit
    """
    acc = move.get("accuracy", 100)
    roll = random.randint(1, 100)
    return roll > acc

def tick_hp_animation(damage_target):
    diff = damage_target.hp_anim - damage_target.hp_target
    step = max(1, int(diff ** TICK_CONSTANT))
    damage_target.hp_anim -= step

    if damage_target.hp_anim < damage_target.hp_target:
        damage_target.hp_anim = damage_target.hp_target

def animate_hp_bar(damage_target):
    """
    Step of generic damage phase.
    Animates HP bar and prepares damage text.
    """
    # Continue HP animation
    if damage_target.hp_anim > damage_target.hp_target:
        tick_hp_animation(damage_target)
        return False
    return True

# ===================================
# HELPERS (W/ BATTLE)
# ===================================

def handle_miss(b, defender):
    """
    Upon miss, sets flags and consumes press turns.
    """

    b.missed = True
    b.damage_amount = None

    b.damage_target = defender
    b.damage_started = True
    b.damage_animating = False
    b.damage_done = True

    b.affinity_text = None
    b.affinity_done = True
    b.affinity_scroll_done = True

    b.crit_done = True
    b.crit_scroll_done = True
    b.affinity_confirm = True

    b.damage_text = "But it missed!"
    b.damage_scroll_index = 0
    b.damage_scroll_done = False

    b.model.consume_miss()
    return True

def reset_damage_flags(b):
    """
    Resets damaging flags for next turn.
    """
    b.damage_started = False
    b.damage_done = False
    b.affinity_done = False
    b.affinity_text = None
    b.crit_text = None
    b.crit_scroll_index = 0
    b.crit_done = False
    b.affinity_confirm = False

def compute_affinity_text(b, is_player):
    """
    Determines affinity and prepares text.
    """

    # Reset affinity scroll state
    b.affinity_done = False
    b.affinity_scroll_done = False
    b.affinity_text = None
    b.affinity_scroll_index = 0

    # Determine move + defender
    if is_player:
        move = b.smt_moves[b.pending_move_name]
        defender = b.model.enemy_team[b.target_index]
    else:
        move = b.smt_moves[b.pending_enemy_move]
        defender = b.model.player_team[b.enemy_target_index]

    # Determine affinity
    element = move["element"]
    element_index = ELEMENT_INDEX[element]
    affinity = defender.affinities[element_index]

    # Guarding override (enemy → player only)
    if not is_player and defender.is_guarding and affinity < AFFINITY_NEUTRAL:
        affinity = AFFINITY_NEUTRAL

    # Select affinity text
    if affinity == AFFINITY_NEUTRAL:
        # Neutral affinity → skip scroll
        b.affinity_text = None
        b.affinity_done = True
        b.affinity_scroll_done = True
    else:
        if affinity < AFFINITY_NEUTRAL:
            b.affinity_text = AFFINITY_TEXT_WEAK
        elif AFFINITY_RESIST <= affinity < AFFINITY_NULL:
            b.affinity_text = AFFINITY_TEXT_RESIST
        elif AFFINITY_NULL <= affinity < AFFINITY_REFLECT:
            b.affinity_text = AFFINITY_TEXT_NULL
        elif affinity == AFFINITY_REFLECT:
            b.affinity_text = AFFINITY_TEXT_REFLECT

        # Reset scroll state for non‑neutral affinity
        b.affinity_scroll_index = 0
        b.affinity_scroll_done = False

# ===================================
# PUBLIC FUNCTIONS
# ===================================
def handle_damaging_enemy_event(b, event):
    """
    battle_state.handle_event
    MENU_MODE_DAMAGING_ENEMY
    """

    if handle_scroll_skip(b, event, "scroll_text", "scroll_index", "scroll_done"):
        return
    if not b.damage_done:
        return
    if b.affinity_text and not b.affinity_done:
        if handle_scroll_skip(b, event, "affinity_text", "affinity_scroll_index", "affinity_scroll_done"):
            return
        return
    if b.is_crit and not b.affinity_confirm and key_confirm(event.key):
        b.affinity_confirm = True
        return
    if b.is_crit and b.affinity_done and not b.crit_done and b.affinity_confirm:
        if handle_scroll_skip(b, event, "crit_text", "crit_scroll_index", "crit_scroll_done"):
            return
        if key_confirm(event.key):
            finish_damage_phase(b)
        return
    if key_confirm(event.key):
        finish_damage_phase(b)

def handle_announce_enemy_attack_event(b, event):
    """
    battle_state.handle_event
    """
    if event.type == pygame.KEYDOWN and key_confirm(event.key):
        if b.enemy_waiting_for_confirm:
            b.menu_mode = MENU_MODE_ENEMY_DAMAGE
            b.damage_started = False
            b.affinity_done = False
            b.affinity_scroll_done = False
            b.damage_animating = False
            return
        
def finish_buff_phase(b):
    """
    battle_menu.handle_buff_player_event
    """
    b.model.handle_action_press_turn_cost(PRESS_TURN_FULL)
    handle_side_switch(b)
    b.pending_move_name = None
    if b.model.is_player_turn:
        b.model.next_turn()
    b.menu_mode = MENU_MODE_MAIN
    b.menu_index = MENU_INDEX_SKILLS 
        
def finish_damage_phase(b):
    reset_damage_flags(b)

    attacker = b.model.get_active_pokemon()
    defender = b.model.enemy_team[b.target_index]
    move = b.smt_moves[b.pending_move_name]

    element = move["element"]
    element_index = ELEMENT_INDEX[element]
    affinity = defender.affinities[element_index]

    # Guarding override (enemy → player only)
    if defender.is_guarding and affinity < AFFINITY_NEUTRAL:
        affinity = AFFINITY_NEUTRAL

    defender.is_guarding = False

    apply_press_turn_cost(b, affinity)
    b.is_crit = False
    handle_side_switch(b)

    b.pending_move_name = None

    if b.model.is_player_turn:
        b.model.next_turn()

    b.menu_mode = MENU_MODE_MAIN
    b.menu_index = MENU_INDEX_SKILLS 

def finish_enemy_damage_phase(b):
    reset_damage_flags(b)

    b.active_enemy_index = b.enemy_turn_order[b.enemy_turn_index]
    attacker = b.model.enemy_team[b.active_enemy_index]
    defender = b.model.player_team[b.enemy_target_index]
    move = b.smt_moves[b.pending_enemy_move]

    element = move["element"]
    element_index = ELEMENT_INDEX[element]
    affinity = defender.affinities[element_index]

    apply_press_turn_cost(b, affinity)
    b.is_crit = False
    handle_side_switch(b)

    b.pending_enemy_move = None

    if b.model.is_player_turn:
        b.menu_mode = MENU_MODE_MAIN
        b.menu_index = MENU_INDEX_SKILLS
        return

    if b.model.has_press_turns_left():
        b.enemy_turn_index = (b.enemy_turn_index + 1) % len(b.enemy_turn_order)
        announce_enemy_attack(b)
        return

    # Safety fallback
    b.model.next_side()
    b.menu_mode = MENU_MODE_MAIN
    b.menu_index = MENU_INDEX_SKILLS

def update_generic_damage_phase(b, is_player=True):
    if is_player and not b.scroll_done:
        if not b.scroll_done:
            return scroll_text_generic(
                b,
                text=b.scroll_text,
                index_attr="scroll_index",
                done_attr="scroll_done"
            )

    
    if not b.damage_started:
        return begin_damage_if_ready(b, is_player)

    if b.damage_animating:
        if b.damage_target.hp_anim > b.damage_target.hp_target:
            tick_hp_animation(b.damage_target)
            return
        else:
            # HP animation finished
            b.damage_animating = False
            b.damage_done = True
            # Only compute affinity text if the move hit
            if not b.missed:
                compute_affinity_text(b, is_player)
            b.damage_text = f"Dealt {b.damage_amount} damage."
            b.damage_scroll_index = 0
            b.damage_scroll_done = False
            return

    # PHASE 3a — affinity scroll
    if b.damage_done and not b.affinity_done and b.affinity_text:
        return scroll_text_generic(
            b,
            text=b.affinity_text,
            index_attr="affinity_scroll_index",
            done_attr="affinity_scroll_done",
            extra_done_attr="affinity_done"
        )

    # PHASE 3b — damage text scroll
    if b.damage_done and not b.damage_scroll_done:
        return scroll_text_generic(
            b,
            text=b.damage_text,
            index_attr="damage_scroll_index",
            done_attr="damage_scroll_done"
        )
    
    if b.is_crit and b.affinity_confirm and b.damage_done and not b.crit_scroll_done:
        scroll_text_generic(
            b,
            text=b.crit_text,
            index_attr="crit_scroll_index",
            done_attr="crit_scroll_done"
        )
        return
    
def handle_damage_delay(b):
    if not b.delay_started:
        b.delay_started = True
        b.delay_frames = 0

    b.delay_frames += 1
    if b.delay_frames < WAIT_FRAMES_BEFORE_DAMAGE:
        return False

    # Start damage
    b.delay_started = False
    b.delay_frames = 0
    return True

def begin_damage_if_ready(b, is_player):

    # wait for delay
    if not handle_damage_delay(b):
        return

    # Select attacker, defender, move
    attacker, defender, move = select_combatants(b, is_player)

    # Accuracy check
    if roll_accuracy(move):
        handle_miss(b, defender)
        return

    # Compute damage, affinity, guarding, reflect, HP animation
    compute_and_apply_damage(b, attacker, defender, move, is_player)
    return

def apply_press_turn_cost(b, affinity):
    if not b.missed:
        if b.is_crit:
            cost = PRESS_TURN_HALF
        else:
            cost = calculate_press_turns_consumed(affinity)
        b.model.handle_action_press_turn_cost(cost)
    else:
        b.missed = False  # reset for next action

def handle_side_switch(battle):
    if not battle.model.has_press_turns_left():
        battle.model.next_side()



def select_combatants(b, is_player):
    if is_player:
        attacker = b.model.get_active_pokemon()
        defender = b.model.enemy_team[b.target_index]
        move = b.smt_moves[b.pending_move_name]
    else:
        attacker = b.model.enemy_team[b.active_enemy_index]
        defender = b.model.player_team[b.enemy_target_index]
        move = b.smt_moves[b.pending_enemy_move]

    return attacker, defender, move

def compute_and_apply_damage(b, attacker, defender, move, is_player):
    # Affinity
    element = move["element"]
    element_index = ELEMENT_INDEX[element]
    affinity = defender.affinities[element_index]

    # Crit (still no side effects)
    if move["type"] == "Physical" and not b.is_crit:
        if random.random() < CRIT_CHANCE:
            b.is_crit = True
            b.crit_text = "A critical hit!"
            b.crit_scroll_done = False
            b.crit_scroll_index = 0

    # Guarding override (enemy → player only)
    if not is_player and defender.is_guarding and affinity < AFFINITY_NEUTRAL:
        affinity = AFFINITY_NEUTRAL

    # Damage calculation
    b.damage_amount = calculate_raw_damage(move, affinity)

    # Reflect / redirect
    damage_target = defender
    if affinity == AFFINITY_REFLECT:
        damage_target = attacker

    # HP animation setup
    damage_target.hp_target = max(0, damage_target.remaining_hp - b.damage_amount)
    damage_target.hp_anim = damage_target.remaining_hp

    damage_pixels = int((b.damage_amount / damage_target.max_hp) * HP_BAR_WIDTH)
    damage_target.hp_anim_speed = max(1, min(12, damage_pixels // 4))

    damage_target.remaining_hp = damage_target.hp_target

    b.damage_target = damage_target
    b.damage_started = True
    b.damage_animating = True

def handle_enemy_damage_event(b, event):
    if not b.affinity_confirm and b.damage_scroll_done and \
        event.type == pygame.KEYDOWN and key_confirm(event.key):
        b.affinity_confirm = True
        if not b.is_crit:
            finish_enemy_damage_phase(b)
        return
    if b.affinity_confirm and b.is_crit:
        if not key_confirm(event.key):
            return
    finish_enemy_damage_phase(b)

def start_enemy_turn(b):
    """
    Just changed turns! Sort speeds.
    """
    # Build SPD‑sorted order
    b.enemy_turn_order = sorted(
        range(len(b.model.enemy_team)),
        key=lambda i: b.model.enemy_team[i].speed,
        reverse=True
    )
    b.enemy_turn_index = 0
    return announce_enemy_attack(b)

def announce_enemy_attack(b):
    """
    Next attacker! Pick target and move.
    """
    b.active_enemy_index = b.enemy_turn_order[b.enemy_turn_index]
    b.attacker = b.model.enemy_team[b.active_enemy_index]
    b.pending_enemy_move = choose_enemy_move(b.attacker.moves)
    b.enemy_target_index = random.randrange(len(b.model.player_team))
    b.target = b.model.player_team[b.enemy_target_index]
    
    if b.pending_enemy_move == "Attack":
        b.scroll_text = f"{b.attacker.name} attacks {b.target.name}!"
    else:
        b.scroll_text = f"{b.attacker.name} uses {b.pending_enemy_move} on {b.target.name}!"

    # Reset scroll state
    b.scroll_index = 0
    b.scroll_done = False

    # Reset damage flags
    b.damage_started = False
    b.damage_done = False
    b.affinity_text = None
    b.affinity_done = False
    b.affinity_scroll_index = 0
    b.affinity_scroll_done = False

    # Enter announcement phase
    b.menu_mode = MENU_MODE_ANNOUNCE_ENEMY_ATTACK
    b.enemy_waiting_for_confirm = False