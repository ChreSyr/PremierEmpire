
import baopig as bp

load = lambda val: bp.image.load(f"images/{val}.png")

f = load("flags")
w, h = f.get_size()
w = w / 3
h = h / 2
FLAGS = {
    "north_america": f.subsurface(0, 0, w, h),
    "europa": f.subsurface(w, 0, w, h),
    "asia": f.subsurface(2 * w, 0, w, h),
    "south_america": f.subsurface(0, h, w, h),
    "africa": f.subsurface(w, h, w, h),
    "oceania": f.subsurface(2 * w, h, w, h),
}

f_big = load("flags_big")
w, h = f_big.get_size()
w = w / 3
h = h / 2
FLAGS_BIG = {
    "north_america": f_big.subsurface(0, 0, w, h),
    "europa": f_big.subsurface(w, 0, w, h),
    "asia": f_big.subsurface( 2 *w, 0, w, h),
    "south_america": f_big.subsurface(0, h, w, h),
    "africa": f_big.subsurface(w, h, w, h),
    "oceania": f_big.subsurface( 2 *w, h, w, h),
}

all_soldiers = load("soldiers")
w, h = all_soldiers.get_size()
w = w / 3
h = h / 2
SOLDIERS = {
    "north_america": all_soldiers.subsurface(0, 0, w, h),
    "europa": all_soldiers.subsurface(w, 0, w, h),
    "asia": all_soldiers.subsurface(2 * w, 0, w, h),
    "south_america": all_soldiers.subsurface(0, h, w, h),
    "africa": all_soldiers.subsurface(w, h, w, h),
    "oceania": all_soldiers.subsurface(2 * w, h, w, h),
    # "black": load("images/builds.png").subsurface(38, 38, 14, 14)
}

boat_back = load("boat_back")
boat_front = load("boat_front")
boat_front_hover = load("boat_front_hover")

map_borders = load("map_borders")
