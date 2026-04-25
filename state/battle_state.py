# state/battle_state_new.py
from constants import *
from stack import Stack
from state.state_manager import GameState

from data.smt.smt_stats import load_pkmn_from_json, get_pkmn_by_number
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

        # Player turn: choose skills/items/...
        self.state = STATE_MAIN
        # Used for multiple menus
        self.menu_cursor_x = 0
        self.menu_cursor_y = 0
        self.skills_cursor = 0
        self.skills_scroll = 0
        # See battle_target
        self.target_index = 0
        # Generic dialogue to scroll
        self.scroll_text = ""
        self.scroll_index = 0
        self.scroll_done = False
        # Generic delay after scroll
        self.delay_target = WAIT_FRAMES_BEFORE_DAMAGE
        self.delay_frames = 0
        self.delay_started = False
        # Keep track of future states
        self.next_state = Stack()
        # Renderer flags
        self.draw_enemy_bounce = False
        self.draw_player_bounce = False
        self.draw_hp_bounce = False
        self.draw_darken = False
        self.draw_affinity_color = False
        self.draw_mp_cost = False
        self.draw_enemy_info = False
        self.draw_anim_skill = False
        self.draw_text_finished = False

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
                    self.enter_state(STATE_GUARD)
                    # ...


                if  self.menu_cursor_x == MENU_CURSOR_TALK_X and \
                    self.menu_cursor_y == MENU_CURSOR_TALK_Y:
                    self.enter_state(STATE_TALK)
                    # ...


                if  self.menu_cursor_x == MENU_CURSOR_CHANGE_X and \
                    self.menu_cursor_y == MENU_CURSOR_CHANGE_Y:
                    self.enter_state(STATE_CHANGE)
                    # ...


                if  self.menu_cursor_x == MENU_CURSOR_ESCAPE_X and \
                    self.menu_cursor_y == MENU_CURSOR_ESCAPE_Y:
                    self.enter_state(STATE_ESCAPE)
                    # ...


                if  self.menu_cursor_x == MENU_CURSOR_PASS_X and \
                    self.menu_cursor_y == MENU_CURSOR_PASS_Y:
                    # ...
                    pass

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
                    self.enter_state(STATE_SKILLS_TARGET_ENEMY)
                    return
                # ...
            if key_back(event.key):
                self.enter_state(STATE_MAIN)
        elif self.state == STATE_ITEMS:
            pass
        elif self.state == STATE_GUARD:
            pass
        elif self.state == STATE_TALK:
            pass
        elif self.state == STATE_CHANGE:
            pass
        elif self.state == STATE_ESCAPE:
            pass
        elif self.state == STATE_INFO:
            pass
        elif self.state == STATE_SKILLS_TARGET_ENEMY:
            if event.key == pygame.K_LEFT:
                self.target_index = (self.target_index - 1) % len(self.enemy_team)
                return
            elif event.key == pygame.K_RIGHT:
                self.target_index = (self.target_index + 1) % len(self.enemy_team)
                return
            elif key_confirm(event.key):
                self.enter_state(STATE_SCROLL)
                self.next_state.push(STATE_ANIMATE_SKILL)
            elif key_back(event.key):
                self.enter_state(STATE_SKILLS)
        elif self.state == STATE_SCROLL:
            if not self.scroll_done and key_confirm(event.key):
                self.scroll_index = len(self.scroll_text)
                self.scroll_done = True
        elif self.state == STATE_WAIT:
            pass
        elif self.state == STATE_ANIMATE_SKILL:
            pass
        # ========================= END HANDLE_EVENT =================================

    def update(self):
        if not self.is_player_turn:
            pass
        if self.state == STATE_SCROLL:
            if not self.scroll_done:
                chars_per_second = SCROLL_SPEED * SCROLL_DELAY_CONSTANT
                chars_per_frame = chars_per_second / (SCROLL_CONSTANT * TARGET_FPS)
                self.scroll_index += chars_per_frame
                if int(self.scroll_index) >= len(self.scroll_text):
                    self.scroll_index = len(self.scroll_text)
                    self.scroll_done = True
            else:
                self.enter_state(self.next_state.pop())
        elif self.state == STATE_WAIT:
            if not self.delay_started:
                self.delay_started = True
                self.delay_frames = 0
            self.delay_frames += 1
            if self.delay_frames < self.delay_target:
                return
            self.delay_started = False
            self.delay_frames = 0
            self.delay_target = 0
            self.enter_state(self.next_state.pop())
        elif self.state == STATE_ANIMATE_SKILL:
            if not self.delay_started:
                self.delay_started = True
                self.delay_frames = 0
            self.delay_frames += 1
            if self.delay_frames < self.delay_target:
                return
            self.delay_started = False
            self.delay_frames = 0
            self.delay_target = 0
            self.enter_state(STATE_CHANGE)
        
    def enter_state(self, state):
        if state == STATE_MAIN:
            self.draw_player_bounce = True
            self.draw_hp_bounce = True
            self.draw_darken = False
            self.draw_mp_cost = False
        elif state == STATE_SKILLS:
            self.draw_enemy_bounce = False
            self.draw_darken = False
            self.draw_affinity_color = False
            self.draw_mp_cost = True
            self.draw_enemy_info = False
        elif state == STATE_SKILLS_TARGET_ENEMY:
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
            self.scroll_done = False
            if self.state == STATE_SKILLS_TARGET_ENEMY:
                self.delay_target = WAIT_FRAMES_BEFORE_DAMAGE
                pkmn = self.player_team[self.turn_index]
                target = self.enemy_team[self.target_index]
                move_name = pkmn.moves[self.skills_cursor + self.skills_scroll]
                move = self.moves[move_name]
                cost = move["mp"]
                pkmn.remaining_mp = max(0, pkmn.remaining_mp - cost)
                if move_name == "Attack":
                    self.scroll_text = f"{pkmn.name} attacks {target.name}!"
                else:
                    self.scroll_text = f"{pkmn.name} uses {move_name} on {target.name}!"
        elif state == STATE_WAIT:
            pass
        elif state == STATE_ANIMATE_SKILL:
            self.draw_anim_skill = True
            self.draw_text_finished = True
            self.delay_target = WAIT_FRAMES_BEFORE_DAMAGE
            if (self.state == STATE_WAIT):
                pass
        self.state = state

    def _init_teams(self):
        # ========================= START _INIT_TEAMS =================================
        pkmn_bulbasaur = get_pkmn_by_number(self.pkmn, pokedex_number=1)
        pkmn_player = Pokemon(
            pokedex_number=PLAYER_DEX_NO,
            name="Kobe",
            level=99,
            stats=pkmn_bulbasaur.base_stats,
            affinities=pkmn_bulbasaur.affinities,
            potential=pkmn_bulbasaur.potential,
            learnset=pkmn_bulbasaur.learnset,
            moves=["Attack", 
                   "Agi", "Bufu", "Zio", "Zan", "Hama", "Mudo", 
                   "Tarukaja", "Rakukaja", "Sukukaja", 
                   "Heat Riser", "Red Capote", 
                   "Matarukaja", "Marakukaja", "Masukukaja", 
                   "Luster Candy", 
                   "Dia", "Diarama", "Diarahan"]
        )

        self.player_team = [
            pkmn_player,
            get_pkmn_by_number(self.pkmn, random.randint(1,392)),      # Nidoking
            get_pkmn_by_number(self.pkmn, random.randint(1,392)),     # Kangaskhan
            get_pkmn_by_number(self.pkmn, random.randint(1,392))        # Charizard
        ]
        for p in self.player_team:
            p.moves = ["Attack", 
                   "Agi", "Bufu", "Zio", "Zan", "Hama", "Mudo", 
                   "Tarukaja", "Rakukaja", "Sukukaja", 
                   "Heat Riser", "Red Capote", 
                   "Matarukaja", "Marakukaja", "Masukukaja", 
                   "Luster Candy", 
                   "Dia", "Diarama", "Diarahan"]
            if p.is_shiny:
                p.sprite_column = random.choice([8, 9])   # shiny back
            else:
                p.sprite_column = random.choice([3, 4])   # nonshiny back
        
        self.enemy_team = [
            get_pkmn_by_number(self.pkmn, random.randint(1,392)),      # Blastoise
            get_pkmn_by_number(self.pkmn, random.randint(1,392)),      # Venusaur
            get_pkmn_by_number(self.pkmn, random.randint(1,392)),    # Mewtwo
            get_pkmn_by_number(self.pkmn, random.randint(1,392))      # Butterfree
        ]
        for p in self.enemy_team:
            p.moves = ["Attack",
                       "Agi", "Bufu", "Zio", "Zan", "Hama", "Mudo"]
            if p.is_shiny:
                p.sprite_column = random.choice([5, 6, 7])  # shiny front
            else:
                p.sprite_column = random.choice([0, 1, 2])  # nonshiny front
        # ========================= END _INIT_TEAMS =================================