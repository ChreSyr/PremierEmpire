
import sys

import pygame.display

sys.path.insert(0, 'C:\\Users\\symrb\\Documents\\dev\\python\\baopig')

from library.loading import set_progression
set_progression(.05)
set_progression(.1)
set_progression(.15)
set_progression(.2)

import baopig as bp

set_progression(.3)

from library.theme import MyTheme
from library.game import Game, memory

set_progression(.7)

class PremierEmpireApp(bp.Application):

    def _update_display(self):

        super()._update_display()
        if self.size == pygame.display.list_modes()[0]:
            memory.set("screen_size", "fullscreen")
        else:
            memory.set("screen_size", self.size)

app = PremierEmpireApp(name="Premier Empire", theme=MyTheme(), size=memory.screen_size.get())
app.set_debug(launchtime=True)

set_progression(.8)

game = Game(app)

set_progression(1)

if __name__ == "__main__":
    app.launch()
