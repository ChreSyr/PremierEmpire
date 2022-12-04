
import baopig as bp
import pygame
import googletrans
from language import TranslatableText, PartiallyTranslatableText, dicts, lang_manager, translator
from library.loading import logo, fullscreen_size, screen_sizes
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


class SettingsZone(BackgroundedZone):

    def __init__(self, game, behind=None):

        BackgroundedZone.__init__(self, game, padding=(90, 60), spacing=20, sticky="center",
                                  layer=game.extra_layer)

        self.game = game
        self.behind = behind

        if behind:
            PE_Button(self, text="<", pos=(10, 10), layer_level=2, translatable=False, size=(40, 40),
                      command=self.hide)

        PE_Button(self, text="X", pos=(-10, 10), sticky="topright", layer_level=2, translatable=False, size=(40, 40),
                  background_color=(150, 20, 20), command=self.close_settings)

        self.main_layer = bp.Layer(self)

    def pack_and_adapt(self):

        self.main_layer.pack()
        self.adapt(self.main_layer)
        if self.behind is not None:
            self.resize(width=max(self.rect.width, self.behind.rect.width),
                        height=max(self.rect.height, self.behind.rect.height))

    def close_settings(self):
        if self.behind is not None:
            self.behind.close_settings()
        self.hide()


class SettingsMainZone(SettingsZone):

    def __init__(self, game):

        SettingsZone.__init__(self, game)

        self.sail = bp.Circle(game, (0, 0, 0, 63), radius=120, visible=False, sticky="center", layer_level=2)
        self.signal.HIDE.connect(self.close_sail, owner=self.sail)

        def newgame():
            self.hide()
            self.game.set_todo(1)
            self.newgame_btn.disable()
        self.newgame_btn = PE_Button(parent=self, text_id=2, command=newgame)
        self.newgame_btn.disable()

        self.tuto_btn = PE_Button(parent=self, text_id=7)

        connection_zone = bp.Zone(self)
        self.connection_title = TranslatableText(connection_zone, text_id=9, sticky="midtop", align_mode="center")
        def toggle_connection():
            if self.connected_to_network:
                self.connected_to_network = False
                self.connection_btn.text_widget.set_ref_text(11)
            else:
                try:
                    googletrans.Translator.translate(translator, "Bonjour", "fr", "en")
                except Exception:
                    return
                self._connected_to_network = True
                lang_manager.update_language()
                self.connection_btn.text_widget.set_ref_text(10)
        self.connection_btn = PE_Button(parent=connection_zone, text_id=10, command=toggle_connection,
                                        pos=(0, self.connection_title.rect.bottom + 3))
        connection_zone.adapt()

        lang_zone = bp.Zone(self)
        lang_title = TranslatableText(lang_zone, text_id=12, sticky="midtop")
        self.lang_btn = PE_Button(parent=lang_zone, text=dicts.get(0, lang_manager.language),
                                  pos=(0, lang_title.rect.bottom + 3), translatable=False)
        lang_zone.adapt()

        resolution_zone = bp.Zone(self)
        resolution_title = TranslatableText(resolution_zone, text_id=46, sticky="midtop")
        self.resolution_btn = PE_Button(parent=resolution_zone, text=f"{game.rect.width} × {game.rect.height}",
                                        pos=(0, resolution_title.rect.bottom + 3), translatable=False)
        resolution_zone.adapt()

        PE_Button(parent=self, text_id=1, command=self.application.exit)
        self.pack_and_adapt()

        def sail_animate():
            if self.is_visible:
                if self.sail.radius < 480:
                    self.sail.set_radius(self.sail.radius + 60)
                else:
                    self.sail.set_radius(sum(fullscreen_size) / 2)
                    self.sail_animator.cancel()
            else:
                if self.sail.radius > 480:
                    self.sail.set_radius(480)
                else:
                    self.sail.set_radius(self.sail.radius - 60)
                if self.sail.radius <= 0:
                    self.sail_animator.cancel()
                    self.sail.hide()
        self.sail_animator = bp.RepeatingTimer(.03, sail_animate)

        self.hide()

    def close_sail(self):
        if not self.sail_animator.is_running:
            self.sail_animator.start()

    def toggle(self):

        if self.is_visible:
            self.hide()
            self.close_sail()
        else:
            self.show()
            self.sail.set_radius(120)
            self.sail.show()
            if not self.sail_animator.is_running:
                self.sail_animator.start()


class SettingsLanguageZone(SettingsZone):

    def __init__(self, game):

        SettingsZone.__init__(self, game, behind=game.settings_zone)

        class LangBtn(PE_Button):

            def __init__(btn, id, text=None):

                if id not in dicts:
                    dicts.create(id)
                if text is None:
                    text = translator.translate(googletrans.LANGUAGES[id], src="en", dest=id).capitalize()
                PE_Button.__init__(btn, parent=self, text=text, translatable=False)
                btn.id = id

            def handle_validate(btn):

                lang_manager.set_language(btn.id)
                if not game.connected_to_network:
                    TmpMessage(self, text_id=34, explain_id=37)
                self.behind.lang_btn.text_widget.set_text(btn.text)
                self.behind.lang_btn.text_widget2.set_text(btn.text)

                memory_lang_id = btn.id
                import importlib
                try:
                    importlib.import_module("language.dict_" + btn.id)
                except ModuleNotFoundError:
                    memory_lang_id = lang_manager.ref_language
                game.memory.set_lang(memory_lang_id)

                self.hide()

        # LangBtn(id="es", text="Español")
        LangBtn(id="en", text="English")
        LangBtn(id="fr", text="Français")
        # LangBtn(id="it", text="Italiano")
        # LangBtn(id="la", text="Latinus")

        self.pack_and_adapt()

        self.behind.lang_btn.command = self.show


class SettingsResolutionZone(SettingsZone):

    def __init__(self, game):

        SettingsZone.__init__(self, game, behind=game.settings_zone)

        class ResolutionBtn(PE_Button):

            def __init__(btn, resolution=None):

                if resolution is None:
                    PE_Button.__init__(btn, self, text_id=47)
                else:
                    PE_Button.__init__(btn, self, text=f"{resolution[0]} × {resolution[1]}",
                                       translatable=False)
                btn.resolution = resolution

            def handle_validate(btn):

                if btn.resolution is None:
                    self.application.set_default_size(screen_sizes[0])
                    pygame.display.set_mode(screen_sizes[0], pygame.FULLSCREEN)
                    self.behind.resolution_btn.text_widget.set_text(btn.text)
                    self.behind.resolution_btn.text_widget2.set_text(btn.text)
                else:
                    self.application.set_default_size(btn.resolution)

        ResolutionBtn()
        for i in range(min(len(screen_sizes), 7)):
            ResolutionBtn(screen_sizes[i])

        self.pack_and_adapt()

        self.behind.resolution_btn.command = self.show


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
