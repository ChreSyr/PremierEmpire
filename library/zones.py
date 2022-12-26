
import math
import baopig as bp
from baopig.googletrans import Dictionnary, TranslatableText, PartiallyTranslatableText, dicts, lang_manager,\
    LANGUAGES_TRANSLATED
import pygame
from library.images import FLAGS_BIG
from library.loading import logo, fullscreen_size, screen_sizes
from library.buttons import PE_Button, PE_Button_Text


class BackgroundedZone(bp.Zone):
    STYLE = bp.Zone.STYLE.substyle()
    STYLE.modify(
        background_color=(176, 167, 139),
        border_color="black",
        border_width=2,
        padding=3,
    )


class KillOnClick(bp.LinkableByMouse):

    def __init__(self, parent, lifetime=3, **kwargs):

        bp.LinkableByMouse.__init__(self, parent, **kwargs)

        self.timer = bp.Timer(lifetime, command=self.kill)
        self.timer.start()

    def handle_link(self):

        self.timer.cancel()
        self.kill()


class GameSail(bp.Circle):

    def __init__(self, game):

        bp.Circle.__init__(self, game, color=(0, 0, 0, 63), radius=120, visible=False, sticky="center",
                           layer=game.extra_layer)

        self.max_radius = sum(fullscreen_size) / 2
        self.animator = bp.RepeatingTimer(.03, self.animate)

        from baopig.pybao import WeakList
        self._targets = WeakList()

    def _needs_to_be_open(self):

        for target in self._targets:
            if target.is_visible:
                return True
        return False

    def add_target(self, target):

        self._targets.append(target)

        target.signal.SHOW.connect(self.handle_targetshow, owner=self)
        target.signal.HIDE.connect(self.handle_targethide, owner=self)

        if target.is_visible:
            self.handle_targetshow()

    def animate(self):

        if self._needs_to_be_open():
            if self.radius < 480:
                self.set_radius(self.radius + 60)
            else:
                self.set_radius(self.max_radius)
                self.animator.cancel()
        else:
            if self.radius > 480:
                self.set_radius(480)
            else:
                self.set_radius(self.radius - 60)
            if self.radius == 0:
                self.animator.cancel()
                self.hide()

    def handle_targetshow(self):

        self.move_behind_main_target()

        if self.radius == self.max_radius:
            return

        if not self.animator.is_running:
            self.show()
            self.animator.start()

    def handle_targethide(self):

        if self.radius == 0:
            return

        if self._needs_to_be_open():
            return self.move_behind_main_target()

        if not self.animator.is_running:
            self.animator.start()

    def move_behind_main_target(self):

        main_target = None
        for target in self._targets:
            if target.is_visible:
                main_target = target

        assert main_target is not None

        if main_target in self.layer:
            self.move_behind(main_target)
        else:
            self.layer.move_on_top(self)


class RightClickZone(BackgroundedZone, bp.Focusable):

    def __init__(self, game, mouse_event, **kwargs):

        BackgroundedZone.__init__(self, game, layer=game.extra_layer, pos=mouse_event.pos,
                                  padding=(2, 6), **kwargs)
        bp.Focusable.__init__(self, game)

        game.focus(self)

    def add_btn(self, btn_text_id, btn_command):

        class RightClickButton(bp.Button):

            STYLE = bp.Button.STYLE.substyle()
            STYLE.modify(
                text_class=PE_Button_Text,
            )

            def __init__(btn, *args, text_id=None, **kwargs):

                if text_id is not None:
                    kwargs["text"] = lang_manager.get_text_from_id(text_id)

                btn.is_translatable = True
                btn.text_id = text_id

                bp.Button.__init__(btn, *args, **kwargs)

            def handle_validate(btn):

                super().handle_validate()
                btn.parent.kill()

        RightClickButton(self, text_id=btn_text_id, command=btn_command, pos=(0, 10000),
                         background_color=(0, 0, 0, 0), size=(220, 32), padding=2,
                         text_style={"font_height":20})
        self.pack()
        self.adapt()

    def handle_defocus(self):

        if self.scene.focused_widget.parent is not self:
            self.kill()


