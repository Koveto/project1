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
    
    def draw_simple_scroll(self, screen, scroll_text, scroll_index, scroll_done, blink):
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

        # Draw text
        self.font0.draw_text(screen, visible_lines[0], X_MENU_MAIN, Y_MENU_MAIN_0)
        self.font0.draw_text(screen, visible_lines[1], X_MENU_MAIN, Y_MENU_MAIN_1)
        self.font0.draw_text(screen, visible_lines[2], X_MENU_MAIN, Y_MENU_MAIN_2)

        # Draw arrow if scroll finished
        if scroll_done and blink:
            screen.blit(self.cursor_sprite, (CONFIRM_ARROW_X, CONFIRM_ARROW_Y))

    
    def draw_damaging_enemy(
            self, screen,
            scroll_text, scroll_index, scroll_done,
            damage_done, affinity_done,
            affinity_text, affinity_scroll_index,
            affinity_scroll_done,
            damage_text, damage_scroll_index, damage_scroll_done,
            blink
    ):
        # =========================================================
        # CASE A — NON‑NEUTRAL AFFINITY (affinity_text is not None)
        # =========================================================
        if damage_done and affinity_text:

            # PHASE 3 — Affinity text scrolling
            if not affinity_done:
                visible_aff = affinity_text[:int(affinity_scroll_index)]
                self.font0.draw_text(screen, visible_aff, X_MENU_MAIN, Y_MENU_MAIN_0)
                return

            # PHASE 4 — Affinity fully displayed, now scroll damage text
            self.font0.draw_text(screen, affinity_text, X_MENU_MAIN, Y_MENU_MAIN_0)

            # Damage text scrolls only after affinity is done
            visible_dmg = damage_text[:int(damage_scroll_index)]
            self.font0.draw_text(screen, visible_dmg, X_MENU_MAIN, Y_MENU_MAIN_1)

            # Confirm arrow only when BOTH scrolls are done
            if affinity_scroll_done and damage_scroll_done and blink:
                screen.blit(self.cursor_sprite, (CONFIRM_ARROW_X, CONFIRM_ARROW_Y))

            return

        # =========================================================
        # CASE B — NEUTRAL AFFINITY (affinity_text is None)
        # =========================================================
        if damage_done and not affinity_text:
            # Draw the original attack text (already fully visible)
            full_word_lines = self.wrap_text_words(scroll_text, max_width=32)

            used_lines = 0
            y = Y_MENU_MAIN_0

            for line in full_word_lines:
                text = " ".join(line)
                if text:
                    self.font0.draw_text(screen, text, X_MENU_MAIN, y)
                    used_lines += 1
                y += DAMAGE_TEXT_INCR

            # Now draw the damage text on the NEXT free line
            dmg_visible = damage_text[:int(damage_scroll_index)]
            dmg_y = Y_MENU_MAIN_0 + used_lines * DAMAGE_TEXT_INCR
            self.font0.draw_text(screen, dmg_visible, X_MENU_MAIN, dmg_y)

            # Confirm arrow only after damage scroll finishes
            if damage_scroll_done and blink:
                screen.blit(self.cursor_sprite, (CONFIRM_ARROW_X, CONFIRM_ARROW_Y))

            return

        # =========================================================
        # CASE C — PRE‑DAMAGE: Attack text scrolls normally
        # =========================================================
        full_word_lines = self.wrap_text_words(scroll_text, max_width=32)

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
        if scroll_done and not damage_done:
            return

        # PHASE 1.5 — Scroll done, HP anim not started yet
        if scroll_done and not damage_done and not self.damage_started:
            if blink:
                screen.blit(self.cursor_sprite, (CONFIRM_ARROW_X, CONFIRM_ARROW_Y))
            return
    
    def draw_item_use(
            self, screen,
            use_text, use_scroll_index, use_scroll_done,
            recover_text, recover_scroll_index, recover_scroll_done,
            blink
    ):
        # PHASE 1 — scroll "[user] uses [item]!"
        if not use_scroll_done:
            lines = self.wrap_text_words(use_text, max_width=32)

            visible_chars = int(use_scroll_index)
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
        full_lines = self.wrap_text_words(use_text, max_width=32)
        y = Y_MENU_MAIN_0
        for line in full_lines:
            text = " ".join(line)
            if text:
                self.font0.draw_text(screen, text, X_MENU_MAIN, y)
            y += DAMAGE_TEXT_INCR  # same spacing you used before

        # Scroll "Recovered X HP!" on the next line
        if recover_text:
            visible_recover = recover_text[:int(recover_scroll_index)]
            self.font0.draw_text(screen, visible_recover, X_MENU_MAIN, Y_MENU_MAIN_1)

            # Confirm arrow when recovery scroll is done
            if recover_scroll_done and blink:
                screen.blit(self.cursor_sprite, (CONFIRM_ARROW_X, CONFIRM_ARROW_Y))

    def draw_enemy_attack_text(self, screen, scroll_text, scroll_index, scroll_done, blink):
        # Word-wrap to 32 characters
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

        # Draw the wrapped text
        self.font0.draw_text(screen, visible_lines[0], X_MENU_MAIN, Y_MENU_MAIN_0)
        self.font0.draw_text(screen, visible_lines[1], X_MENU_MAIN, Y_MENU_MAIN_1)
        self.font0.draw_text(screen, visible_lines[2], X_MENU_MAIN, Y_MENU_MAIN_2)

        # Draw confirm arrow sprite (same behavior as draw_simple_scroll)
        if scroll_done and blink:
            screen.blit(self.cursor_sprite, (CONFIRM_ARROW_X, CONFIRM_ARROW_Y))





