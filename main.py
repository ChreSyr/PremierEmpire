
import os

os.chdir(os.path.dirname(os.path.realpath(__file__)))  # executable from console
import sys
sys.path.insert(0, 'C:\\Users\\symrb\\Documents\\python\\baopig')

from library.loading import set_progression, fullscreen_size
set_progression(.05)
set_progression(.1)
set_progression(.15)
set_progression(.2)

import baopig as bp

set_progression(.3)

from library.theme import MyTheme
from library.game import Game

set_progression(.7)

app = bp.Application(name="PremierEmpire", theme=MyTheme(), size=fullscreen_size)
app.set_debug(launchtime=True)

set_progression(.8)

game = Game(app)

set_progression(1)

if __name__ == "__main__":
    app.launch()