class TmpMessage(BackgroundedZone, KillOnClick):

    def __init__(self, game, text_id, explain_id=None, explain=None):

        BackgroundedZone.__init__(self, game, size=(400, 150), sticky="midtop", layer_level=2)
        KillOnClick.__init__(self, game)

        msg_w = TranslatableText(self, text_id=text_id, max_width=self.rect.w - 10, align_mode="center", pos=(0, 5),
                                 sticky="midtop", font_height=self.get_style_for(bp.Text)["font_height"] + 4)
        r2 = bp.Rectangle(self, size=(self.rect.w, msg_w.rect.h + 10), color=(0, 0, 0, 0), border_width=2)
        if explain_id:
            TranslatableText(self, text_id=explain_id, max_width=self.rect.w - 10,
                             pos=(5, 5), ref=r2, refloc="bottomleft")
        elif explain:
            bp.Text(self, text=explain, max_width=self.rect.w - 10, pos=(5, 5), ref=r2, refloc="bottomleft")


class Warning(BackgroundedZone):

    def __init__(self, game, msg_id, anyway, always=None):

        BackgroundedZone.__init__(self, game, layer=game.extra_layer, size=(640, 400), sticky="center")
        game.sail.add_target(self)

        TranslatableText(self, text_id=msg_id, sticky="midtop", pos=(0, 40), font_height=35, align_mode="center")

        btns_zone = bp.Zone(self, sticky="midbottom", pos=(0, -40), spacing=140 * 2)
        def cancel():
            self.kill()
            if always is not None:
                always()
        PE_Button(btns_zone, text_id=91, command=cancel)
        def confirm():
            self.kill()
            anyway()
            if always is not None:
                always()
        PE_Button(btns_zone, text_id=92, command=confirm)
        btns_zone.default_layer.pack(axis="horizontal")
        btns_zone.adapt()


# --


class CardsZone(BackgroundedZone):

    class Card(BackgroundedZone):

        def __init__(self, cards_zone, region, slot_id):

            BackgroundedZone.__init__(self, cards_zone, size=cards_zone.current_slot_size,
                                      pos=cards_zone.add_buttons[slot_id].rect.topleft)

            title_zone = BackgroundedZone(self, size=cards_zone.little_slot_size)
            TranslatableText(title_zone, text_id=region.upper_name_id, sticky="center",
                             max_width=self.content_rect.w - 6, align_mode="center", selectable=False)

            self.region = region
            self.slot_id = slot_id

        def decrease(self):
            self.resize(*self.parent.little_slot_size)

        def increase(self):
            self.resize(*self.parent.big_slot_size)

    class AddCardButton(PE_Button):

        def __init__(self, cards_zone, slot_id):
            PE_Button.__init__(self, cards_zone, text="+", translatable=False, size=cards_zone.little_slot_size)
            self.slot_id = slot_id

        def decrease(self):
            self.resize(*self.parent.little_slot_size)

        def increase(self):
            self.resize(*self.parent.big_slot_size)

    def __init__(self, game):

        BackgroundedZone.__init__(self, game, sticky="midbottom", pos=(0, 2), visible=False, padding=8, spacing=4)

        self.set_style_for(
            PE_Button,
            text_style={"font_height": 35},
            padding=0,
        )

        self.little_slot_size = (152, 44)
        self.big_slot_size = (152, int(152 * 1.6))

        self.toggler = PE_Button(self, text="^", translatable=False, size=(44, 44), command=self.increase)
        self.add1 = self.AddCardButton(self, slot_id=0)
        self.add2 = self.AddCardButton(self, slot_id=1)
        self.add3 = self.AddCardButton(self, slot_id=2)
        self.add_buttons = [self.add1, self.add2, self.add3]

        self.hands = {}  # self.hands[a_player] -> 3 widgets (Card or AddCardButton)
        self.current_hand = [self.add1, self.add2, self.add3]

        self.default_layer.pack(axis="horizontal")
        self.adapt()

        game.signal.PLAYER_TURN.connect(self.handle_player_turn, owner=self)

    current_slot_size = property(lambda self: self.big_slot_size if self.is_open else self.little_slot_size)
    is_open = property(lambda self: self.rect.height > 150)

    def decrease(self):

        for slot in self.current_hand:
            slot.decrease()

        self.resize_height(44 + self.padding.top * 2)

        self.toggler.set_text("^")
        self.toggler.command = self.increase

    def increase(self):

        for slot in self.current_hand:
            slot.increase()

        self.resize_height(self.big_slot_size[1] + self.padding.top * 2)

        self.toggler.set_text("-")
        self.toggler.command = self.decrease

    def handle_player_turn(self):

        if self.scene.step.id < 20:
            return

        for slot in self.current_hand:
            slot.hide()

        try:
            self.current_hand = self.hands[self.scene.current_player]

        except KeyError:
            flag_region_card = self.Card(self, region=self.scene.current_player.flag_region, slot_id=0)
            self.current_hand = [flag_region_card, self.add2, self.add3]
            self.hands[self.scene.current_player] = self.current_hand

        for slot in self.current_hand:
            slot.show()

    def reset(self):

        for slots in self.hands.values():
            for widget in slots:
                if not isinstance(widget, PE_Button):
                    widget.kill()


