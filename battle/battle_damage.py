from constants import *
from battle.battle_constants import *
"""
def handle_event_animate_enemy_hp(b, event):
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

def animate_hp(b, is_player=True):
    attacker = b.player_team[b.turn_index]
    defender = b.enemy_team[b.target_index]
    move = b.moves[b.pending_move_name]
    if _roll_accuracy(move):
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
        return
    
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

def _roll_accuracy(move):
    """
"""
    Rolls accuracy check.
    Returns true for miss
    -       false for hit
    """
"""
    acc = move.get("accuracy", 100)
    roll = random.randint(1, 100)
    return roll > acc
"""