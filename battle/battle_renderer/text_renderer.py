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
    
    def draw_simple_scroll(self, b, screen, scroll_index, blink):
        full_word_lines = self.wrap_text_words(b.scroll_text, max_width=32)

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

        # Draw text
        self.font0.draw_text(screen, visible_lines[0], X_MENU_MAIN, Y_MENU_MAIN_0)
        self.font0.draw_text(screen, visible_lines[1], X_MENU_MAIN, Y_MENU_MAIN_1)
        self.font0.draw_text(screen, visible_lines[2], X_MENU_MAIN, Y_MENU_MAIN_2)

        # Draw arrow if scroll finished
        if b.scroll_done and blink:
            screen.blit(self.cursor_sprite, (CONFIRM_ARROW_X, CONFIRM_ARROW_Y))

    
    def draw_damaging_enemy(
            self, b, screen, scroll_index,
            blink
    ):
        # =========================================================
        # CASE A — NON‑NEUTRAL AFFINITY (affinity_text is not None)
        # =========================================================
        if b.damage_done and b.affinity_text:

            # PHASE 3 — Affinity text scrolling
            if not b.affinity_done:
                visible_aff = b.affinity_text[:int(b.affinity_scroll_index)]
                self.font0.draw_text(screen, visible_aff, X_MENU_MAIN, Y_MENU_MAIN_0)
                return

            # PHASE 4 — Affinity fully displayed, now scroll damage text
            self.font0.draw_text(screen, b.affinity_text, X_MENU_MAIN, Y_MENU_MAIN_0)

            # Damage text scrolls only after affinity is done
            visible_dmg = b.damage_text[:int(b.damage_scroll_index)]
            self.font0.draw_text(screen, visible_dmg, X_MENU_MAIN, Y_MENU_MAIN_1)

            # Confirm arrow only when BOTH scrolls are done
            if b.affinity_scroll_done and b.damage_scroll_done and blink:
                screen.blit(self.cursor_sprite, (CONFIRM_ARROW_X, CONFIRM_ARROW_Y))

            return

        # =========================================================
        # CASE B — NEUTRAL AFFINITY (affinity_text is None)
        # =========================================================
        if b.damage_done and not b.affinity_text:
            # Draw the original attack text (already fully visible)
            full_word_lines = self.wrap_text_words(b.scroll_text, max_width=32)

            used_lines = 0
            y = Y_MENU_MAIN_0

            for line in full_word_lines:
                text = " ".join(line)
                if text:
                    self.font0.draw_text(screen, text, X_MENU_MAIN, y)
                    used_lines += 1
                y += DAMAGE_TEXT_INCR

            # Now draw the damage text on the NEXT free line
            dmg_visible = b.damage_text[:int(b.damage_scroll_index)]
            dmg_y = Y_MENU_MAIN_0 + used_lines * DAMAGE_TEXT_INCR
            self.font0.draw_text(screen, dmg_visible, X_MENU_MAIN, dmg_y)

            # Confirm arrow only after damage scroll finishes
            if b.damage_scroll_done and blink:
                screen.blit(self.cursor_sprite, (CONFIRM_ARROW_X, CONFIRM_ARROW_Y))

            return

        # =========================================================
        # CASE C — PRE‑DAMAGE: Attack text scrolls normally
        # =========================================================
        full_word_lines = self.wrap_text_words(b.scroll_text, max_width=32)

        visible_chars = scroll_index
        visible_lines = ["", "", ""]

        for line_idx, words in enumerate(full_word_lines):
            for word in words:
                chunk = word + " "
                if visible_chars >= len(chunk):
                    visible_lines[line_idx] += chunk
                    visible_chars -= len(chunk)
                else:
                    visible_lines[line_idx] += chunk[:visible_chars]
                    visible_chars = 0
                    break
            if visible_chars == 0:
                break

        # Draw scrolling attack text
        self.font0.draw_text(screen, visible_lines[0], X_MENU_MAIN, Y_MENU_MAIN_0)
        self.font0.draw_text(screen, visible_lines[1], X_MENU_MAIN, Y_MENU_MAIN_1)
        self.font0.draw_text(screen, visible_lines[2], X_MENU_MAIN, Y_MENU_MAIN_2)

        # PHASE 2 — Scroll done, HP anim running (NO ARROW)
        if b.scroll_done and not b.damage_done:
            return

        # PHASE 1.5 — Scroll done, HP anim not started yet
        if b.scroll_done and not b.damage_done and not b.damage_started:
            if blink:
                screen.blit(self.cursor_sprite, (CONFIRM_ARROW_X, CONFIRM_ARROW_Y))
            return
    
    def draw_item_use(
            self, b, screen, blink
    ):
        # PHASE 1 — scroll "[user] uses [item]!"
        if not b.item_use_scroll_done:
            lines = self.wrap_text_words(b.item_use_text, max_width=32)

            visible_chars = int(b.item_use_scroll_index)
            visible_lines = ["", "", ""]

            for line_idx, words in enumerate(lines):
                for word in words:
                    chunk = word + " "
                    if visible_chars >= len(chunk):
                        visible_lines[line_idx] += chunk
                        visible_chars -= len(chunk)
                    else:
                        visible_lines[line_idx] += chunk[:visible_chars]
                        visible_chars = 0
                        break
                if visible_chars == 0:
                    break

            self.font0.draw_text(screen, visible_lines[0], X_MENU_MAIN, Y_MENU_MAIN_0)
            self.font0.draw_text(screen, visible_lines[1], X_MENU_MAIN, Y_MENU_MAIN_1)
            self.font0.draw_text(screen, visible_lines[2], X_MENU_MAIN, Y_MENU_MAIN_2)
            return

        # PHASE 4 — "[user] uses [item]!" fully visible on line 0
        full_lines = self.wrap_text_words(b.item_use_text, max_width=32)
        y = Y_MENU_MAIN_0
        for line in full_lines:
            text = " ".join(line)
            if text:
                self.font0.draw_text(screen, text, X_MENU_MAIN, y)
            y += DAMAGE_TEXT_INCR  # same spacing you used before

        # Scroll "Recovered X HP!" on the next line
        if b.item_recover_text:
            visible_recover = b.item_recover_text[:int(b.item_recover_scroll_index)]
            self.font0.draw_text(screen, visible_recover, X_MENU_MAIN, Y_MENU_MAIN_1)

            # Confirm arrow when recovery scroll is done
            if b.item_recover_scroll_done and blink:
                screen.blit(self.cursor_sprite, (CONFIRM_ARROW_X, CONFIRM_ARROW_Y))
