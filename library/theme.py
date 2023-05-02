
import baopig as bp
import pygame
from baopig.prefabs.themes import DarkTheme
from library.images import image


class MyTheme(DarkTheme):

    def __init__(self):

        DarkTheme.__init__(self)

        self.colors.content = (176, 167, 139)
        self.colors.font_opposite = self.colors.font
        self.colors.font = "black"

        self.set_style_for(bp.Text, font_file="kirsty-bold", font_height=18)

def set_cursor(cursor_name):
    try:
        bp.pygame.mouse.set_cursor((5, 0), image.mouses[cursor_name])
    except pygame.error as e:
        bp.LOGGER.warning(e)


set_cursor("default")
