"""
Simple ASCII sound system placeholder that prints textual cues
"""

class ASCIISoundSystem:
    def __init__(self):
        self.enabled = True

    def initialize(self):
        # In real terminal, could use bell or curses beeps
        self.play('init')

    def play(self, name: str):
        if not self.enabled:
            return
        sounds = {
            'init': '♪ boot chime',
            'shoot': '• pew!',
            'hit': '× thud',
            'heal': '+ ting',
            'pickup': '* ding',
        }
        print(f"[SND] {sounds.get(name, name)}")

    def play_shoot(self):
        self.play('shoot')
