
import random
import baopig as bp


class SoundManager:

    def __init__(self, game):

        self.game = game

        self.click = bp.mixer.Sound("sounds/256116__kwahmah_02__click_2.wav")
        self.soldier_grunt = bp.mixer.Sound("sounds/427972__lipalearning__male-grunt_10_2.wav")
        self.build = bp.mixer.Sound("sounds/388269__sami_kullstrom__knocking-on-a-wood-table.wav")
        self.flag = bp.mixer.Sound("sounds/244976__ani_music__wing-flap-flag-flapping-4a_2.wav")
        self.change_gold = bp.mixer.Sound("sounds/439538__ethanchase7744__epic-sword-clang-2_2.wav")
        self.conquest = bp.mixer.Sound("sounds/384882__ali_6868__knight-left-footstep-on-gravel-3-with-chainmail.wav")
        self.win = bp.mixer.Sound("sounds/60444__jobro__tada2_2.wav")
        self.defeat = bp.mixer.Sound("sounds/455396__insanity54__accidentally-punching-the-floor_3.wav")

        self.musics = {
            "Oasis City": "sounds/614838__quadraslayer__medieval-city-middle-east.mp3",
            "The Tavern": "sounds/615166__quadraslayer__medieval-tavern.mp3",
        }
        bp.mixer.music.load(random.choice(tuple(self.musics.values())))

        self._music = (bp.mixer.music,)

        self._sfx = (
            self.soldier_grunt, self.build, self.flag, self.change_gold, self.conquest, self.win, self.defeat,
        )

        self._ui = (
            self.click,
        )

        self._master = self._music + self._sfx + self._ui

        self.set_volume('master', game.memory.volume_master, from_init=True)
        self.set_volume('music', game.memory.volume_music, from_init=True)
        self.set_volume('sfx', game.memory.volume_sfx, from_init=True)
        self.set_volume('ui', game.memory.volume_ui, from_init=True)

    def set_music(self, music_name):

        bp.mixer.music.load(self.musics[music_name])
        self.start_music()

    def set_volume(self, target, val, from_init=False):

        for element in getattr(self, '_' + target):
            element.set_volume(val)

        if from_init is False:
            self.game.memory.set(f"volume_{target}", val)

    @staticmethod
    def start_music():

        bp.mixer.music.play(loops=-1)

    @staticmethod
    def stop_music():

        bp.mixer.music.stop()
