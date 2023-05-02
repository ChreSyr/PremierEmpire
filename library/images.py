
from library.loading import load

class ImagesConatiner:

    def __init__(self):

        # MOUSE
        self.mouses_full = load("hands")
        self.mouses = {
            "default": self.mouses_full.subsurface(0, 0, 32, 32),
            "Jaune": self.mouses_full.subsurface(0, 32, 32, 32),
            "Bleu": self.mouses_full.subsurface(0, 64, 32, 32),
            "Vert": self.mouses_full.subsurface(0, 96, 32, 32),
            "Rouge": self.mouses_full.subsurface(0, 128, 32, 32),
            "Gris": self.mouses_full.subsurface(0, 160, 32, 32),
            "Violet": self.mouses_full.subsurface(0, 192, 32, 32),
        }

        # PACKED IMAGES
        self.FLAGS = self.load_packed("flags")
        self.FLAGS_BIG = self.load_packed("flags_big")
        self.SOLDIERS = self.load_packed("soldiers")

        # MAP
        self.map = load("map")
        self.map_borders = load("map_borders")

        # BUTTON
        self.raw_back = load("btn_back")
        self.raw_window = load("btn_window")

        # STRUCTURE
        self.BUILDS = load("builds")
        self.WIP = self.BUILDS.subsurface(0, 0, 30, 30)
        self.DONE = self.BUILDS.subsurface(30, 0, 30, 30)
        self.MINE = self.BUILDS.subsurface(0, 30, 30, 30)
        self.CAMP = self.BUILDS.subsurface(30, 30, 30, 30)

        # BOAT
        self.boat_back = load("boat_back")
        self.boat_front = load("boat_front")
        self.boat_front_hover = load("boat_front_hover")

    def load_packed(self, name):

        full = load(name)
        w, h = full.get_size()
        w = w / 3
        h = h / 2
        return {
            "north_america": full.subsurface(0, 0, w, h),
            "europa": full.subsurface(w, 0, w, h),
            "asia": full.subsurface(2 * w, 0, w, h),
            "south_america": full.subsurface(0, h, w, h),
            "africa": full.subsurface(w, h, w, h),
            "oceania": full.subsurface(2 * w, h, w, h),
        }

image = ImagesConatiner()