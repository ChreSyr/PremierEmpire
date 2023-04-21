
import baopig as bp
from library.images import SOLDIERS
from library.zones import BackgroundedZone


class Transfer:

    SOLDIERS_MODE = 0
    BOAT_MODE = 1

    def __init__(self, game):

        self.game = game
        self.from_region = None
        self.destination_names = None
        self.owner = None
        self.mode = None
        self._amount = 0
        self.boat = None
        self.zone = TransferZone(game)

    amount = property(lambda self: self._amount)

    def end(self):

        self.zone.hide()
        self.from_region = None
        self.destination_names = None
        self.owner = None
        self.mode = None
        self._amount = 0
        self.boat = None

    def set_amount(self, amount):

        self._amount = amount
        self.zone.title.set_text(str(self.amount))
        self.zone.pack(axis="horizontal", adapt=True)

    def set_mode(self, mode, amount):

        self.mode = mode
        self._amount = amount
        self.zone.set_mode(mode)


class TransferZone(bp.Zone):

    STYLE = bp.Zone.STYLE.substyle()
    STYLE.modify(
        padding=4,
        spacing=4,
        border_color=BackgroundedZone.STYLE["border_color"],
    )

    def __init__(self, game):

        bp.Zone.__init__(self, game, visible=False, layer=game.extra_layer)

        # Soldiers mode
        self.title = bp.Text(self, "")
        self.icon = bp.Image(self, SOLDIERS["asia"])

        bp.mouse.signal.MOUSEMOTION.connect(self.handle_mouse_motion, owner=self)

    def handle_mouse_motion(self):

        if self.is_visible:
            self.set_under_mouse()

    def set_mode(self, mode):

        if mode == Transfer.SOLDIERS_MODE or mode == Transfer.BOAT_MODE:
            self.set_background_color(BackgroundedZone.STYLE["background_color"])
            self.set_border(width=BackgroundedZone.STYLE["border_width"])

            game = self.scene
            self.icon.set_surface(game.transfer.owner.soldier_icon)
            self.title.set_text(str(game.transfer.amount))
            self.pack(axis="horizontal", adapt=True)
            self.set_under_mouse()

        elif mode == Transfer.BOAT_MODE:
            self.set_background_color((0, 0, 0, 0))
            self.set_border(width=0)

        else:
            raise PermissionError(f"Wrong mode : {mode}")

        self.show()

    def set_under_mouse(self):

        if self.scene.sail.need_to_be_open():
            return

        self.layer.move_on_top(self)
        self.set_pos(midtop=(bp.mouse.x - self.parent.abs_rect.left,
                             bp.mouse.y + 30 - self.parent.abs_rect.top))
