
import random

import baopig as bp
import pygame
load = bp.image.load

from library.loading import set_progression, fullscreen_size, screen_sizes

import googletrans
from language import TranslatableText, PartiallyTranslatableText, dicts, lang_manager, translator

set_progression(.4)

from library.memory import Memory
from library.theme import set_cursor
from library.buttons import PE_Button, RegionInfoButton
from library.player import Player
from library.zones import BackgroundedZone, PlayZone, TmpMessage, WinnerInfoZone
from library.region import Region
from library.map import Map

set_progression(.5)


class Game(bp.Scene):

    def __init__(self, app):

        bp.Scene.__init__(self, app, background_color=(96, 163, 150))

        self.players = {}
        self.regions = {}
        self.regions_list = None
        self.flags = []
        self.current_player_id = 0
        self.turn_index = 0  # 0 is the setup, 1 is the first turn
        self.last_selected_region = None

        # MEMORY
        self.memory = Memory()
        if self.memory.lang_id != lang_manager.ref_language:
            dicts.create(self.memory.lang_id)
            lang_manager.set_language(self.memory.lang_id)

        # LAYERS
        self.game_layer = bp.Layer(self, level=1, weight=2)
        self.gameinfo_layer = bp.Layer(self, level=1, weight=3)
        self.gametuto_layer = bp.Layer(self, level=1, weight=4)
        self.extra_layer = bp.Layer(self, level=2, weight=2)
        self.progress_layer = bp.Layer(self, level=2, weight=3)

        # NETWORK
        self._connected_to_network = True

        # TUTORIAL
        self.tutoring = False
        self.tuto_text = 38
        def create_tuto_zone():
            self.tutoring = True
            self.tuto_btn.command = switch_tuto
            self.tuto_btn.text_widget.set_ref_text(8)
            self.tuto_zone = hibou_zone = bp.Zone(self, size=(305, 500), sticky="bottomright",
                                                  layer=self.gametuto_layer)
            hibou1 = bp.Image(hibou_zone, load("images/hibou1.png"), sticky="bottomright", pos=(-30, 50))
            hibou2 = bp.Image(hibou_zone, load("images/hibou2.png"), sticky="bottomright", pos=(-30, 50), visible=False)
            hibou3 = bp.Image(hibou_zone, load("images/hibou3.png"), sticky="bottomright", pos=(-30, 50), visible=False)
            bulle = bp.Image(hibou_zone, load("images/hibou_bulle.png"), midbottom=hibou1.rect.midtop)
            self.tuto_text = TranslatableText(hibou_zone, text_id=self.tuto_text,
                                              pos=(bulle.rect.left + 10, bulle.rect.top + 10),
                                              max_width=bulle.rect.w - 20, align_mode="center")
            def animate_hibou():
                if hibou1.is_visible:
                    hibou1.hide()
                    hibou2.show()
                    self.hibou_animator.set_interval(.45)
                    self.hibou_animator.start()
                elif hibou2.is_visible:
                    hibou2.hide()
                    hibou3.show()
                    self.hibou_animator.start()
                else:
                    hibou3.hide()
                    hibou1.show()
                    self.hibou_animator.set_interval(3 + random.random() * 3)
                    self.hibou_animator.start()
            self.hibou_animator = bp.Timer(.45, animate_hibou)
            self.tuto_zone.signal.HIDE.connect(self.hibou_animator.cancel, owner=None)
            self.tuto_zone.signal.SHOW.connect(self.hibou_animator.start, owner=None)
        def switch_tuto():
            if self.tutoring is False:
                self.tuto_btn.text_widget.set_ref_text(8)
                self.hibou_animator.set_interval(.45)
                self.tuto_zone.show()
                self.tutoring = True
            else:
                self.tuto_btn.text_widget.set_ref_text(7)
                self.tuto_zone.hide()
                self.tutoring = False

        # PARAMETERS
        def close_paramsail():
            if not self.paramsail_animator.is_running:
                self.paramsail_animator.start()
        def toggle_param():
            if param_zone.is_visible:
                param_zone.hide()
                close_paramsail()
            else:
                param_zone.show()
                self.paramsail.set_radius(120)
                self.paramsail.show()
                if not self.paramsail_animator.is_running:
                    self.paramsail_animator.start()
        self.paramsail = bp.Circle(self, (0, 0, 0, 63), radius=120, visible=False, sticky="center", layer_level=2)
        param_zone = BackgroundedZone(self, visible=False, padding=(90, 60, 90, 60), spacing=20, sticky="center",
                                      layer=self.extra_layer)
        param_zone.signal.HIDE.connect(close_paramsail, owner=self.paramsail)
        PE_Button(param_zone, text="X", pos=(-10, 10), sticky="topright", layer_level=2, translatable=False,
                  command=param_zone.hide, size=(40, 40), background_color=(150, 20, 20))
        def newgame():
            param_zone.hide()
            self.set_todo(1)
            self.newgame_btn.disable()
        self.newgame_btn = PE_Button(parent=param_zone, text_id=2, command=newgame)
        self.newgame_btn.disable()
        self.tuto_btn = PE_Button(parent=param_zone, text_id=7, command=create_tuto_zone)
        connection_zone = bp.Zone(param_zone)
        self.connection_title = TranslatableText(connection_zone, text_id=9, sticky="midtop", align_mode="center")
        def toggle_connection():
            if self.connected_to_network:
                self.connected_to_network = False
                self.connection_btn.text_widget.set_ref_text(11)
                # if lang_manager.language == "fr":
                #     self.connection_btn.text_widget.set_text("Reconnecter")
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
        lang_zone = bp.Zone(param_zone)
        lang_title = TranslatableText(lang_zone, text_id=12, sticky="midtop")
        self.lang_btn = PE_Button(parent=lang_zone, text=dicts.get(0, lang_manager.language),
                                  pos=(0, lang_title.rect.bottom + 3), translatable=False)
        lang_zone.adapt()
        resolution_zone = bp.Zone(param_zone)
        resolution_title = TranslatableText(resolution_zone, text_id=46, sticky="midtop")
        self.resolution_btn = PE_Button(parent=resolution_zone, text=f"{self.rect.width} × {self.rect.height}",
                                        pos=(0, resolution_title.rect.bottom + 3), translatable=False)
        resolution_zone.adapt()
        PE_Button(parent=param_zone, text_id=1, command=app.exit)
        param_zone.default_layer.pack()
        param_zone.adapt(param_zone.default_layer)
        def paramsail_animate():
            if param_zone.is_visible:
                if self.paramsail.radius < 480:
                    self.paramsail.set_radius(self.paramsail.radius + 60)
                else:
                    self.paramsail.set_radius(sum(fullscreen_size) / 2)
                    self.paramsail_animator.cancel()
            else:
                if self.paramsail.radius > 480:
                    self.paramsail.set_radius(480)
                else:
                    self.paramsail.set_radius(self.paramsail.radius - 60)
                if self.paramsail.radius <= 0:
                    self.paramsail_animator.cancel()
                    self.paramsail.hide()
        self.paramsail_animator = bp.RepeatingTimer(.03, paramsail_animate)
        self.settings_btn = PE_Button(self, text_id=13, command=toggle_param, layer=self.extra_layer)
        self.settings_btn.move_behind(self.paramsail)

        # LANGUAGE
        lang_manager.game = self
        def create_lang_choose_zone():
            with bp.paint_lock:
                translator.game = self
                lang_choose_zone = BackgroundedZone(self, padding=(90, 60), spacing=20, sticky="center",
                                                    layer=self.extra_layer)
                PE_Button(lang_choose_zone, text="<", pos=(10, 10), layer_level=2, translatable=False, size=(40, 40),
                          command=lang_choose_zone.hide)
                PE_Button(lang_choose_zone, text="X", pos=(-10, 10), sticky="topright", layer_level=2,
                          translatable=False, size=(40, 40), background_color=(150, 20, 20),
                          command=bp.PackedFunctions(lang_choose_zone.hide, param_zone.hide))
                self.lang_btn.command = lang_choose_zone.show
                class LangBtn(PE_Button):
                    def __init__(btn, id, text=None):
                        if id not in dicts:
                            dicts.create(id)
                        if text is None:
                            text = translator.translate(googletrans.LANGUAGES[id], src="en", dest=id).capitalize()
                        PE_Button.__init__(btn, parent=lang_choose_zone, text=text, translatable=False)
                        btn.id = id
                    def handle_validate(btn):
                        lang_manager.set_language(btn.id)
                        if not self.connected_to_network:
                            TmpMessage(self, text_id=34, explain_id=37)
                        self.lang_btn.text_widget.set_text(btn.text)
                        self.lang_btn.text_widget2.set_text(btn.text)

                        memory_lang_id = btn.id
                        import importlib
                        try:
                            importlib.import_module("language.dict_" + btn.id)
                        except ModuleNotFoundError:
                            memory_lang_id = lang_manager.ref_language
                        self.memory.set_lang(memory_lang_id)

                        lang_choose_zone.hide()
                LangBtn(id="es", text="Español")
                LangBtn(id="en", text="English")
                fr = LangBtn(id="fr", text="Français")
                LangBtn(id="it", text="Italiano")
                LangBtn(id="la", text="Latinus")
                fr.layer.pack()
                lang_choose_zone.adapt()
                lang_choose_zone.resize(width=max(lang_choose_zone.rect.width, param_zone.rect.width),
                                        height=max(lang_choose_zone.rect.height, param_zone.rect.height))
        self.lang_btn.command = create_lang_choose_zone

        # RESOLUTION
        def create_resolution_choose_zone():
            with bp.paint_lock:
                resolution_choose_zone = BackgroundedZone(self, padding=(90, 60), spacing=20, sticky="center",
                                                          layer=self.extra_layer)
                PE_Button(resolution_choose_zone, text="<", pos=(10, 10), layer_level=2, translatable=False,
                          size=(40, 40), command=resolution_choose_zone.hide)
                PE_Button(resolution_choose_zone, text="X", pos=(-10, 10), sticky="topright", layer_level=2,
                          translatable=False, size=(40, 40), background_color=(150, 20, 20),
                          command=bp.PackedFunctions(resolution_choose_zone.hide, param_zone.hide))
                class ResolutionBtn(PE_Button):
                    def __init__(btn, resolution=None):
                        if resolution is None:
                            PE_Button.__init__(btn, resolution_choose_zone, text_id=47)
                        else:
                            PE_Button.__init__(btn, resolution_choose_zone, text=f"{resolution[0]} × {resolution[1]}",
                                               translatable=False)
                        btn.resolution = resolution
                    def handle_validate(btn):
                        if btn.resolution is None:
                            self.application.set_default_size(screen_sizes[0])
                            pygame.display.set_mode(screen_sizes[0], pygame.FULLSCREEN)
                            self.resolution_btn.text_widget.set_text(btn.text)
                            self.resolution_btn.text_widget2.set_text(btn.text)
                        else:
                            self.application.set_default_size(btn.resolution)
                fullscreen_btn = ResolutionBtn()
                for i in range(min(len(screen_sizes), 7)):
                    ResolutionBtn(screen_sizes[i])
                fullscreen_btn.layer.pack()
                resolution_choose_zone.adapt()
                resolution_choose_zone.resize(width=max(resolution_choose_zone.rect.width, param_zone.rect.width),
                                              height=max(resolution_choose_zone.rect.height, param_zone.rect.height))
            self.resolution_btn.command = resolution_choose_zone.show
        self.resolution_btn.command = create_resolution_choose_zone

        # PROGRESS TRACKER
        # self.progress_tracker = ProgressTracker(self, layer=self.progress_layer)
        # self.progress_tracker.hide()

        # MAP
        map = self.map = Map(self)
        self.map_sail = map.sail
        def mapsail_open_animate():
            self.map_sail.set_radius(self.map_sail.radius + 60)
            if self.map_sail.radius >= 250:
                self.mapsail_open_animator.cancel()
        self.mapsail_open_animator = bp.RepeatingTimer(.03, mapsail_open_animate)
        def mapsail_close_animate():
            self.map_sail.set_radius(self.map_sail.radius - 60)
            if self.map_sail.radius <= 0:
                self.mapsail_close_animator.cancel()
                self.map_sail.hide()
        self.mapsail_close_animator = bp.RepeatingTimer(.02, mapsail_close_animate)

        # NEXT_TODO ANIMATION
        self.next_sail = bp.Zone(map, pos=(-map.rect.h, 0), size=(map.rect.h, "100%"), layer_level=2)
        def nextsail_animate():
            self.next_sail.move(dx=max(abs(self.next_sail.rect.centerx - map.auto_rect.centerx) / 5, 20))
            if self.next_sail.rect.left >= self.map.rect.width:
                self.nextsail_animator.cancel()
        self.nextsail_animator = bp.RepeatingTimer(.04, nextsail_animate)
        bp.Circle(self.next_sail, (0, 0, 0, 63), radius=map.auto_rect.centery, center=("50%", "50%"))
        self.nextsail_text = bp.Text(self.next_sail, "HELLO !!", font_height=50, font_color="orange", font_bold=True,
                                     sticky="center", ref=map)

        # INFORMATION ON TOP & RIGHT
        self.info_right_zone = bp.Zone(self, sticky="midright", size=("10%", 0), spacing=-3, layer=self.gameinfo_layer)
        self.info_top_zone = bp.Zone(self, sticky="midtop", size=("80%", "5%"), visible=False, layer=self.gameinfo_layer)
        self.au_tour_de = PartiallyTranslatableText(self.info_top_zone, sticky="center", text_id=5,
                                                  get_args=(lambda : self.current_player.name_id,))

        # INFORMATION AT LEFT
        self.info_left_zone = bp.Zone(self, sticky="midleft", size=("10%", "60%"), visible=False, layer=self.gameinfo_layer)
        def next_todo_command():
            if self.todo.id == 22:
                self.next_player()
                self.set_todo(20)
            else:
                self.set_todo(self.todo.id + 1)
        self.next_todo = PE_Button(self.info_left_zone, "Étape suivante", width="100%", sticky="midbottom",
                                   command=next_todo_command)
        def handle_timeout():
            if self.todo.text == "build":
                self.todo.end()
            if self.todo.text == "attack":
                self.todo.end()
            self.next_player()
            self.set_todo(20)
        self.time_left = bp.Timer(90, handle_timeout)
        order_zone = bp.Zone(self.info_left_zone, size=("100%", self.next_todo.rect.top))
        def handle_ilz_resize():
            order_zone.resize(self.info_left_zone.rect.width, self.next_todo.rect.top)
            order_zone.pack()
        self.info_left_zone.signal.RESIZE.connect(handle_ilz_resize, owner=order_zone)
        timer_zone = bp.Zone(order_zone, size=("100%", "10%"), background_color="black")
        bp.DynamicText(timer_zone, lambda: bp.format_time(self.time_left.get_time_left(), formatter="%M:%S"),
                            sticky="center", align_mode="center", font_color="white")
        self.construction_label_zone = z1= BackgroundedZone(order_zone, size=("100%", "30%"), padding=5)
        self.construction_label_zone.text = TranslatableText(z1, text_id=16, sticky="center", align_mode="center")
        self.attack_label_zone = z2 = BackgroundedZone(order_zone, size=("100%", "30%"), padding=5)
        self.attack_label_zone.text = TranslatableText(z2, text_id=17, sticky="center", align_mode="center")
        self.reorganisation_label_zone = z3 = BackgroundedZone(order_zone, size=("100%", "30%"), padding=5)
        self.reorganisation_label_zone.text = TranslatableText(z3, text_id=18, sticky="center", align_mode="center")
        order_zone.pack()

        # INFO COUNTRY
        self.info_country_on_hover = False
        self.region_info_zone = BackgroundedZone(self, size=(150, 150), visible=False, layer=self.game_layer)
        r2 = bp.Rectangle(self.region_info_zone, size=(self.region_info_zone.rect.w, 40),
                          color=(0, 0, 0, 0), border_width=2, border_color="black")
        self.invade_btn = RegionInfoButton(self, text_id=4)
        self.back_btn = RegionInfoButton(self, text_id=19)
        self.import_btn = RegionInfoButton(self, text_id=20)
        class InfoCountryTitle(TranslatableText):
            def __init__(txt, *args, **kwargs):
                TranslatableText.__init__(txt, *args, text_id=0, **kwargs)
            def set_region(self, region):
                if region.upper_name == self.text:
                    return
                self.set_ref_text(region.upper_name_id)
        info_country_title = InfoCountryTitle(self.region_info_zone, align_mode="center", sticky="center", ref=r2,
                                              max_width=self.region_info_zone.rect.w - 10)
        self.info_csa = bp.Text(self.region_info_zone, "", pos=(5, r2.rect.bottom + 5))
        self.info_csi = bp.Image(self.region_info_zone, Player.SOLDIERS["asia"],
                                 ref=self.info_csa, pos=(4, -2), refloc="topright")
        def handle_infocountry_change(region=None):
            region = self.map.selected_region if region is None else region

            self.region_info_zone.set_pos(midleft=(region.abs_rect.right + 5, region.abs_rect.centery))
            # info_country_title.set_text(region.name.upper().replace("_", " "))
            info_country_title.set_region(region)
            if region.owner is None:
                self.info_csi.hide()
                self.info_csa.hide()
            else:
                self.info_csi.show()
                self.info_csa.show()
                self.info_csi.set_surface(region.owner.soldier_icon)
                self.info_csa.set_text(str(region.soldiers_amount))
            self.region_info_zone.show()

            self.invade_btn.hide()
            self.back_btn.hide()
            self.import_btn.hide()
            if self.todo.id == 21 and self.transferring:
                if region.name in self.transfert_from.neighbors and region.owner != self.transfert_from.owner:
                    self.invade_btn.show()
                elif region is self.transfert_from:
                    self.back_btn.show()
            elif self.todo.id == 22 and self.transferring:
                if region is self.transfert_from:
                    self.back_btn.show()
                elif region in self.transfert_from.all_allied_neighbors:
                    self.import_btn.show()
        self.handle_infocountry_change = handle_infocountry_change
        self.map.signal.REGION_SELECT.connect(handle_infocountry_change, owner=None)

        # REGION CHOOSE
        self.picked_regions = []
        def rc_next():
            if len(self.players) < self.nb_players:
                self.rc_yes.hide()
                self.rc_no.hide()
                set_cursor("default")
                self.set_todo(10)
            else:
                self.next_player()
                count = 0
                while self.current_player.flag_region is not None:
                    self.next_player()
                    count += 1
                    if count == self.nb_players:
                        self.current_player_id = -1
                        self.next_player()  # set to player n°1
                        self.time_left.start()
                        self.rc_yes.hide()
                        self.rc_no.hide()
                        return self.set_todo(20)
                self.pick_region()
        def yes():
            self.current_player.flag_region = self.last_selected_region
            flag = self.flags[self.current_player_id]
            flag.swap_layer(map.behind_regions_layer)
            flag.set_pos(midbottom=self.last_selected_region.flag_midbottom)
            flag.show()
            self.current_player.conquer(self.last_selected_region)
            self.current_player.move_flag(self.last_selected_region)
            self.last_selected_region.add_soldiers(3)
            rc_next()
        self.rc_yes = RegionInfoButton(self, text_id=21)
        self.rc_no = RegionInfoButton(self, text_id=22)
        self.rc_yes.set_pos(midbottom=(75, 103))
        self.rc_yes.command = yes
        self.rc_no.command = rc_next

        # WINNER INFO
        self.winner_info_zone = WinnerInfoZone(self)

        # NB PLAYERS CHOOSE
        self.nb_players = None
        self.choose_nb_players_zone = BackgroundedZone(self, size=(992, 400), sticky="center", visible=False,
                                                       layer=self.gameinfo_layer)
        r2 = bp.Rectangle(self.choose_nb_players_zone, size=("100%", 50), color="black")
        centerx = int(self.choose_nb_players_zone.rect.w / 2)
        centery = int((self.choose_nb_players_zone.rect.h + r2.rect.h + 3) / 2)
        TranslatableText(self.choose_nb_players_zone, text_id=25, center=r2.rect.center, font_height=30,
                font_color=self.theme.colors.font_opposite)
        btn_w = 36*3
        btn_marg = 20
        btn_mid = int(btn_w / 2 + btn_marg / 2)
        class ClickableNb(bp.Button):
            STYLE = bp.Button.STYLE.substyle()
            STYLE.modify(text_style={"font_height":30}, background_color=(0, 0, 0, 24), width=btn_w, height=60*3)
            def __init__(btn, number, pos):
                bp.Button.__init__(btn, self.choose_nb_players_zone, text=str(number), center=pos)
                btn.original_font_height = btn.text_widget.font.height
            def handle_hover(btn):
                btn.text_widget.font.config(height=int(btn.original_font_height * 1.5))
            def handle_unhover(btn):
                btn.text_widget.font.config(height=btn.original_font_height)
            def validate(btn, *args, **kwargs):
                self.set_todo(10)
                self.nb_players = int(btn.text)

        b1 = ClickableNb(1, pos=(centerx - btn_w * 2 - btn_marg * 2 - btn_mid, centery))
        b1.set_background_color((0, 0, 0, 0))
        b1.disable()
        TranslatableText(b1, text_id=36, sticky="midbottom", pos=(0, -5), align_mode="center")
        ClickableNb(2, pos=(centerx - btn_w * 1 - btn_marg * 1 - btn_mid, centery))
        ClickableNb(3, pos=(centerx - btn_mid, centery))
        ClickableNb(4, pos=(centerx + btn_mid, centery))
        ClickableNb(5, pos=(centerx + btn_w * 1 + btn_marg * 1 + btn_mid, centery))
        ClickableNb(6, pos=(centerx + btn_w * 2 + btn_marg * 2 + btn_mid, centery))

        # FLAG CHOOSE
        self.choose_color_zone = BackgroundedZone(self, size=(992, 400), sticky="center", visible=False,
                                                  layer=self.gameinfo_layer)
        r2 = bp.Rectangle(self.choose_color_zone, size=("100%", 50), color="black")
        centerx = int(self.choose_color_zone.rect.w / 2)
        centery = int((self.choose_color_zone.rect.h + r2.rect.h + 3) / 2)
        TranslatableText(self.choose_color_zone, text_id=26, center=r2.rect.center, font_height=30,
                font_color=self.theme.colors.font_opposite)
        class ClickableFlag(bp.Button):
            STYLE = bp.Button.STYLE.substyle()
            STYLE.modify(background_color=(0, 0, 0, 24), width=btn_w, height=60*3, hover_class=None)
            def __init__(btn, continent, pos):
                bp.Button.__init__(btn, self.choose_color_zone, center=pos)
                btn.continent = continent
                btn.flag = bp.Image(btn, Player.FLAGS[continent], sticky="center")
                btn.flag2 = bp.Image(btn, Player.FLAGS_BIG[continent], sticky="center", visible=False)
                btn.flag2.resize(int(btn.flag.rect.width * 1.5), int(btn.flag.rect.height * 1.5))
            def disable(btn):
                btn.set_background_color((0, 0, 0, 0))
                super().disable()
            def enable(btn):
                btn.set_background_color((0, 0, 0, 24))
                super().enable()
            def handle_hover(btn):
                with bp.paint_lock:
                    btn.flag.hide()
                    btn.flag2.show()
            def handle_unhover(btn):
                with bp.paint_lock:
                    btn.flag.show()
                    btn.flag2.hide()
            def validate(btn, *args, **kwargs):
                Player(self, btn.continent)
                self.next_player()
                self.flags.append(self.current_player.flag)
                self.set_todo(11)
                btn.disable()
        ClickableFlag("north_america", pos=(centerx - btn_w * 2 - btn_marg * 2 - btn_mid, centery))
        ClickableFlag("europa", pos=(centerx - btn_w * 1 - btn_marg * 1 - btn_mid, centery))
        ClickableFlag("asia", pos=(centerx - btn_mid, centery))
        ClickableFlag("south_america", pos=(centerx + btn_mid, centery))
        ClickableFlag("africa", pos=(centerx + btn_w * 1 + btn_marg * 1 + btn_mid, centery))
        ClickableFlag("oceania", pos=(centerx + btn_w * 2 + btn_marg * 2 + btn_mid, centery))

        # CLICK TO START
        self.play_zone = PlayZone(self)

        # CONFIRMATION
        self.confirm_zone = BackgroundedZone(self, visible=False, padding=6, spacing=4, layer=self.game_layer)
        bp.Button(self.confirm_zone, size=(30, 30), background_color="green4", focus=-1,
                  background_image=Region.BUILDS.subsurface(0, 60, 30, 30),
                  command=bp.PackedFunctions(lambda: self.todo.confirm(), self.map.region_unselect))
        bp.Button(self.confirm_zone, size=(30, 30), background_color="red4", focus=-1,
                  background_image=Region.BUILDS.subsurface(30, 60, 30, 30), command=self.map.region_unselect)
        self.confirm_zone.pack(adapt=True)

        # CHOOSE BUILD
        self.choose_build_zone = BackgroundedZone(self, visible=False, padding=6, spacing=4, layer=self.game_layer)

        def build(build_name):
            self.last_selected_region.start_construction(build_name)
            self.current_player.change_gold(-3)
            self.current_player.check_build()
            self.map.region_unselect()

        bp.Button(self.choose_build_zone, "", size=(30, 30), background_image=Region.MINE,
                  command=bp.PrefilledFunction(build, "mine"), background_color=(0, 0, 0, 0))
        bp.Button(self.choose_build_zone, "", size=(30, 30), background_image=Region.CAMP,
                  command=bp.PrefilledFunction(build, "camp"), background_color=(0, 0, 0, 0))
        self.choose_build_zone.pack(adapt=True)

        # SOLDIERS TRANSFERT
        self.transfert_from = None
        self.transfert_zone = BackgroundedZone(self, size=(35, 24), visible=False,
                                               padding=4, spacing=4, layer=self.game_layer)
        self.transfert_amount = 0
        self.transfert_title = bp.Text(self.transfert_zone, "")
        self.transfert_icon = bp.Image(self.transfert_zone, Player.SOLDIERS["asia"])
        def handle_mouse_motion():
            self.transfert_zone.set_pos(topleft=(bp.mouse.x + 12, bp.mouse.y))
        bp.mouse.signal.MOUSEMOTION.connect(handle_mouse_motion, owner=None)

        # TODOS
        self.step = None
        self.step_from_id = {}

        self.todo = None
        self.todo_from_id = {}
        self._init_steps()

        # SETUP
        self.map.signal.REGION_SELECT.connect(self.handle_region_select, owner=self)
        self.map.signal.REGION_UNSELECT.connect(self.handle_region_unselect, owner=self)

    def _init_steps(self):

        from library.step import Step

        def start_presentation():
            self.set_tuto_ref_text_id(38)
            self.play_zone.btn.resize(*self.play_zone.btn.original_size)
            self.play_zone.show()
            self.play_zone.btn_animator.start()
        def end_presentation():
            self.play_zone.hide()
            self.play_zone.btn_animator.cancel()
        Step(self, 0, start_presentation, end_presentation)

        def start_choosenbplayers():
            self.choose_nb_players_zone.show()
            self.newgame_setup()
            self.set_tuto_ref_text_id(27)
            self.info_top_zone.hide()
            self.info_right_zone.hide()
        Step(self, 1, start_choosenbplayers, end=self.choose_nb_players_zone.hide)

        def start_choosecolor():
            self.choose_color_zone.show()
            self.set_tuto_ref_text_id(28)
        def end_choosecolor():
            self.choose_color_zone.hide()
            self.info_top_zone.show()
            self.info_right_zone.show()
        Step(self, 10, start_choosecolor, end_choosecolor)

        def start_pickregion():
            self.set_tuto_ref_text_id(29)
            self.pick_region()
        Step(self, 11, start=start_pickregion)

        def start_build():
            self.next_todo.show()
            self.info_left_zone.show()
            self.set_tuto_ref_text_id(31)
            self.construction_label_zone.set_background_color("orange")
            self.nextsail_text.set_text(self.construction_label_zone.text.text)
            self.current_player.build_stuff()
        def end_build():
            self.construction_label_zone.set_background_color(BackgroundedZone.STYLE["background_color"])
        Step(self, 20, start=start_build, end=end_build)

        def start_attack():
            self.set_tuto_ref_text_id(32)
            self.attack_label_zone.set_background_color("orange")
            self.nextsail_text.set_text(self.attack_label_zone.text.text)
            self.current_player.check_attack()
        def end_attack():
            self.attack_label_zone.set_background_color(BackgroundedZone.STYLE["background_color"])
        Step(self, 21, start=start_attack, end=end_attack)

        def start_reorganization():
            self.set_tuto_ref_text_id(33)
            self.reorganisation_label_zone.set_background_color("orange")
            self.nextsail_text.set_text(self.reorganisation_label_zone.text.text)
            self.current_player.check_movement()
        def end_reorganization():
            self.reorganisation_label_zone.set_background_color(BackgroundedZone.STYLE["background_color"])
        Step(self, 22, start=start_reorganization, end=end_reorganization)

        self.todo = self.todo_from_id[0]
        self.set_todo(0)

    def _set_connected_to_network(self, boolean):
        if boolean:
            raise PermissionError("Can only set game.connected_to_network to False")
        if self._connected_to_network is False:
            return
        self._connected_to_network = False
        self.connection_btn.text_widget.set_ref_text(11)
        self.connection_btn.enable()
        TmpMessage(self, text_id=34)
    connected_to_network = property(lambda self: self._connected_to_network, _set_connected_to_network)
    current_player = property(lambda self: self.players[self.current_player_id])
    transferring = property(lambda self: self.transfert_from is not None)

    def end_transfert(self, region=None):

        assert self.transferring
        if region is None:
            region = self.map.selected_region
        if region is None:
            region = self.temp_import_region
        assert region is not None

        if region.owner is None:
            self.current_player.conquer(region)
            region.add_soldiers(self.transfert_amount)
        elif region.owner is self.transfert_from.owner:
            region.add_soldiers(self.transfert_amount)
        else:
            deaths = min(self.transfert_amount, region.soldiers_amount)
            self.transfert_amount -= deaths
            region.rem_soldiers(deaths)

            if self.transfert_amount > 0:
                self.current_player.conquer(region)
                region.add_soldiers(self.transfert_amount)
            self.transfert_amount = 0
            self.current_player.update_soldiers_title()

        self.transfert_from = None
        self.transfert_amount = 0
        self.transfert_zone.hide()
        self.back_btn.hide()
        self.invade_btn.hide()
        self.back_btn.defocus()

        if region.owner is None:
            self.info_csi.hide()
            self.info_csa.hide()
        else:
            self.info_csi.set_surface(region.owner.soldier_icon)
            self.info_csa.set_text(str(region.soldiers_amount))
            self.info_csi.show()
            self.info_csa.show()

        if self.map.selected_region is region:
            self.back_btn.hide()
            self.import_btn.hide()

        if self.todo.id == 21 and self.winner_info_zone.is_hidden:
            self.current_player.check_attack()
        elif self.todo.id == 22:
            self.current_player.check_movement()

    def handle_event(self, event):

        # Region sail
        if self.todo.id >= 20:
            if event.type == bp.MOUSEMOTION:
                if self.map.selected_region is None and self.map.is_hovered:
                    hovered = ctrl_hovered = None
                    for region in self.regions.values():
                        if region.get_hovered():
                            if self.map.hovered_region is region:
                                hovered = region
                                break
                            if self.info_country_on_hover:
                                ctrl_hovered = region
                                self.handle_infocountry_change(region)
                                self.region_info_zone.show()

                            hoverable = False
                            if self.todo.id == 17:
                                if region.owner is None:
                                    hoverable = True
                            if self.todo.id == 20:
                                if region.owner is self.current_player and region.build_state == "empty":
                                    hoverable = True
                            elif self.todo.id == 21:
                                if self.transferring:
                                    if region is self.transfert_from:
                                        hoverable = True
                                    elif region.name in self.transfert_from.neighbors and \
                                            region.owner != self.transfert_from.owner:
                                        hoverable = True
                                elif region in self.current_player.regions:
                                    hoverable = True
                            if self.todo.id == 22:
                                if self.transferring:
                                    if region is self.transfert_from:
                                        hoverable = True
                                    elif region in self.transfert_from.all_allied_neighbors and \
                                            region.owner is self.transfert_from.owner:
                                        hoverable = True
                                elif region in self.current_player.regions:
                                    hoverable = True
                            if hoverable:
                                hovered = region
                                if self.map.hovered_region is not None:
                                    self.map.hovered_region.hide()
                                self.map.hovered_region = region
                                region.show()
                                break
                            if ctrl_hovered is not None:
                                break

                    if hovered is None:
                        if ctrl_hovered is None and self.region_info_zone.is_visible:
                            self.region_info_zone.hide()
                        if self.map.hovered_region is not None:
                            self.map.hovered_region.hide()
                            self.map.hovered_region = None

            elif event.type == bp.KEYDOWN:
                if self.todo.id > 2:
                    if event.key == bp.K_LCTRL:
                        self.info_country_on_hover = True

            elif event.type == bp.KEYUP:
                if self.todo.id > 2:
                    if event.key == bp.K_LCTRL:
                        self.info_country_on_hover = False
                        if self.map.selected_region is None:
                            self.region_info_zone.hide()

            elif event.type == bp.MOUSEBUTTONDOWN and event.button == 3:  # right click
                if self.todo.id in (21, 22):
                    if self.map.is_hovered:
                        right_clicked = None
                        for region in self.current_player.regions:
                            if region.get_hovered():
                                self.transfert(region)
                                right_clicked = region
                                break
                        if right_clicked is None and self.transferring:
                            for region_name in self.transfert_from.neighbors:
                                region = self.regions[region_name]
                                if region.owner != self.transfert_from.owner:
                                    if region.get_hovered():
                                        self.map.handle_link()

    def handle_region_select(self, region):

        if self.mapsail_close_animator.is_running:
            self.mapsail_close_animator.cancel()
        if self.mapsail_open_animator.is_running:
            self.mapsail_open_animator.cancel()
        self.map_sail.set_pos(center=region.rect.center)
        self.map_sail.set_radius(60)
        self.mapsail_open_animator.start()
        self.map_sail.show()

        self.last_selected_region = region

        if self.todo.id == 17:
            flag = self.flags[self.current_player_id]
            if region.owner is not None:
                flag.hide()
                self.confirm_zone.hide()
                return
            flag.set_pos(midbottom=region.flag_midbottom)
            flag.show()
            self.confirm_zone.set_pos(midright=(region.abs_rect.left - 5, region.abs_rect.centery))
            self.confirm_zone.show()

        if self.todo.id == 20:
            if region in self.current_player.regions and region.build_state == "empty":
                self.choose_build_zone.set_pos(midright=(region.abs_rect.left - 5, region.abs_rect.centery))
                self.choose_build_zone.show()
            else:
                self.choose_build_zone.hide()

    def handle_region_unselect(self):

        if self.mapsail_open_animator.is_running:
            self.mapsail_open_animator.cancel()
        self.mapsail_close_animator.start()

        self.region_info_zone.hide()
        self.confirm_zone.hide()
        self.choose_build_zone.hide()

        if self.todo.id == 10:
            flag = self.flags[self.current_player_id]
            flag.hide()

    def handle_resize(self):

        super().handle_resize()
        # if self.resolution_btn.text_widget.has_locked("text"):
        #     return
        text = f"{self.rect.width} × {self.rect.height}"
        self.resolution_btn.text_widget.set_text(text)
        self.resolution_btn.text_widget2.set_text(text)

    def next_player(self):

        if self.todo.id >= 20:
            if self.turn_index > 0 and self.current_player_id == len(self.players) - 1:
                self.turn_index += 1

        self.current_player_id = (self.current_player_id + 1) % len(self.players)
        if not self.current_player.is_alive:
            self.next_player()
            return
        self.au_tour_de.complete_text()
        self.info_top_zone.set_background_color(self.current_player.color)

        if self.time_left.is_running:
            self.time_left.cancel()
        if self.todo.id >= 20:
            self.time_left.start()

        set_cursor(self.current_player.name)

    def next_turn(self):

        self.turn_index += 1
        self.current_player_id = -1
        self.next_player()
        if self.todo.id >= 20:
            self.time_left.start()
        self.set_todo(20)
        if self.map.selected_region is not None:
            self.map.region_unselect()

    def newgame_setup(self):

        for r in self.regions.values():
            r.flag = None
            r.destroy_construction()

        for p in self.players.values():
            for r in tuple(p.regions):
                r.rem_soldiers(r.soldiers_amount)
            p.flag.kill()
        self.players = {}
        self.flags = []

        for w in self.choose_color_zone.children:
            if isinstance(w, bp.Button):
                w.enable()

        for z in tuple(self.info_right_zone.children):
            z.kill()
        self.info_top_zone.hide()
        self.info_left_zone.hide()
        self.winner_info_zone.hide()
        if self.time_left.is_running:
            self.time_left.cancel()

        self.picked_regions.clear()

        set_cursor("default")

    def pick_region(self):

        while True:
            picked = random.choice(self.regions_list)
            if picked not in self.picked_regions:
                self.picked_regions.append(picked)
                break
        self.map.region_select(picked)

        player = self.current_player
        player.choose_region_attemps += 1
        if player.choose_region_attemps < 3:
            self.rc_yes.show()
            self.rc_no.show()
        else:
            self.rc_yes.command()

    def set_todo(self, index):

        if self.transferring:
            self.end_transfert(self.transfert_from)

        self.todo.end()

        self.todo = self.todo_from_id[index]

        if self.map.selected_region is not None:
            self.map.region_unselect()
        self.todo.start()

        if self.todo.id >= 20:
            self.next_sail.set_pos(right=0)
            if self.nextsail_animator.is_running:
                self.nextsail_animator.cancel()
            self.nextsail_animator.start()

    def set_tuto_ref_text_id(self, text_id):
        self.tuto_ref_text_id = text_id
        if isinstance(self.tuto_text, TranslatableText):
            self.tuto_text.set_ref_text(text_id)
        else:
            self.tuto_text = text_id

    def transfert(self, region):

        if self.transferring:
            if self.transfert_from is region:
                if region.soldiers_amount < 2:
                    self.back_btn.command(region)
                else:
                    self.map.region_unselect()
                    amount = region.soldiers_amount - 1 if bp.keyboard.mod.maj else 1
                    self.transfert_amount += amount
                    region.rem_soldiers(amount)
                    self.transfert_title.set_text(str(self.transfert_amount))
                    self.transfert_zone.pack(axis="horizontal", adapt=True)
            else:
                if self.todo.text == "troops movement":
                    self.temp_import_region = region
                    self.import_btn.validate()
        else:
            if region.soldiers_amount < 2:
                return

            self.map.region_unselect()
            self.transfert_from = region
            amount = region.soldiers_amount - 1 if bp.keyboard.mod.maj else 1
            self.transfert_amount = amount
            region.rem_soldiers(amount)
            self.transfert_icon.set_surface(region.owner.soldier_icon)
            self.transfert_title.set_text(str(self.transfert_amount))
            self.transfert_zone.pack(axis="horizontal", adapt=True)
            self.transfert_zone.show()
