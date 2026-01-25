import math
from constants import *
from battle.battle_constants import *

class AnimationRenderer:
    def __init__(self):
        self.anim_frame = 0

    def update(self):
        self.anim_frame += 1

    def get_bounce_offsets(self):
        poke_offset = int(AMP * math.sin(self.anim_frame * SPEED))
        hp_offset = int(-AMP * math.sin(self.anim_frame * SPEED + PHASE))
        return poke_offset, hp_offset

    def get_blink(self):
        return (self.anim_frame // 10) % 2 == 0
