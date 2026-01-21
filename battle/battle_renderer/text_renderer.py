from constants import *
from battle.battle_constants import *

class TextRenderer:
    def __init__(self, font0, cursor_sprite):
        self.font0 = font0
        self.cursor_sprite = cursor_sprite

    def wrap_text_words(self, text, max_width=32):
        words = text.split()
        lines = []
        current = []

        for word in words:
            # Predict length if we add this word
            predicted = " ".join(current + [word])
            if len(predicted) > max_width:
                lines.append(current)
                current = [word]
            else:
                current.append(word)

        if current:
            lines.append(current)

        # Ensure exactly 3 lines
        while len(lines) < 3:
            lines.append([])

        return lines[:3]
    
    def draw_damaging_enemy(
            self, screen,
            scroll_text, scroll_index, scroll_done,
            damage_done, affinity_done,
            affinity_text, affinity_scroll_index,
            affinity_scroll_done, blink
    ):
        
        # ---------------------------------------------------------
        # PHASE 3/4 — Affinity text (scrolling or full)
        # ---------------------------------------------------------
        if damage_done and affinity_text:

            # PHASE 3 — affinity text scrolling
            if not affinity_done:
                visible = int(affinity_scroll_index)
                text_to_draw = affinity_text[:visible]

                self.font0.draw_text(
                    screen, text_to_draw,
                    X_MENU_MAIN, Y_MENU_MAIN_0
                )

                if affinity_scroll_done and blink:
                    screen.blit(self.cursor_sprite, (CONFIRM_ARROW_X, CONFIRM_ARROW_Y))

                return

            # PHASE 4 — affinity text fully displayed
            self.font0.draw_text(
                screen, affinity_text,
                X_MENU_MAIN, Y_MENU_MAIN_0
            )

            if blink:
                screen.blit(self.cursor_sprite, (CONFIRM_ARROW_X, CONFIRM_ARROW_Y))
            return


        # ---------------------------------------------------------
        # PHASE 4b — Neutral damage: KEEP ATTACK TEXT VISIBLE
        # ---------------------------------------------------------
        if damage_done and not affinity_text:

            full_word_lines = self.wrap_text_words(scroll_text, max_width=32)

            if len(full_word_lines) > 0:
                self.font0.draw_text(screen, full_word_lines[0],
                                    X_MENU_MAIN, Y_MENU_MAIN_0)
            if len(full_word_lines) > 1:
                self.font0.draw_text(screen, full_word_lines[1],
                                    X_MENU_MAIN, Y_MENU_MAIN_1)
            if len(full_word_lines) > 2:
                self.font0.draw_text(screen, full_word_lines[2],
                                    X_MENU_MAIN, Y_MENU_MAIN_2)

            if blink:
                screen.blit(self.cursor_sprite, (CONFIRM_ARROW_X, CONFIRM_ARROW_Y))

            return


        # ---------------------------------------------------------
        # PHASE 1 — Attack text scrolls (pre‑damage)
        # ---------------------------------------------------------
        full_word_lines = self.wrap_text_words(scroll_text, max_width=32)

        visible_chars = scroll_index
        visible_lines = ["", "", ""]

        for line_idx, words in enumerate(full_word_lines):
            for word in words:
                chunk = (word + " ")
                if visible_chars >= len(chunk):
                    visible_lines[line_idx] += chunk
                    visible_chars -= len(chunk)
                else:
                    visible_lines[line_idx] += chunk[:visible_chars]
                    visible_chars = 0
                    break

            if visible_chars == 0:
                break

        # Draw attack text (scrolling)
        self.font0.draw_text(screen, visible_lines[0], X_MENU_MAIN, Y_MENU_MAIN_0)
        self.font0.draw_text(screen, visible_lines[1], X_MENU_MAIN, Y_MENU_MAIN_1)
        self.font0.draw_text(screen, visible_lines[2], X_MENU_MAIN, Y_MENU_MAIN_2)

        # ---------------------------------------------------------
        # PHASE 2 — Scroll done, HP anim running (NO ARROW)
        # ---------------------------------------------------------
        if scroll_done and not damage_done:
            return

        # ---------------------------------------------------------
        # PHASE 1.5 — Scroll done, HP anim not started yet
        # ---------------------------------------------------------
        if scroll_done and not damage_done and not self.damage_started:
            if blink:
                screen.blit(self.cursor_sprite, (CONFIRM_ARROW_X, CONFIRM_ARROW_Y))
            return

