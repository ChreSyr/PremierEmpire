
import baopig as bp
from library.images import FLAGS, SOLDIERS
from library.zones import BackgroundedZone
from library.region import Boat, front, back


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
        self.has_flag = False
        self.zone = TransferZone(game, self)

    amount = property(lambda self: self._amount)

    def add_flag(self):

        self.has_flag = True
        self.zone.flag.set_surface(FLAGS[self.owner.continent])
        self.zone.flag.wake()
        self.zone.flag.layer.move_on_top(self.zone.flag)
        self.zone.pack(axis="horizontal", adapt=True)
        self.zone.set_under_mouse()

    def end(self):

        self.zone.hide()
        self.from_region = None
        self.destination_names = None
        self.owner = None
        self.mode = None
        self._amount = 0
        self.boat = None
        self.has_flag = False

    def set_amount(self, amount):

        self._amount = amount
        self.zone.title.set_text(str(self.amount))
        self.zone.pack(axis="horizontal", adapt=True)

    def set_mode(self, mode, amount):

        self.mode = mode
        self._amount = amount
        self.zone.set_mode(mode)


class TransferZone(bp.Zone):

    def __init__(self, game, transfer):

        bp.Zone.__init__(self, game, visible=False, layer=game.extra_layer)

        self.transfer = transfer

        # Soldiers mode
        self.soldiers_zone = BackgroundedZone(self, padding=4, spacing=4)
        self.title = bp.Text(self.soldiers_zone, "")
        self.icon = bp.Image(self.soldiers_zone, SOLDIERS["asia"])

        # Boat mode
        self.boat_zone = bp.Zone(self, size=(front.get_width(), front.get_height() + Boat.TOP_PADDING))
        self.back = bp.Image(self.boat_zone, image=back,
                             pos=(front.get_width() / 2 - back.get_width() / 2, Boat.TOP_PADDING))
        self.soldiers_in_boat_zone = bp.Zone(self.boat_zone, size=(0, 22), sticky="midtop", spacing=-1)
        self.soldiers_in_boat = ()
        for _ in range(self.scene.MAX_SOLDIERS_IN_BOAT):
            soldier = bp.Image(self.soldiers_in_boat_zone, image=SOLDIERS["north_america"])
            soldier.sleep()
            self.soldiers_in_boat += (soldier,)
        self.front = bp.Image(self.boat_zone, image=front, pos=(0, Boat.TOP_PADDING))

        self.flag = bp.Image(self, FLAGS["north_america"])
        self.flag.sleep()

        bp.mouse.signal.MOUSEMOTION.connect(self.handle_mouse_motion, owner=self)

    def handle_mouse_motion(self):

        if self.is_visible:
            self.set_under_mouse()

    def set_mode(self, mode):

        if mode == Transfer.SOLDIERS_MODE:

            self.soldiers_zone.wake()
            self.boat_zone.sleep()

            self.icon.set_surface(self.transfer.owner.soldier_icon)
            self.title.set_text(str(self.transfer.amount))
            self.soldiers_zone.pack(axis="horizontal", adapt=True)
            self.adapt()
            self.set_under_mouse()

        elif mode == Transfer.BOAT_MODE:

            self.soldiers_zone.sleep()
            self.boat_zone.wake()

            for i, soldier_image in enumerate(self.soldiers_in_boat):
                if i < self.transfer.amount:
                    soldier_image.set_surface(self.transfer.owner.soldier_icon)
                    soldier_image.wake()
                else:
                    soldier_image.sleep()
            self.soldiers_in_boat_zone.pack(axis="horizontal")
            self.soldiers_in_boat_zone.adapt()

            self.adapt()
            self.set_under_mouse()

        else:
            raise PermissionError(f"Wrong mode : {mode}")

        self.show()

    def set_under_mouse(self):

        if self.scene.sail.need_to_be_open():
            return

        self.layer.move_on_top(self)
        self.set_pos(midtop=(bp.mouse.x - self.parent.abs_rect.left,
                             bp.mouse.y + 30 - self.parent.abs_rect.top))
