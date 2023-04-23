
import random
import baopig as bp


class SoundManager:

    def __init__(self, game):

        self.game = game

        self.click = bp.mixer.Sound("sounds/256116__kwahmah_02__click_2.wav")
        self.soldier_grunt = bp.mixer.Sound("sounds/427972__lipalearning__male-grunt_10.wav")
        self.build = bp.mixer.Sound("sounds/388269__sami_kullstrom__knocking-on-a-wood-table.wav")
        self.flag = bp.mixer.Sound("sounds/244976__ani_music__wing-flap-flag-flapping-4a_2.wav")
        self.change_gold = bp.mixer.Sound("sounds/439538__ethanchase7744__epic-sword-clang-2_2.wav")
        self.conquest = bp.mixer.Sound("sounds/384882__ali_6868__knight-left-footstep-on-gravel-3-with-chainmail.wav")
        self.win = bp.mixer.Sound("sounds/60444__jobro__tada2_2.wav")
        self.defeat = bp.mixer.Sound("sounds/455396__insanity54__accidentally-punching-the-floor_3.wav")

        self.musics = (
            "sounds/614838__quadraslayer__medieval-city-middle-east.mp3",
            "sounds/615166__quadraslayer__medieval-tavern.mp3",
        )
        bp.mixer.music.load(random.choice(self.musics))

    @staticmethod
    def start_music():

        bp.mixer.music.play(loops=10)