class InfoLeftZone(BackgroundedZone):

    def __init__(self, game):

        spacing = 4
        padding = 4
        BackgroundedZone.__init__(self, game, sticky="midleft", visible=False, layer=game.gameinfo_layer)

        self.highlighted = None
        self.highlighted_color = (201, 129, 0)
        self.standard_color = (158, 106, 51)

        self.turn_zone = bp.Zone(self, size=(140 + spacing * 2, 40))
        self.turn_text = PartiallyTranslatableText(self.turn_zone, text_id=5, sticky="center", max_width=140,
                                                   get_args=(lambda: game.current_player.name_id,), align_mode="center")
        def update():
            self.turn_zone.set_background_color(game.current_player.color)
            self.turn_text.complete_text()
        game.signal.PLAYER_TURN.connect(update, owner=self)

        timer_zone = bp.Zone(self, size=(140 + spacing * 2, 40), background_color="black")
        bp.DynamicText(timer_zone, lambda: bp.format_time(game.time_left.get_time_left(), formatter="%M:%S"),
                            sticky="center", align_mode="center", font_color="white")

        class InfoLeftButton(PE_Button):

            STYLE = PE_Button.STYLE.substyle()
            STYLE.modify(
                text_style={"font_height": 18},
            )

            def __init__(btn, parent, text_id, step_id=None, command=None):

                def set_step():

                    return game.set_step(btn.step_id)

                    player = game.current_player
                    i = 0

                    game.next_step()

                    while game.current_player == player and game.step.id != btn.step_id:
                        game.next_step()

                        i += 1
                        if i > 5:
                            raise StopIteration

                PE_Button.__init__(btn, parent, text_id=text_id, height=80, background_color=self.standard_color,
                                   command=set_step if command is None else command)

                btn.step_id = step_id
                btn.highlighted = False

            def set_highlighted(btn, highlighted):

                btn.highlighted = highlighted

                if highlighted:
                    btn.set_background_color(self.highlighted_color)
                    btn.disable()
                    btn.disable_sail.hide()
                else:
                    btn.set_background_color(self.standard_color)
                    if not btn.is_touchable_by_mouse:
                        btn.disable_sail.show()

        stepbtns_zone = bp.Zone(self, padding=(padding, spacing, padding, padding), spacing=spacing)
        self.construction_btn = InfoLeftButton(stepbtns_zone, text_id=16, step_id=20)
        self.construction_btn.disable()
        self.attack_btn = InfoLeftButton(stepbtns_zone, text_id=17, step_id=21)
        self.reorganisation_btn = InfoLeftButton(stepbtns_zone, text_id=18, step_id=22)
        stepbtns_zone.pack()
        stepbtns_zone.adapt()

        nextstep_zone = bp.Zone(self, padding=(padding, 40, padding, padding))
        self.next_step_btn = PE_Button(nextstep_zone, text_id=15, background_color=self.standard_color,
                                       command=game.next_player)
        nextstep_zone.pack()
        nextstep_zone.adapt()

        self.pack()
        self.adapt()

    def highlight(self, btn):

        if btn == self.reorganisation_btn:
            self.reorganisation_btn.disable()

        if self.highlighted is not None:
            self.highlighted.set_highlighted(False)

        self.highlighted = btn
        btn.set_highlighted(True)

        if btn == self.construction_btn:
            self.scene.nextsail_text.set_text(self.construction_btn.text)
            self.attack_btn.enable()
            self.reorganisation_btn.enable()
        elif btn == self.attack_btn:
            self.scene.nextsail_text.set_text(self.attack_btn.text)
            self.reorganisation_btn.enable()
        elif btn == self.reorganisation_btn:
            self.scene.nextsail_text.set_text(self.reorganisation_btn.text)
            self.attack_btn.disable()


