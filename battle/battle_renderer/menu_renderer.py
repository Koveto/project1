from constants import *
from battle.battle_constants import *

class MenuRenderer:
    def __init__(self, font0, font2, cursor_sprite, smt_moves):
        self.font0 = font0
        self.font2 = font2
        self.cursor_sprite = cursor_sprite
        self.smt_moves = smt_moves

    def draw_main_menu(self, screen, active_pokemon, menu_index):
        self.font0.draw_text(screen, f"What will {active_pokemon.name} do?",
                                X_MENU_MAIN, Y_MENU_MAIN_0)
        self.font0.draw_text(screen, MENU_MAIN_LINE_1,
                            X_MENU_MAIN, Y_MENU_MAIN_1)
        self.font0.draw_text(screen, MENU_MAIN_LINE_2,
                            X_MENU_MAIN, Y_MENU_MAIN_2)

        cursor_x, cursor_y = COORDS_MENU_MAIN[menu_index]
        screen.blit(self.cursor_sprite, (cursor_x, cursor_y))

    def draw_skills_menu(self, screen, active_pokemon, skills_scroll, skills_cursor):
        visible_moves = active_pokemon.moves[skills_scroll:skills_scroll + 3]
        y = SKILLS_Y
        for move_name in visible_moves:
            text = active_pokemon.format_move_for_menu(move_name, self.smt_moves)
            self.font2.draw_text(screen, text, SKILLS_X, y)
            y += SKILLS_Y_INCR

        cursor_x, cursor_y = COORDS_MENU_SKILLS[skills_cursor]
        screen.blit(self.cursor_sprite, (cursor_x, cursor_y))

    def draw_dummy_menu(self, screen, previous_menu_index):
        msg = DUMMY_TEXTS[previous_menu_index]
        self.font0.draw_text(screen, msg, X_MENU_MAIN, Y_MENU_MAIN_0)
        self.font0.draw_text(screen, DUMMY_MSG, X_MENU_MAIN, Y_MENU_MAIN_1)
