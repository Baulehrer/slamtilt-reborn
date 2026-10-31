#!/usr/bin/env python3
"""Earn Werewolf then Brain on one original Windows game; no rule-state writes."""
from demon_video_oracle import Video


class ConsecutiveVideo(Video):
    second = False

    def mark(self, label):
        return super().mark(('second_' if self.second else '') + label)

    def perform(self, case):
        if case != 'video-consecutive':
            raise ValueError(case)
        # Idle werewolf fails naturally, after the existing four-moon bank and
        # already-armed-bank guard. The ball actually returns before rearming.
        super().perform('video-wolf-idle')
        self.second = True
        self.case = 'video-brain-win'
        self.moons()
        self.admit(True)
        self.tap('enter')
        self.mark('early_enter_guard')
        start = self.tick
        while self.m.get(0x46d594) < 0x80000000:
            self.step()
            assert self.tick - start < 10000, 'Brain choice not offered'
        self.mark('choice_ready')
        target = next(i for i in range(5) if self.m.get(0x46d554 + 4 * i))
        while self.m.get(0x46d584) != target:
            self.tap('left' if self.m.get(0x46d584) > target else 'right')
        self.mark('choice_selected')
        self.tap('enter')
        self.mark('choice_confirmed')
        start = self.tick
        while self.video()[-1]:
            self.step()
            assert self.tick - start < 16000, 'Brain video did not end'
        self.mark('video_ended')
        self.free()
        self.park(220)
        self.mark('video_returned')


if __name__ == '__main__':
    ConsecutiveVideo().generate_rewards('video-consecutive')