class PlayerTurnZone(BackgroundedZone, bp.LinkableByMouse):

    def __init__(self, game):

        BackgroundedZone.__init__(self, game, size=(650, 650), sticky="center")
        bp.LinkableByMouse.__init__(self, game)

        self.flags = {}

        i_delta = 0 if game.nb_players % 2 == 0 else math.radians(-90)

        radius = 200
        for id, player in game.players.items():

            i2 = id / game.nb_players * math.pi * 2 + i_delta
            x_rel = math.cos(i2) * radius
            y_rel = math.sin(i2) * radius

            flag = FLAGS_BIG[player.continent]
            self.flags[player.id] = bp.Image(self, image=flag,
                                             center=(x_rel + self.rect.width / 2, y_rel + self.rect.height / 2))

        flag = self.flags[game.current_player.id]
        self.select_movement = None
        self.select_travel = None
        self.select_origin = None
        self.select_dest = None
        self.select_color_travel = None
        self.select_color_origin = game.current_player.color
        self.select_color_dest = None
        self.select = bp.Rectangle(self, size=(flag.rect.width + 30, flag.rect.height + 30),
                                   center=self.auto_rect.center,
                                   color=(0, 0, 0, 0), border_width=5, border_color=game.current_player.color)

        def move_select():
            self.select_movement += .07
            if self.select_movement < 0:
                return
            color = self.select_color_origin + self.select_color_travel * self.select_movement
            pos = self.select_origin + self.select_travel * self.select_movement
            if self.select_movement >= 1:
                pos = self.select_dest
                color = self.select_color_dest
                self.select_animator.cancel()
                self.select_color_origin = self.select_color_dest
            self.select.set_border_color(color)
            self.select.set_pos(center=pos)
        self.select_animator = bp.RepeatingTimer(.05, move_select)

        self.hide_timer = bp.Timer(1.5, self.hide)

        self.show()  # start animations

    def handle_link(self):

        self.hide()

    def hide(self):

        super().hide()

        if self.hide_timer.is_running:
            self.hide_timer.cancel()

        if self.scene.step.id >= 20:
            self.scene.nextsail_animator.resume()

    def show(self):

        super().show()

        self.select_origin = self.select.rect.center
        self.select_dest = self.flags[self.scene.current_player.id].rect.center
        self.select_travel = pygame.Vector2(self.select_dest) - self.select_origin
        self.select_movement = -.3
        if self.select_animator.is_running:
            self.select_animator.cancel()
            self.select_color_origin = self.select_color_dest
            self.select.set_border_color(self.select_color_origin)
        self.select_color_dest = self.scene.current_player.color
        self.select_color_travel = pygame.Vector3(self.select_color_dest) - self.select_color_origin
        self.select_animator.start()

        if self.hide_timer.is_running:
            self.hide_timer.cancel()
        self.hide_timer.start()

        if self.scene.step.id >= 20:
            self.scene.nextsail_animator.pause()


