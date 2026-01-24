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

    def draw_target_select_menu(self, screen, active_pokemon,
                            skills_scroll, skills_cursor):
        selected_index = skills_scroll + skills_cursor
        move_name = active_pokemon.moves[selected_index]
        text = active_pokemon.format_move_for_menu(move_name, self.smt_moves)
        y = SKILLS_Y + (skills_cursor * SKILLS_Y_INCR)
        self.font2.draw_text(screen, text, SKILLS_X, y)
        cursor_x, cursor_y = COORDS_MENU_SKILLS[skills_cursor]
        screen.blit(self.cursor_sprite, (cursor_x, cursor_y))

    def draw_item_target_select_menu(self, screen, active_pokemon,
                                 skills_scroll, skills_cursor,
                                 pending_item_data):

        # Extract the skill name from the item type
        item_type = pending_item_data["type"]  # e.g. "damage_Agibarion"
        skill_name = item_type.split("damage_")[1]   # → "Agibarion"

        # Format the move info using the existing skill formatter
        text = active_pokemon.format_move_for_menu(skill_name, self.smt_moves)

        # Draw it in the same row as the skills menu would
        self.font2.draw_text(screen, text, SKILLS_X, SKILLS_Y)

        # Draw cursor in the same place as the skills menu
        cursor_x, cursor_y = COORDS_MENU_SKILLS[0]
        screen.blit(self.cursor_sprite, (cursor_x, cursor_y))


    def draw_item_menu(self, screen, inventory, cursor_x, cursor_y):
        item_names = list(inventory.keys())

        index = 0
        for row in range(ITEM_ROWS):
            for col in range(ITEM_COLS):
                if index < len(item_names):
                    name = item_names[index]
                    qty = inventory[name]

                    # Build display string
                    if qty > 1:
                        suffix = f" x{qty}"
                        base_len = 13 - len(suffix)

                        # Truncate name if needed
                        if len(name) > base_len:
                            display_name = name[:base_len]
                        else:
                            display_name = name

                        display_text = display_name + suffix
                    else:
                        # Single item: truncate to 13 chars max
                        display_text = name[:13]

                    # Compute coordinates
                    x = X_ITEM + col * ITEM_COL_SIZE
                    y = Y_ITEM + row * ITEM_ROW_SIZE

                    # Draw item text
                    self.font2.draw_text(screen, display_text, x, y)

                index += 1

        # Draw cursor
        cursor_x_pos = X_MENU_MAIN + cursor_x * ITEM_COL_SIZE
        cursor_y_pos = Y_ITEM + cursor_y * ITEM_ROW_SIZE
        screen.blit(self.cursor_sprite, (cursor_x_pos, cursor_y_pos))


    def draw_item_info(self, screen, item_data, text_renderer):
        # Word-wrap the description
        desc_lines = text_renderer.wrap_text_words(item_data["description"], max_width=32)
    
        y = Y_MENU_MAIN_0
        for line in desc_lines:
            text = " ".join(line)
            self.font0.draw_text(screen, text, X_MENU_MAIN, y)
            y += 100


