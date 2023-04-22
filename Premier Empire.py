
# import sys
# sys.path.insert(0, 'C:\\Users\\symrb\\Documents\\dev\\python\\baopig')

from library.loading import set_progression, screen_size
set_progression(.05)
set_progression(.1)
set_progression(.15)
set_progression(.2)

import baopig as bp

set_progression(.3)

from library.theme import MyTheme
from library.game import Game

set_progression(.7)

app = bp.Application(name="Premier Empire", theme=MyTheme(), size=screen_size)
app.set_debug(launchtime=True)

set_progression(.8)

game = Game(app)

set_progression(1)

if __name__ == "__main__":
    app.launch()