class PlayZone(bp.Zone):

    def __init__(self, game):

        logo_filled = bp.Surface(logo.get_size())
        logo_filled.fill((255, 255, 255))
        logo_filled.blit(logo, (0, 0))
        bp.Zone.__init__(self, game, size=logo.get_size(), sticky="center", layer=game.game_layer,
                         background_image=logo_filled)
        self.btn = play_btn = PE_Button(self, text_id=3, center=(0, -37), refloc="midbottom",
                                                  command=bp.PrefilledFunction(game.set_step, 1))
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

    def __init__(self, game, behind=None, padding=(90, 60), **kwargs):

        BackgroundedZone.__init__(self, game, spacing=20, sticky="center", padding=padding,
                                  layer=game.extra_layer, **kwargs)

        self.game = game
        self.behind = behind

        if behind:
            PE_Button(self, text="<", pos=(10, 10), layer_level=2, translatable=False, size=(40, 40),
                      command=self.hide, text_style={"font_height": 35}, padding=0)

        PE_Button(self, text="X", pos=(-10, 10), sticky="topright", layer_level=2, translatable=False, size=(40, 40),
                  background_color=(150, 20, 20), command=self.close_settings)

        self.main_layer = bp.Layer(self)

        game.sail.add_target(self)

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

        SettingsZone.__init__(self, game, visible=False)

        # NEW GAME
        def newgame():
            if game.step.id > 1 and game.winner is None:
                def anyway():
                    self.hide()
                    game.set_step(1)
                Warning(game, msg_id=90, anyway=anyway)  # , always=always)
            else:
                self.hide()
                self.game.set_step(1)
        self.newgame_btn = PE_Button(parent=self, text_id=2, command=newgame)

        # QUICK SETTUP
        def init_qs():
            qs_zone = SettingsZone(game, behind=self, size=self.rect.size)
            def quick_setup1():
                with bp.paint_lock:
                    if game.step.id == 0:
                        game.set_step(1)
                    if game.step.id == 1:
                        game.nb_players = 2
                        game.set_step(10)
                    if game.step.id == 10:
                        game.flag_btns[0].validate()
                        game.map.region_select(game.regions_list[0])  # alaska
                        game.rc_yes.validate()
                        game.flag_btns[2].validate()
                        game.map.region_select(game.regions_list[1])  # alberta
                        game.rc_yes.validate()
                        qs_zone.close_settings()
            PE_Button(qs_zone, text="1", translatable=False, command=quick_setup1)
            def quick_setup2():
                with bp.paint_lock:
                    if game.step.id == 0:
                        game.set_step(1)
                    if game.step.id == 1:
                        game.nb_players = 3
                        game.set_step(10)
                    if game.step.id == 10:
                        game.flag_btns[2].validate()
                        game.map.region_select(game.regions_list[0])  # alaska
                        game.rc_yes.validate()
                        game.flag_btns[3].validate()
                        game.map.region_select(game.regions_list[4])  # ontario
                        game.rc_yes.validate()
                        game.flag_btns[4].validate()
                        game.map.region_select(game.regions_list[8])  # mexique
                        game.rc_yes.validate()
                        qs_zone.close_settings()
            PE_Button(qs_zone, text="2", translatable=False, command=quick_setup2)
            def quick_setup3():
                with bp.paint_lock:
                    if game.step.id == 0:
                        game.set_step(1)
                    if game.step.id == 1:
                        game.nb_players = 2
                        game.set_step(10)
                    if game.step.id == 10:

                        qs_zone.close_settings()

                        alaska = game.regions_list[0]
                        territoires = game.regions_list[1]
                        alberta = game.regions_list[2]

                        game.flag_btns[4].validate()  # gray
                        game.map.region_select(alaska)
                        game.rc_yes.validate()
                        game.flag_btns[5].validate()  # purple
                        game.map.region_select(alberta)
                        game.rc_yes.validate()

                        game.map.region_select(alaska)
                        game.camp_btn.validate()
                        game.next_step()

                        game.map.region_select(alberta)
                        game.camp_btn.validate()
                        game.transfert(alberta)
                        game.map.region_select(territoires)
                        game.invade_btn.validate()
                        game.next_step()
                        game.transfert(alberta)
                        game.end_transfert(territoires)
                        game.next_step()

                        game.map.region_select(alaska)
                        game.transfert(alaska)
                        game.transfert(alaska)
                        game.map.region_select(alberta)
                        game.invade_btn.validate()
            PE_Button(qs_zone, text="3", translatable=False, command=quick_setup3)
            qs_zone.pack_and_adapt()
            self.qs_btn.command = qs_zone.show
        self.qs_btn = PE_Button(parent=self, text="Quick setup", translatable=False, command=init_qs)

        # TUTORIAL
        self.tuto_btn = PE_Button(parent=self, text_id=7)

        # CONNECTION
        connection_zone = bp.Zone(self)
        self.connection_title = TranslatableText(connection_zone, text_id=9, sticky="midtop", align_mode="center")
        def toggle_connection():
            lang_manager.set_connected(not lang_manager.is_connected_to_network)
        self.connection_btn = PE_Button(parent=connection_zone, text_id=10, command=toggle_connection,
                                        pos=(0, self.connection_title.rect.bottom + 3))
        def handle_update_connection():
            if lang_manager.is_connected_to_network:
                self.connection_btn.text_widget.set_ref_text(10)
            else:
                self.connection_btn.text_widget.set_ref_text(11)
                TmpMessage(self.scene, text_id=34)
        lang_manager.signal.NEW_CONNECTION_STATE.connect(handle_update_connection, owner=self)
        connection_zone.adapt()

        # LANGUAGE
        lang_zone = bp.Zone(self)
        lang_title = TranslatableText(lang_zone, text_id=12, sticky="midtop")
        self.lang_btn = PE_Button(parent=lang_zone, text=LANGUAGES_TRANSLATED[lang_manager.language].capitalize(),
                                  pos=(0, lang_title.rect.bottom + 3), translatable=False)
        lang_zone.adapt()

        # RESOLUTION
        resolution_zone = bp.Zone(self)
        resolution_title = TranslatableText(resolution_zone, text_id=46, sticky="midtop")
        self.resolution_btn = PE_Button(parent=resolution_zone, text=f"{game.rect.width} × {game.rect.height}",
                                        pos=(0, resolution_title.rect.bottom + 3), translatable=False)
        def handle_update_language():
            if "×"  not in self.resolution_btn.text:
                self.resolution_btn.set_text(lang_manager.get_text_from_id(text_id=47))
        lang_manager.signal.UPDATE_LANGUAGE.connect(handle_update_language, owner=self.resolution_btn)
        resolution_zone.adapt()

        # EXIT
        PE_Button(parent=self, text_id=1, command=self.application.exit)

        self.pack_and_adapt()

    def toggle(self):

        if self.is_visible:
            self.hide()
        else:
            self.show()


