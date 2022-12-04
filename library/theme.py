
import baopig as bp
from baopig.prefabs.themes import DarkTheme


class MyTheme(DarkTheme):

    def __init__(self):

        DarkTheme.__init__(self)

        self.colors.content = (176, 167, 139)
        self.colors.font_opposite = self.colors.font
        self.colors.font = "black"

        self.set_style_for(bp.Text, font_file="kirsty-bold", font_height=18)

def set_cursor(cursor_name):
    bp.pygame.mouse.set_cursor((5, 0), mouses[cursor_name])


mouses_full = bp.image.load("images/hands.png")
mouses = {
    "default": mouses_full.subsurface(0, 0, 32, 32),
    "Jaune": mouses_full.subsurface(0, 32, 32, 32),
    "Bleu": mouses_full.subsurface(0, 64, 32, 32),
    "Vert": mouses_full.subsurface(0, 96, 32, 32),
    "Rouge": mouses_full.subsurface(0, 128, 32, 32),
    "Gris": mouses_full.subsurface(0, 160, 32, 32),
    "Violet": mouses_full.subsurface(0, 192, 32, 32),
}
set_cursor("default")
