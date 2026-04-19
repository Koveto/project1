from constants import *
from battle.battle_constants import *

class MenuRenderer:
    def __init__(self, font0, font2, cursor_sprite, smt_moves):
        self.font0 = font0
        self.font2 = font2
        self.cursor_sprite = cursor_sprite
        self.smt_moves = smt_moves

    def format_move_for_menu(self, move_name, smt_moves, active_pokemon):
        m = smt_moves.get(move_name)
        if not m:
            return f"{move_name[:11]:<11} {'---':>3}  {'----':<5}  {'---':>3}  {'---':<12}"

        # Base name (max 11 chars before adding potential)
        base_name = move_name[:11]

        # Full element order including Healing + Support
        ELEMENT_ORDER = [
            "Physical", "Fire", "Force", "Ice", "Electric", "Light", "Dark",
            "Healing", "Support"
        ]

        element = m["element"]

        # Determine potential index
        try:
            element_index = ELEMENT_ORDER.index(element)
            pot = active_pokemon.potential[element_index]
        except ValueError:
            pot = 0

        # Build potential text
        pot_text = f" {pot:+d}" if pot != 0 else ""

        # Ensure name + pot_text fits in 11 chars
        combined = base_name + pot_text
        if len(combined) > 11:
            trim_amount = min(len(combined) - 11, 3)
            base_name = base_name[:-trim_amount]
            combined = base_name + pot_text

        name_field = f"{combined:<11}"

        # Support / Healing formatting
        if element in ("Support", "Healing"):
            mp = f"{m['mp']:>3}"
            element_short = f"{element[:7]:<7}"
            desc = m.get("description", "")[:15]
            desc = f"{desc:<15}"
            return f"{name_field} {mp}  {element_short}  {desc}"

        # Attack formatting
        mp = f"{m['mp']:>3}"
        power = f"{m['power']:>3}" if m["power"] is not None else "---"
        element_short = f"{element[:5]:<5}"
        desc = m.get("description", "")[:12]
        desc = f"{desc:<12}"

        return f"{name_field} {mp}  {element_short}  {power}  {desc}"



    def draw_main_menu(self, b, screen, active_pokemon):
        self.font0.draw_text(screen, f"What will {active_pokemon.name} do?",
                                X_MENU_MAIN, Y_MENU_MAIN_0)
        self.font0.draw_text(screen, MENU_MAIN_LINE_1,
                            X_MENU_MAIN, Y_MENU_MAIN_1)
        self.font0.draw_text(screen, MENU_MAIN_LINE_2,
                            X_MENU_MAIN, Y_MENU_MAIN_2)

        cursor_x, cursor_y = COORDS_MENU_MAIN[b.menu_index]
        screen.blit(self.cursor_sprite, (cursor_x, cursor_y))

    def draw_skills_menu(self, b, screen, active_pokemon):
        visible_moves = active_pokemon.moves[b.skills_scroll:b.skills_scroll + 3]
        y = SKILLS_Y
        for move_name in visible_moves:
            text = self.format_move_for_menu(move_name, self.smt_moves, active_pokemon)
            self.font2.draw_text(screen, text, SKILLS_X, y)
            y += SKILLS_Y_INCR

        cursor_x, cursor_y = COORDS_MENU_SKILLS[b.skills_cursor]
        screen.blit(self.cursor_sprite, (cursor_x, cursor_y))

    def draw_dummy_menu(self, b, screen):
        msg = DUMMY_TEXTS[b.previous_menu_index]
        self.font0.draw_text(screen, msg, X_MENU_MAIN, Y_MENU_MAIN_0)
        self.font0.draw_text(screen, DUMMY_MSG, X_MENU_MAIN, Y_MENU_MAIN_1)

    def draw_target_select_menu(self, b, screen, active_pokemon):
        selected_index = b.skills_scroll + b.skills_cursor
        move_name = active_pokemon.moves[selected_index]
        text = self.format_move_for_menu(move_name, self.smt_moves, active_pokemon)
        y = SKILLS_Y + (b.skills_cursor * SKILLS_Y_INCR)
        self.font2.draw_text(screen, text, SKILLS_X, y)
        cursor_x, cursor_y = COORDS_MENU_SKILLS[b.skills_cursor]
        screen.blit(self.cursor_sprite, (cursor_x, cursor_y))

    def draw_item_target_select_menu(self, b, screen, active_pokemon):

        # Extract the skill name from the item type
        item_type = b.pending_item_data["type"]  # e.g. "damage_Agibarion"
        skill_name = item_type.split("damage_")[1]   # → "Agibarion"

        # Format the move info using the existing skill formatter
        text = self.format_move_for_menu(skill_name, self.smt_moves, active_pokemon)

        # Draw it in the same row as the skills menu would
        self.font2.draw_text(screen, text, SKILLS_X, SKILLS_Y)

        # Draw cursor in the same place as the skills menu
        cursor_x, cursor_y = COORDS_MENU_SKILLS[0]
        screen.blit(self.cursor_sprite, (cursor_x, cursor_y))


    def draw_item_menu(self, b, screen):
        item_names = list(b.model.inventory.keys())

        index = 0
        for row in range(ITEM_ROWS):
            for col in range(ITEM_COLS):
                if index < len(item_names):
                    name = item_names[index]
                    qty = b.model.inventory[name]

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
        cursor_x_pos = X_MENU_MAIN + b.item_cursor_x * ITEM_COL_SIZE
        cursor_y_pos = Y_ITEM + b.item_cursor_y * ITEM_ROW_SIZE
        screen.blit(self.cursor_sprite, (cursor_x_pos, cursor_y_pos))


    def draw_item_ally_target(self, b, screen, text_renderer):
        # Word-wrap the description
        desc_lines = text_renderer.wrap_text_words(b.item_data["description"], max_width=32)
    
        y = Y_MENU_MAIN_0
        for line in desc_lines:
            text = " ".join(line)
            self.font0.draw_text(screen, text, X_MENU_MAIN, y)
            y += 100

    def draw_target_buff_menu(self, b, screen, active_pokemon):
        selected_index = b.skills_scroll + b.skills_cursor
        move_name = active_pokemon.moves[selected_index]
        text = self.format_move_for_menu(move_name, self.smt_moves, active_pokemon)
        y = SKILLS_Y + (b.skills_cursor * SKILLS_Y_INCR)
        self.font2.draw_text(screen, text, SKILLS_X, y)
        cursor_x, cursor_y = COORDS_MENU_SKILLS[b.skills_cursor]
        screen.blit(self.cursor_sprite, (cursor_x, cursor_y))