class SettingsLanguageZone(SettingsZone):

    def __init__(self, game):

        SettingsZone.__init__(self, game, behind=game.settings_zone, size=game.settings_zone.rect.size,
                              padding=(90, 60, 90 - 40, 60))

        class LangBtn(PE_Button):

            def __init__(btn, lang_id):

                if lang_id not in dicts:
                    raise AssertionError

                PE_Button.__init__(btn, parent=self.scrolled,
                                   text=LANGUAGES_TRANSLATED[lang_id].capitalize(), translatable=False)

                btn.lang_id = lang_id

            def handle_mousebuttondown(btn, event):

                if btn.lang_id == lang_manager.ref_language:
                    return  # can't delete the ref language

                if btn.lang_id == lang_manager.language:
                    return  # can't delete the current language

                if event.button == 3:

                    def delete():
                        dict_path = f"{os.path.abspath(os.path.dirname(sys.argv[0]))}{os.sep}lang{os.sep}" \
                                    f"dict_{btn.lang_id}.py"
                        assert os.path.exists(dict_path), f"Where is the dict file for {btn.lang_id} ?"
                        os.remove(dict_path)
                        dicts.pop(btn.lang_id)
                        btn.kill()
                        self.pack_and_adapt()

                    rightclick_zone = RightClickZone(game, event)
                    rightclick_zone.add_btn(btn_text_id=14, btn_command=delete)

            def handle_validate(btn):

                lang_manager.set_language(btn.lang_id)
                self.behind.lang_btn.set_text(btn.text)
                game.memory.set_lang(btn.lang_id)
                self.hide()

            def set_text(btn, text):

                super().set_text(text)

                if lang_manager.language == btn.lang_id:
                    self.behind.lang_btn.set_text(btn.text)
        self.langbtn_class = LangBtn

        self.scrollview = bp.ScrollView(self, size=(self.behind.content_rect.width + 40,
                                                    self.behind.content_rect.height - 60),
                                        pos=(self.padding.left, self.padding.top))
        self.scrolled = bp.Zone(self.scrollview, spacing=20)

        import os
        import sys
        directory = f"{os.path.abspath(os.path.dirname(sys.argv[0]))}{os.sep}lang"
        for root, dirs, files in os.walk(directory):
            for file_name in files:
                if file_name.endswith(".py") and file_name.startswith("dict_"):
                    lang_id = file_name[5:-3]  # discard 'lang_' and '.py'
                    if lang_id not in dicts:
                        Dictionnary(lang_id)
                    LangBtn(lang_id=lang_id)

        self.add_btn = PE_Button(self, text="+", translatable=False, text_style={"font_height": 35}, padding=0,
                                 topleft=(0, 20), ref=self.scrollview, refloc="bottomleft",
                                 command=bp.PrefilledFunction(SettingsLangAddZone, game, self))

        self.pack_and_adapt()

        self.behind.lang_btn.command = self.show

    def add_lan_btn(self, lang_id):

        with bp.paint_lock:
            new_btn = self.langbtn_class(lang_id=lang_id)
            self.pack_and_adapt()
            return new_btn

    def pack_and_adapt(self):

        def get_sortkey(btn):
            return btn.text
        self.scrolled.default_layer.pack(key=get_sortkey)
        self.scrolled.adapt()
        self.scrollview.resize_height(min(self.scrolled.rect.height, self.behind.content_rect.height - 60))
        self.adapt(self.main_layer)


