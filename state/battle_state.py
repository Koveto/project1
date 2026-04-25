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
from battle.battle_menu import (
    handle_event_main,
    handle_event_skills
)
from battle.battle_target import handle_event_skills_target_enemy
from battle.battle_text import (
    handle_event_scroll,
    update_scroll
)
#from battle.battle_damage import handle_event_animate_enemy_hp

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
        self.menu_scroll_x = 0
        self.menu_scroll_y = 0
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
        # After SCROLL_THEN_WAIT go here
        self.next_state = Stack()
        # Move selected by player or enemy
        self.pending_move_name = ""
        # Renderer flags
        self.draw_enemy_bounce = False


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
            handle_event_main(self, event)
        elif self.state == STATE_SKILLS:
            handle_event_skills(self, event)
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
            handle_event_skills_target_enemy(self, event)
        elif self.state == STATE_SCROLL:
            handle_event_scroll(self, event)
        elif self.state == STATE_WAIT:
            print("wait")
        #if self.state == STATE_ANIMATE_ENEMY_HP:
        #    handle_event_animate_enemy_hp(self, event)
        # ========================= END HANDLE_EVENT =================================

    def update(self):
        if not self.is_player_turn:
            pass
        if self.state == STATE_SCROLL:
            return update_scroll(self)
        
    def enter_state(self, state):
        self.state = state
        if self.state == STATE_MAIN:
            self.menu_cursor_x = 0
            self.menu_cursor_y = 0
            self.menu_scroll_x = 0
            self.menu_scroll_y = 0
            self.target_index = 0
            self.scroll_text = ""
            self.scroll_index = 0
            self.scroll_done = False
            self.delay_target = WAIT_FRAMES_BEFORE_DAMAGE
            self.delay_frames = 0
            self.delay_started = False
            self.next_state = Stack()
            self.pending_move_name = ""
            self.draw_enemy_bounce = False
        elif self.state == STATE_SKILLS:
            self.menu_cursor_x = 0
            self.menu_cursor_y = 0
            self.menu_scroll_x = 0
            self.menu_scroll_y = 0
            self.target_index = 0
            self.scroll_text = ""
            self.scroll_index = 0
            self.scroll_done = False
            self.delay_target = WAIT_FRAMES_BEFORE_DAMAGE
            self.delay_frames = 0
            self.delay_started = False
            self.next_state = Stack()
            self.pending_move_name = ""
            self.draw_enemy_bounce = False
        elif self.state == STATE_SKILLS_TARGET_ENEMY:
            self.menu_cursor_x = 0
            self.menu_cursor_y = 0
            self.menu_scroll_x = 0
            self.menu_scroll_y = 0
            self.target_index = 0
            self.scroll_text = ""
            self.scroll_index = 0
            self.scroll_done = False
            self.delay_target = WAIT_FRAMES_BEFORE_DAMAGE
            self.delay_frames = 0
            self.delay_started = False
            self.next_state = Stack()
            self.pending_move_name = ""
            self.draw_enemy_bounce = True
        elif self.state == STATE_SCROLL:
            self.menu_cursor_x = 0
            self.menu_cursor_y = 0
            self.menu_scroll_x = 0
            self.menu_scroll_y = 0
            self.target_index = 0
            self.scroll_text = ""
            self.scroll_index = 0
            self.scroll_done = False
            self.delay_target = WAIT_FRAMES_BEFORE_DAMAGE
            self.delay_frames = 0
            self.delay_started = False
            self.next_state = Stack()
            self.pending_move_name = ""
            self.draw_enemy_bounce = False
        elif self.state == STATE_WAIT:
            self.menu_cursor_x = 0
            self.menu_cursor_y = 0
            self.menu_scroll_x = 0
            self.menu_scroll_y = 0
            self.target_index = 0
            self.scroll_text = ""
            self.scroll_index = 0
            self.scroll_done = False
            self.delay_target = WAIT_FRAMES_BEFORE_DAMAGE
            self.delay_frames = 0
            self.delay_started = False
            self.next_state = Stack()
            self.pending_move_name = ""
            self.draw_enemy_bounce = False

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