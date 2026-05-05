# state/battle_state_new.py
from constants import *
from stack import Stack
from state.state_manager import GameState

from data.smt.smt_stats import load_pkmn_from_json, create_pokemon_from_species, get_species_by_number
from data.smt.smt_moves import load_moves
from data.smt.smt_items import SMT_ITEMS
from pokedex.pokemon import Pokemon

from battle.battle_constants import *
from battle.battle_renderer import BattleRenderer

class BattleState(GameState):
    def __init__(self):
        # ========================= START INIT =================================
        self.pkmn = load_pkmn_from_json(FILENAME_STATS)
        self.moves = load_moves(FILENAME_MOVES)
        self.items = SMT_ITEMS

        self._init_teams()
        # player/enemy_team[ turn_index ] is active
        self.turn_index = 0 
        # [2, 2, 2, 2] where 2 is fresh, 1 blinking, 0 gone
        self.press_turns = FRESH_PRESS_TURNS.copy()
        self.is_player_turn = True

        self.inventory = {
            "Medicine": 2,
            "Bead": 1,
            "Fire Gem": 1,
            "Ice Gem": 1,
            "Elec Gem": 1,
            "Force Gem": 1,
            "Light Gem": 1,
            "Dark Gem": 1
        }

        self.state = None
        self.pending_state = None
        self.enter_state(STATE_MAIN)

        self.background    = random.choice([BACKGROUND_GRASS_1,
                                            BACKGROUND_WATER_1,
                                            BACKGROUND_CAVE_1,
                                            BACKGROUND_BRICK_1,
                                            BACKGROUND_GRASS_2,
                                            BACKGROUND_WATER_2,
                                            BACKGROUND_CAVE_2,
                                            BACKGROUND_BRICK_2,
                                            BACKGROUND_GRASS_3,
                                            BACKGROUND_CAVE_3,
                                            BACKGROUND_BRICK_4,
                                            BACKGROUND_BRICK_5,
                                            BACKGROUND_WATER_3,
                                            BACKGROUND_CAVE_4,
                                            BACKGROUND_BRICK_6])

        self.renderer = BattleRenderer(self)
        # ========================= END INIT =================================
    
    def draw(self, screen):
        self.renderer.draw(self, screen)

    def handle_event(self, event):
        # ========================= START HANDLE_EVENT =================================
        if event.type != pygame.KEYDOWN:
            return
        if self.state == STATE_MAIN:
            if event.key == pygame.K_RIGHT:
                self.menu_cursor_x = (self.menu_cursor_x + 1) % 4
            elif event.key == pygame.K_LEFT:
                self.menu_cursor_x = (self.menu_cursor_x - 1) % 4
            elif event.key == pygame.K_DOWN:
                self.menu_cursor_y = 1 if self.menu_cursor_y == 0 else 0
            elif event.key == pygame.K_UP:
                self.menu_cursor_y = 0 if self.menu_cursor_y == 1 else 0

            if key_confirm(event.key):
                if  self.menu_cursor_x == MENU_CURSOR_SKILLS_X and \
                    self.menu_cursor_y == MENU_CURSOR_SKILLS_Y:
                    self.enter_state(STATE_SKILLS)

                if  self.menu_cursor_x == MENU_CURSOR_ITEMS_X and \
                    self.menu_cursor_y == MENU_CURSOR_ITEMS_Y:
                    self.enter_state(STATE_ITEMS)
                    # ...


                if  self.menu_cursor_x == MENU_CURSOR_GUARD_X and \
                    self.menu_cursor_y == MENU_CURSOR_GUARD_Y:
                    pkmn = self.player_team[self.turn_index]
                    pkmn.is_guarding = True
                    self._consume_full_turn()
                    self.next_state.push(STATE_COMPLETE_PLAYER_TURN)
                    self.next_text.push((f"{pkmn.name} guards!",
                                         True,
                                         False,
                                         False,
                                         False,
                                         False))
                    self.enter_state(STATE_SCROLL)


                if  self.menu_cursor_x == MENU_CURSOR_TALK_X and \
                    self.menu_cursor_y == MENU_CURSOR_TALK_Y:
                    self.next_state.push(STATE_MAIN)
                    self.next_text.push(("Foes are crazed for battle! Words can't get through.",
                                         True,
                                         False,
                                         False,
                                         False,
                                         False))
                    self.enter_state(STATE_SCROLL)


                if  self.menu_cursor_x == MENU_CURSOR_CHANGE_X and \
                    self.menu_cursor_y == MENU_CURSOR_CHANGE_Y:
                    self.next_state.push(STATE_MAIN)
                    self.next_text.push(("Can't change!",
                                         True,
                                         False,
                                         False,
                                         False,
                                         False))
                    self.enter_state(STATE_SCROLL)


                if  self.menu_cursor_x == MENU_CURSOR_ESCAPE_X and \
                    self.menu_cursor_y == MENU_CURSOR_ESCAPE_Y:
                    self.next_state.push(STATE_MAIN)
                    self.next_text.push(("You are unable to escape!",
                                         True,
                                         False,
                                         False,
                                         False,
                                         False))
                    self.enter_state(STATE_SCROLL)


                if  self.menu_cursor_x == MENU_CURSOR_PASS_X and \
                    self.menu_cursor_y == MENU_CURSOR_PASS_Y:
                    self._consume_half_turn()
                    self.enter_state(STATE_COMPLETE_PLAYER_TURN)


                if  self.menu_cursor_x == MENU_CURSOR_INFO_X and \
                    self.menu_cursor_y == MENU_CURSOR_INFO_Y:
                    self.enter_state(STATE_INFO)
                    # ...


        elif self.state == STATE_SKILLS:
            pkmn = self.player_team[self.turn_index]
            skill_list_length = len(pkmn.moves)
            if event.key == pygame.K_DOWN:
                if (self.skills_cursor == 2) and \
                    (self.skills_scroll == skill_list_length - 3):
                    self.skills_cursor = 0
                    self.skills_scroll = 0
                elif self.skills_cursor < 2 and self.skills_cursor < skill_list_length - 1:
                    self.skills_cursor += 1
                elif self.skills_scroll + 3 < skill_list_length:
                    self.skills_scroll += 1
                elif self.skills_cursor < 2:
                    self.skills_cursor += 1
            if event.key == pygame.K_UP:
                if (self.skills_cursor == 0) and \
                    (self.skills_scroll == 0):
                    self.skills_cursor = 2
                    self.skills_scroll = skill_list_length - 3
                elif self.skills_cursor > 0:
                    self.skills_cursor -= 1
                elif self.skills_scroll > 0:
                    self.skills_scroll -= 1
                elif self.skills_cursor > 0:
                    self.skills_cursor -= 1
            if key_confirm(event.key):
                move_name = pkmn.moves[self.skills_scroll + self.skills_cursor]
                move = self.moves.get(move_name)
                if not pkmn.remaining_mp >= move["mp"]:
                    return
                if (move["target"] == "Single" and
                    move["type"] in ("Physical", "Special")):
                    self.enter_state(STATE_PLAYER_SINGLE_TARGET_TARGET)
                    return
                # ...
            if key_back(event.key):
                self.enter_state(STATE_MAIN)


        elif self.state == STATE_PLAYER_SINGLE_TARGET_TARGET:
            if event.key == pygame.K_LEFT:
                self.target_index = (self.target_index - 1) % len(self.enemy_team)
                return
            elif event.key == pygame.K_RIGHT:
                self.target_index = (self.target_index + 1) % len(self.enemy_team)
                return
            elif key_confirm(event.key):
                self.enter_state(STATE_PLAYER_SINGLE_TARGET_CALC)
            elif key_back(event.key):
                self.enter_state(STATE_SKILLS)


        elif self.state == STATE_SCROLL:
            if not self.scroll_is_done and key_confirm(event.key):
                self.scroll_index = len(self.scroll_text)
                self.scroll_is_done = True
            if self.scroll_is_done and \
                key_confirm(event.key) and \
                    self.scroll_is_input_required:
                self.enter_state(self.next_state.pop())

        elif self.state == STATE_INFO:
            if key_back(event.key):
                self.enter_state(STATE_MAIN)
            if event.key == pygame.K_LEFT:
                self.info_col = (self.info_col - 1) % 4
            if event.key == pygame.K_RIGHT:
                self.info_col = (self.info_col + 1) % 4
            if event.key == pygame.K_UP:
                self.info_row = INFO_ROW_ENEMY
            if event.key == pygame.K_DOWN:
                self.info_row = INFO_ROW_PLAYER
        # ========================= END HANDLE_EVENT =================================

    def update(self):
        if self.pending_state is not None:
            next_state = self.pending_state
            self.pending_state = None
            self.enter_state(next_state)
            return

        if not self.is_player_turn:
            pass
        if self.state == STATE_SCROLL:
            if not self.scroll_is_done:
                chars_per_second = SCROLL_SPEED * SCROLL_DELAY_CONSTANT
                chars_per_frame = chars_per_second / (SCROLL_CONSTANT * TARGET_FPS)
                self.scroll_index += chars_per_frame
                if int(self.scroll_index) >= len(self.scroll_text):
                    self.scroll_index = len(self.scroll_text)
                    self.scroll_is_done = True
            else:
                if not self.scroll_is_input_required:
                    self.enter_state(self.next_state.pop())
        elif self.state == STATE_WAIT:
            if not self.delay_is_started:
                self.delay_is_started = True
                self.delay_elapsed = 0
            self.delay_elapsed += 1
            if self.delay_elapsed < self.delay_target:
                return
            self.delay_is_started = False
            self.delay_elapsed = 0
            self.delay_target = 0
            self.enter_state(self.next_state.pop())
        elif self.state == STATE_PLAYER_SINGLE_TARGET_HP:
            if self.dmg_hp_scrolls[0] > self.dmg_hp_targets[0]:
                diff = self.dmg_hp_scrolls[0] - self.dmg_hp_targets[0]
                step = max(1, int(diff * 0.18))   # tweak 0.18 to taste
                self.dmg_hp_scrolls[0] -= step
            else:
                self.enter_state(STATE_SCROLL)
                self.next_state.push(STATE_COMPLETE_PLAYER_TURN)


        
    def enter_state(self, state):
        if state == STATE_MAIN:
            if self.state in (None,
                              STATE_COMPLETE_PLAYER_TURN):
                # Used for menus
                self.menu_cursor_x = 0
                self.menu_cursor_y = 0
                self.skills_cursor = 0
                self.skills_scroll = 0
                self.info_row = INFO_ROW_PLAYER
                self.info_col = 0
            # See battle_target
            self.target_index = 0
            # Generic dialogue to scroll
            self.scroll_text = ""
            self.scroll_index = 0
            self.scroll_is_done = False
            self.scroll_is_input_required = False
            # Generic delay after scroll
            self.delay_target = WAIT_FRAMES_ANNOUNCE_SKILL
            self.delay_elapsed = 0
            self.delay_is_started = False
            # Keep track of future states
            self.next_state = Stack()
            # (text, 
            #  is_input_required, 
            #  flag_miss,
            #  flag_weak,
            #  flag_neutral,
            #  flag_null)
            self.next_text = Stack()
            # (frames, draw_text_finished, draw_anim_skill)
            self.next_wait = Stack()
            # Damage phase flag
            self.dmg_hp_targets = []
            self.dmg_hp_scrolls = []
            # Renderer flags
            self.draw_enemy_bounce = False
            self.draw_affinity_color = False
            self.draw_enemy_info = False
            self.draw_anim_skill = False
            self.draw_text_finished = False
            self.draw_player_bounce = True
            self.draw_hp_bounce = True
            self.draw_darken = False
            self.draw_mp_cost = False
            self.draw_dmg_hp_scroll_enemy = False
            self.draw_dmg_hp_scroll_player = False
            self.draw_press_turn = True
                
        elif state == STATE_SKILLS:
            self.draw_enemy_bounce = False
            self.draw_darken = False
            self.draw_affinity_color = False
            self.draw_mp_cost = True
            self.draw_enemy_info = False
        elif state == STATE_PLAYER_SINGLE_TARGET_TARGET:
            self.draw_enemy_bounce = True
            self.draw_darken = True
            self.draw_affinity_color = True
            self.draw_enemy_info = True
        elif state == STATE_SCROLL:      
            self.draw_enemy_bounce = False
            self.draw_player_bounce = False
            self.draw_hp_bounce = False
            self.draw_affinity_color = False
            self.draw_mp_cost = False
            self.scroll_index = 0
            self.scroll_is_done = False
            next = self.next_text.pop()
            self.scroll_text = next[0]
            self.scroll_is_input_required = next[1]
            scroll_flag_miss = next[2]
            scroll_flag_weak = next[3]
            scroll_flag_neutral = next[4]
            scroll_flag_null = next[5]
            if scroll_flag_miss:
                self._consume_full_turn()
                self._consume_full_turn()
            if scroll_flag_weak:
                self._consume_half_turn()
            if scroll_flag_neutral:
                self._consume_full_turn()
            if scroll_flag_null:
                self._consume_wipe_turn()
            if self.state == STATE_PLAYER_SINGLE_TARGET_HP:
                self.draw_dmg_hp_scroll_player = False
                self.draw_dmg_hp_scroll_enemy = False
            if self.state == STATE_MAIN:
                self.draw_player_bounce = True
                self.draw_hp_bounce = True
        elif state == STATE_WAIT:
            next = self.next_wait.pop()
            self.delay_target = next[0]
            self.draw_text_finished = next[1]
            self.draw_anim_skill = next[2]
            if self.state == STATE_SCROLL:
                self.draw_text_finished = True
        elif state == STATE_PLAYER_SINGLE_TARGET_CALC:
            attacker = self.player_team[self.turn_index]
            defender = self.enemy_team[self.target_index]

            move_name = attacker.moves[self.skills_cursor + self.skills_scroll]
            move = self.moves[move_name]
            move_mp_cost = move["mp"]
            move_power = move["power"]
            move_element = move["element"]
            move_accuracy = move["accuracy"]
            move_type = move["type"]

            defender_affinity = defender.affinities[ELEMENT_INDEX[move_element]]

            attacker.remaining_mp -= move_mp_cost

            odds_hit = move_accuracy / 100
            odds_hit *= DMG_BUFFS_ACC[attacker.speed_buff]
            odds_hit /= DMG_BUFFS_ACC[defender.speed_buff]
            atk_norm = (attacker.speed - DMG_SPEED_MIN) / (DMG_SPEED_MAX - DMG_SPEED_MIN)
            def_norm = (defender.speed - DMG_SPEED_MIN) / (DMG_SPEED_MAX - DMG_SPEED_MIN)
            odds_hit *= 1 + (DMG_SPEED_CONSTANT * (atk_norm - def_norm))
            odds_hit = max(0.0, min(1.0, odds_hit))

            if  (random.random() <= odds_hit) or \
                (defender_affinity >= AFFINITY_NULL):
                # hit
                is_crit = (random.random() < CHANCE_CRIT) and (move_element == "Physical")
                reflected = (AFFINITY_REFLECT <= defender_affinity < AFFINITY_ABSORB)
                nontarget = attacker
                target = defender
                if reflected:
                    nontarget = defender
                    target = attacker
                target_affinity = target.affinities[ELEMENT_INDEX[move_element]]
                if reflected:
                    target_affinity = min(AFFINITY_NULL, target_affinity)

                damage = move_power
                # atk/def
                if (move_type == "Physical"):
                    damage *= nontarget.attack
                    damage /= target.defense
                elif (move_type == "Special"):
                    damage *= nontarget.spattack
                    damage /= target.spdefense
                damage *= DMG_BUFFS[nontarget.attack_buff]
                damage /= DMG_BUFFS[target.defense_buff]
                # level
                damage *= (((2 * nontarget.level)/5)+2)
                damage /= 50
                damage += 2
                # crit
                if is_crit:
                    damage *= DMG_CRIT
                # affinities
                if ((target_affinity < AFFINITY_NEUTRAL) and \
                    (not target.is_guarding)):
                    damage *= DMG_WEAK
                if (AFFINITY_RESIST <= target_affinity < AFFINITY_NULL):
                    damage *= DMG_RESIST
                if (AFFINITY_NULL <= target_affinity < AFFINITY_REFLECT):
                    damage *= DMG_IMMUNE
                # potentials
                potential = nontarget.potential[ELEMENT_INDEX[move_element]]
                damage *= (1.0 + (potential / 18))
                # random
                damage *= random.randint(85, 100) / 100
                # round
                damage = int(damage)

                actual_dealt = damage
                if target.remaining_hp < damage:
                    actual_dealt = target.remaining_hp
                t = ""
                if defender_affinity == AFFINITY_NEUTRAL:
                    t = f"Dealt {actual_dealt} damage."
                else:
                    if defender_affinity < AFFINITY_NEUTRAL:
                        t = AFFINITY_TEXT_WEAK
                    elif AFFINITY_RESIST <= defender_affinity < AFFINITY_NULL:
                        t = AFFINITY_TEXT_RESIST
                    elif AFFINITY_NULL <= defender_affinity < AFFINITY_REFLECT:
                        t = AFFINITY_TEXT_NULL
                    elif AFFINITY_REFLECT <= defender_affinity < AFFINITY_ABSORB:
                        t = AFFINITY_TEXT_REFLECT
                    elif defender_affinity >= AFFINITY_ABSORB:
                        t = AFFINITY_TEXT_ABSORB
                        t += f" \n Recovered {actual_dealt} HP."
                    if (defender_affinity < AFFINITY_NEUTRAL
                        or AFFINITY_RESIST <= defender_affinity < AFFINITY_NULL
                        or AFFINITY_REFLECT <= defender_affinity < AFFINITY_ABSORB
                    ):
                        t += f" \n Dealt {actual_dealt} damage."
                if is_crit:
                    t += f" \n A critical hit!"
                flag_weak = (is_crit or (defender_affinity < AFFINITY_NEUTRAL)) and not defender.is_guarding
                flag_neutral = (AFFINITY_NEUTRAL <= defender_affinity < AFFINITY_NULL) and not is_crit
                flag_null = (defender_affinity >= AFFINITY_NULL)
                self.next_text.push((t,
                                     True,
                                     False,
                                     flag_weak,
                                     flag_neutral,
                                     flag_null))
                
                defender.is_guarding = False
                
                hp_target = target.remaining_hp - damage
                hp_target = max(0, hp_target)
                hp_target = min(hp_target, target.max_hp)

                self.dmg_hp_targets = [hp_target]
                self.dmg_hp_scrolls = [target.remaining_hp]
                target.remaining_hp = hp_target
                self.draw_dmg_hp_scroll_player = False
                self.draw_dmg_hp_scroll_enemy = True
                if (AFFINITY_REFLECT <= defender_affinity < AFFINITY_ABSORB):
                    self.draw_dmg_hp_scroll_player = True
                    self.draw_dmg_hp_scroll_enemy = False
                self.next_state.push(STATE_PLAYER_SINGLE_TARGET_HP)

                self.next_wait.push((WAIT_FRAMES_BEFORE_HP,
                                     True,
                                     False))
                self.next_state.push(STATE_WAIT)

                self.next_wait.push((WAIT_FRAMES_SKILL_ANIM,
                                     True,
                                     True))
                self.next_state.push(STATE_WAIT)
            else:
                # missed
                self.scroll_is_input_required = True
                self.next_text.push(("But it missed!", 
                                     True,
                                     True,
                                     False,
                                     False,
                                     False))
                self.next_state.push(STATE_SCROLL)

            if move_name == "Attack":
                self.next_text.push((f"{attacker.name} attacks {defender.name}!", 
                                     False,
                                     False,
                                     False,
                                     False,
                                     False))
            else:
                self.next_text.push((f"{attacker.name} uses {move_name} on {defender.name}!", 
                                     False,
                                     False,
                                     False,
                                     False,
                                     False))
            self.pending_state = STATE_SCROLL

            self.next_wait.push((WAIT_FRAMES_ANNOUNCE_SKILL,
                                 True,
                                 False))
            self.next_state.push(STATE_WAIT)
        elif state == STATE_COMPLETE_PLAYER_TURN:
            if not any(v > 0 for v in self.press_turns):
                self.is_player_turn = False
                self.press_turns = FRESH_PRESS_TURNS.copy()
                for e in self.enemy_team:
                    e.attack_buff_turns = max(0, e.attack_buff_turns - 1)
                    e.defense_buff_turns = max(0, e.defense_buff_turns - 1)
                    e.speed_buff_turns = max(0, e.speed_buff_turns - 1)
                    if e.attack_buff_turns == 0:
                        e.attack_buff = 0
                    if e.defense_buff_turns == 0:
                        e.defense_buff = 0
                    if e.speed_buff_turns == 0:
                        e.speed_buff = 0
            self.turn_index = (self.turn_index + 1) % len(self.player_team)
            if self.is_player_turn:
                self.player_team[self.turn_index].is_guarding = False
            self.pending_state = STATE_MAIN
        elif state == STATE_INFO:
            self.draw_press_turn = False
            self.draw_darken = True
            self.draw_enemy_info = True
        self.state = state

    def _init_teams(self):
        # ========================= START _INIT_TEAMS =================================

        # --- PLAYER LEADER (custom Pokémon) ---
        species_bulbasaur = get_species_by_number(self.pkmn, 1)
        pkmn_player = create_pokemon_from_species(species_bulbasaur, level=99)
        pkmn_player.name = "Kobe"
        pkmn_player.pokedex_number = PLAYER_DEX_NO
        player_moves = [
            "Attack",
            "Agi", "Bufu", "Zio", "Zan", "Hama", "Mudo",
            "Tarukaja", "Rakukaja", "Sukukaja",
            "Heat Riser", "Red Capote",
            "Matarukaja", "Marakukaja", "Masukukaja",
            "Luster Candy",
            "Dia", "Diarama", "Diarahan"
        ]
        pkmn_player.moves = player_moves[:]

        self.player_team = [pkmn_player]

        for _ in range(3):
            species = get_species_by_number(self.pkmn, random.randint(1, 392))
            p = create_pokemon_from_species(species)
            p.moves = player_moves[:]

            # Back sprites
            if p.is_shiny:
                p.sprite_column = random.choice([8, 9])   # shiny back
            else:
                p.sprite_column = random.choice([3, 4])   # nonshiny back

            self.player_team.append(p)

        enemy_moves = ["Attack", "Agi", "Bufu", "Zio", "Zan", "Hama", "Mudo"]

        self.enemy_team = []
        for _ in range(4):
            species = get_species_by_number(self.pkmn, random.randint(1, 392))
            p = create_pokemon_from_species(species)
            p.moves = enemy_moves[:]

            # Front sprites
            if p.is_shiny:
                p.sprite_column = random.choice([5, 6, 7])  # shiny front
            else:
                p.sprite_column = random.choice([0, 1, 2])  # nonshiny front

            self.enemy_team.append(p)
        # ========================= END _INIT_TEAMS =================================

    def _consume_full_turn(self):
        for i in range(4):
            if self.press_turns[i] != PRESS_TURN_NULL:
                self.press_turns[i] = PRESS_TURN_NULL
                return
            
    def _consume_half_turn(self):
        for i in range(4):
            if self.press_turns[i] == PRESS_TURN_SOLID:
                self.press_turns[i] = PRESS_TURN_FLASH
                return
        for i in range(4):
            if self.press_turns[i] == PRESS_TURN_FLASH:
                self.press_turns[i] = PRESS_TURN_NULL
                return
            
    def _consume_wipe_turn(self):
        self.press_turns = [0, 0, 0, 0]