class SettingsLangAddZone(SettingsZone):

    def __init__(self, game, behind):

        class AddLangBtn(bp.Button):

            STYLE = bp.Button.STYLE.substyle()
            STYLE.modify(
                text_style={"font_height":20}
            )

            def __init__(btn, parent, lang_id, lang):

                bp.Button.__init__(btn, parent, text=lang, background_color=(0, 0, 0, 0), size=(140, 32), padding=2)

                btn.id = lang_id

            def handle_validate(btn):

                if btn.id in dicts:
                    for lang_btn in self.behind.scrolled.default_layer:
                        if lang_btn.lang_id == btn.id:
                            lang_btn.validate()
                            break
                    return self.hide()

                if not lang_manager.is_connected_to_network:
                    return TmpMessage(game, text_id=37, explain_id=34)

                old_cursor = bp.pygame.mouse.get_cursor()
                bp.pygame.mouse.set_cursor(bp.SYSTEM_CURSOR_WAIT)

                try:
                    lang_manager.set_language(btn.id)

                except Exception as e:
                    return TmpMessage(game, text_id=37, explain=str(e))

                finally:
                    bp.pygame.mouse.set_cursor(old_cursor)

                dicts[btn.id].save()

                new_btn = self.behind.add_lan_btn(btn.id)
                new_btn.validate()
                dicts[new_btn.lang_id].save()

                self.hide()
                self.behind.hide()

        class SearchEntry(bp.Entry):

            def handle_keydown(entry, key):

                if key == pygame.K_RETURN:
                    entry.defocus()
                else:
                    super().handle_keydown(key)
                    entry.search()

            def reset(entry):

                if entry.text == "":
                    return

                entry.set_text("")
                for btn in self.langbtns:
                    btn.wake()
                self.scrolled.pack(key=lambda widget: widget.text)
                self.scrolled.adapt()

            def search(entry):

                search_text = entry.text
                for btn in self.langbtns:
                    if not btn.text.lower().startswith(search_text):
                        btn.sleep()
                    else:
                        btn.wake()
                self.scrolled.pack(key=lambda widget: widget.text)
                self.scrolled.adapt()
                self.scrollview.y_scroller.set_val(0)

        SettingsZone.__init__(self, game, behind)
        self.resize(*behind.behind.rect.size)

        self.search = SearchEntry(self, entry_type=str, width=140, padding=7)
        self.scrollview = bp.ScrollView(self, size=(self.content_rect.width + 40, self.content_rect.height - 40))
        self.scrolled = bp.Zone(self.scrollview)

        self.langbtns = []
        inversed_languages_translated = dict(map(reversed, LANGUAGES_TRANSLATED.items()))
        sorted_languages_translated = sorted(inversed_languages_translated)
        for lang in sorted_languages_translated:
            lang_id = inversed_languages_translated[lang]
            self.langbtns.append(AddLangBtn(self.scrolled, lang_id, lang.capitalize()))

        self.scrolled.pack()
        self.scrolled.adapt()

        self.default_layer.pack(spacing=0)

        self.behind.add_btn.command = self.show
        self.scene.focus(self.search)

    def show(self):

        super().show()
        self.scene.focus(self.search)

    def hide(self):

        super().hide()
        self.search.reset()
        self.scrollview.y_scroller.set_val(0)


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
                    self.behind.resolution_btn.set_text(btn.text)
                else:
                    self.application.set_default_size(btn.resolution)

        ResolutionBtn()
        for i in range(min(len(screen_sizes), 7)):
            ResolutionBtn(screen_sizes[i])

        self.pack_and_adapt()

        self.behind.resolution_btn.command = self.show


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
        PE_Button(self, text_id=24, midbottom=(rw1.rect.centerx, rw1.rect.bottom - 5), command=self.hide)
