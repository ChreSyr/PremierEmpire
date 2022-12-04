
import baopig as bp
from language import TranslatableText, PartiallyTranslatableText
from library.loading import logo
from library.buttons import PE_Button


class BackgroundedZone(bp.Zone):
    STYLE = bp.Zone.STYLE.substyle()
    STYLE.modify(
        background_color=(176, 167, 139),
        border_width=2,
        border_color="black"
    )


class PlayZone(bp.Zone):

    def __init__(self, game):

        logo_filled = bp.Surface(logo.get_size())
        logo_filled.fill((255, 255, 255))
        logo_filled.blit(logo, (0, 0))
        bp.Zone.__init__(self, game, size=logo.get_size(), sticky="center", layer=game.game_layer,
                         background_image=logo_filled)
        self.btn = play_btn = PE_Button(self, text_id=3, center=(0, -37), refloc="midbottom",
                                                  command=bp.PrefilledFunction(game.set_todo, 1))
        self.btn.original_size = play_btn.rect.size
        play_btn.growing = True
        def anim_play_zone():
            if play_btn.growing:
                if play_btn.rect.height >= 48:
                    play_btn.growing = False
                else:
                    play_btn.resize(play_btn.rect.w+2, play_btn.rect.h+2)
            else:
                if play_btn.rect.height <= 40:
                    play_btn.growing = True
                else:
                    play_btn.resize(play_btn.rect.w-2, play_btn.rect.h-2)
        self.btn_animator = bp.RepeatingTimer(.1, anim_play_zone)


class ProgressTracker(bp.Zone):

    def __init__(self, scene, **kwargs):

        bp.Zone.__init__(self, parent=scene, size=("100%", "100%"), **kwargs)

        self.logo = bp.Image(self, image=bp.image.load("images/logo.png"), sticky="center")
        self.progress_rect = bp.Rectangle(self, color="white", ref=self.logo, size=(0, self.logo.rect.height))
        self.logo.move_in_front_of(self.progress_rect)

        self.progress = 0

    def set_progress(self, progress):

        assert 0 <= progress <= 1
        self.progress = progress
        self.progress_rect.resize_width(int(self.logo.rect.width * progress))


class TmpMessage(BackgroundedZone, bp.LinkableByMouse):

    def __init__(self, game, text_id, explain_id=None):

        BackgroundedZone.__init__(self, game, size=(300, 100), sticky="midtop", layer_level=2)
        bp.LinkableByMouse.__init__(self, game)

        msg_w = TranslatableText(self, text_id=text_id, max_width=self.rect.w - 10, align_mode="center", pos=(0, 5),
                                 sticky="midtop", font_height=self.get_style_for(bp.Text)["font_height"] + 4)
        r2 = bp.Rectangle(self, size=(self.rect.w, msg_w.rect.h + 10), color=(0, 0, 0, 0), border_width=2)
        if explain_id:
            TranslatableText(self, text_id=explain_id, max_width=self.rect.w - 10,
                             pos=(5, 5), ref=r2, refloc="bottomleft")

        self.timer = bp.Timer(3, command=self.kill)
        self.timer.start()

    def handle_linkm(self):

        self.timer.cancel()
        self.kill()


class WinnerInfoZone(bp.Zone):

    def __init__(self, game):

        bp.Zone.__init__(self, game, size=game.map.rect.size, background_color=(0, 0, 0, 63), sticky="center",
                         visible=False, layer=game.gameinfo_layer)

        self.panel = rw1 = bp.Rectangle(self, size=("40%", "40%"), sticky="center", border_width=2,
                                        border_color="black")
        self.title = PartiallyTranslatableText(self, text_id=23, get_args=(lambda : game.current_player.name_id,),
                                               font_height=self.get_style_for(bp.Text)["font_height"] + 15,
                                               max_width=rw1.rect.w - 10, align_mode="center",
                                               pos=(rw1.rect.left + 5, rw1.rect.top + 5))
        rw2 = bp.Rectangle(self, size=(rw1.rect.w, self.title.rect.h + 10),
                           pos=rw1.rect.topleft, color=(0, 0, 0, 0), border_width=2, border_color="black")  # border
        self.subtitle = TranslatableText(self, text_id=6, max_width=rw1.rect.w - 10, pos=(5, 5),
                                         ref=rw2, refloc="bottomleft")
        PE_Button(self, "OK", midbottom=(rw1.rect.centerx, rw1.rect.bottom - 5), command=self.hide)
