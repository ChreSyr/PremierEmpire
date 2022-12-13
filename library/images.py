
import baopig as bp

f_big = bp.image.load("images/flags_big.png")
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
