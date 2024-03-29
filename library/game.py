
import random

import baopig as bp

from library.loading import memory, set_progression, resource_path

from baopig.googletrans import TranslatableText, lang_manager, translator

set_progression(.4)


from library.sound_manager import SoundManager
from library.theme import set_cursor
from library.images import image
from library.buttons import ButtonWithSound, PE_Button, RegionInfoButton
from library.player import Player
from library.zones import BackgroundedZone, BoatInfoZone, CardsZone, ChooseCardZone, GameSail, InfoLeftZone,\
    NextStepZone, PlayerTurnZone, PlayZone, RegionInfoZone, RightClickZone, TmpMessage, WinnerInfoZone
from library.transfer import Transfer
from library.map import Map
from library.region import Boat

set_progression(.5)


class Game(bp.Scene):

    # Gameplay values
    BUILD_PRICE = 3
    CARDS_PER_HAND = 3
    CARD_PRICE = 3
    CARD_SELL_PRICE = 3
    MAX_CHOOSE_REGION_ATTEMPTS = 3
    PRODUCTION_CAMP = 3
    PRODUCTION_MINE = 3
    MAX_SOLDIERS_IN_BOAT = 5
    START_GOLD = 9
    START_SOLDIERS = 4

    def __init__(self, app):

        bp.Scene.__init__(self, app, background_color=(96, 163, 150), can_select=False)

        self.regions = {}  # regions by region_name -> {"alaska": Alaska(...), "alberta: Aberta(...), ...}
        self.regions_list = None
        self.flags = []
        self.current_player_id = 0
        self.turn_index = 0  # 0 is the setup, 1 is the first turn

        # MEMORY
        self.memory = memory
        lang_manager.set_dicts_path(resource_path("lang"))
        lang_manager.set_ref_language("fr")
        lang_manager.set_language(self.memory.lang_id)

        # SOUNDS
        self.sounds = SoundManager(self)

        # SIGNALS
        self.create_signal("PLAYER_TURN")

        # PlAYERS
        self.players = {}
        self.nb_players = None
        def handle_update_language():
            for player in self.players.values():
                player.translated_name = lang_manager.get_text_from_id(player.name_id)
        lang_manager.signal.UPDATE_LANGUAGE.connect(handle_update_language, owner=self)

        # LAYERS
        self.game_layer = bp.Layer(self, level=1, weight=2)
        self.gameinfo_layer = bp.Layer(self, level=1, weight=3)
        self.gametuto_layer = bp.Layer(self, level=1, weight=4)
        self.extra_layer = bp.Layer(self, level=2, weight=2)

        # TUTORIAL
        self.tutoring = False
        self.tuto_text = 38
        def create_tuto_zone():
            self.tutoring = True
            self.settings_zone.tuto_btn.command = switch_tuto
            self.settings_zone.tuto_btn.text_widget.set_ref_text(8)
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
                self.settings_zone.tuto_btn.text_widget.set_ref_text(8)
                self.hibou_animator.set_interval(.45)
                self.tuto_zone.show()
                self.tutoring = True
            else:
                self.settings_zone.tuto_btn.text_widget.set_ref_text(7)
                self.tuto_zone.hide()
                self.tutoring = False

        # SAIL
        self.sail = GameSail(self)

        # PARAMETERS
        from library.zones import SettingsMainZone, SettingsLanguageZone, SettingsResolutionZone, SettingsSoundZone
        self.settings_zone = SettingsMainZone(self)
        self.settings_zone.tuto_btn.command = create_tuto_zone
        self.settings_btn = PE_Button(self, text_id=13, command=self.settings_zone.toggle, layer=self.extra_layer)
        self.settings_btn.move_behind(self.sail)

        # LANGUAGE
        lang_manager.game = self
        translator.game = self
        self.settings_zone.lang_btn.command = bp.PrefilledFunction(SettingsLanguageZone, self)

        # RESOLUTION
        self.settings_zone.resolution_btn.command = bp.PrefilledFunction(SettingsResolutionZone, self)

        # SOUNDS
        SettingsSoundZone(self)  # created from the start because it needs to read the memory

        # MAP
        class Pile(list, bp.Communicative):

            def __init__(pile):

                list.__init__(pile)
                bp.Communicative.__init__(pile)

                pile.create_signal("UPDATE")

            def append(self, *args):
                super().append(*args)

                self.signal.UPDATE.emit()

            def merge_with_discard_pile(pile):
                while self.discard_pile:
                    pile.append(self.discard_pile.pop())

            def pick(pile):

                if len(pile) == 0:

                    if len(self.discard_pile) == 0:
                        return None

                    pile.merge_with_discard_pile()
                    pile.shuffle()

                return pile.pop()

            def pop(self, *args):
                val = super().pop(*args)

                self.signal.UPDATE.emit()

                return val

            def shuffle(pile):
                random.shuffle(pile)

        self.draw_pile = Pile()  # pioche
        self.discard_pile = Pile()  # défausse
        self.map = Map(self)

        # NEXT STEP ANIMATION
        self.nextstep_zone = NextStepZone(self)

        # INFORMATION ON TOP & RIGHT
        self.info_right_zone = bp.Zone(self, sticky="midright", size=("10%", 0), spacing=-3, layer=self.gameinfo_layer)

        # INFORMATION AT LEFT
        self.time_left = bp.Timer(90, self.next_player)
        self.info_left_zone = InfoLeftZone(self)

        # PLAYER TURN
        self.playerturn_zone = None

        # REGION INFO
        self.region_info_zone = RegionInfoZone(self)

        # BOAT ZONE
        self.info_boat_zone = BoatInfoZone(self)

        # REGION CHOOSE
        def rc_next():
            if len(self.players) < self.nb_players:
                self.rc_yes.hide()
                self.rc_no.hide()
                set_cursor("default")
                self.set_step(10)
            else:
                if self.playerturn_zone is None:
                    self.playerturn_zone = PlayerTurnZone(self)
                self.next_player()
                count = 0
                while self.current_player.flag.region is not None:
                    self.next_player()
                    count += 1
                    if count == self.nb_players:
                        self.rc_yes.hide()
                        self.rc_no.hide()
                        self.current_player_id = -1
                        self.next_player()
                        return
                self.pick_region()
                self.playerturn_zone.show()
        def no():
            self.discard_pile.append(self.last_selected_region)
            rc_next()
        def yes():
            self.current_player.flag.set_region(self.last_selected_region)
            self.current_player.cards[0] = self.last_selected_region
            self.current_player.conquer(self.last_selected_region)
            self.last_selected_region.add_soldiers(self.START_SOLDIERS)
            self.current_player.update_soldiers_title()
            rc_next()
        self.rc_yes = RegionInfoButton(self, text_id=21, command=yes)
        self.rc_no = RegionInfoButton(self, text_id=22, command=no)
        self.rc_yes.set_pos(midbottom=(76, 103))

        # WINNER INFO
        self.winner = None
        self.winner_info_zone = WinnerInfoZone(self)

        # NB PLAYERS CHOOSE
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
        class ClickableNb(ButtonWithSound):
            STYLE = ButtonWithSound.STYLE.substyle()
            STYLE.modify(text_style={"font_height":30}, background_color=(0, 0, 0, 24), width=btn_w, height=60*3)
            def __init__(btn, number, pos):
                ButtonWithSound.__init__(btn, self.choose_nb_players_zone, text=str(number), center=pos)
                btn.original_font_height = btn.text_widget.font.height
            def handle_hover(btn):
                btn.text_widget.font.config(height=int(btn.original_font_height * 1.5))
            def handle_unhover(btn):
                btn.text_widget.font.config(height=btn.original_font_height)
            def handle_validate(btn):
                super().handle_validate()
                self.set_step(10)
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
        class ClickableFlag(ButtonWithSound):
            STYLE = ButtonWithSound.STYLE.substyle()
            STYLE.modify(background_color=(0, 0, 0, 24), width=btn_w, height=60*3, hover_class=None)
            def __init__(btn, continent, pos):
                ButtonWithSound.__init__(btn, self.choose_color_zone, center=pos)
                btn.continent = continent
                btn.flag = bp.Image(btn, image.FLAGS[continent], sticky="center")
                btn.flag2 = bp.Image(btn, image.FLAGS_BIG[continent], sticky="center", visible=False)
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
            def handle_validate(btn):
                super().handle_validate()
                Player(self, btn.continent)
                self.next_player()
                self.flags.append(self.current_player.flag)
                self.set_step(11)
                btn.disable()
        self.flag_btns = (
            ClickableFlag("north_america", pos=(centerx - btn_w * 2 - btn_marg * 2 - btn_mid, centery)),
            ClickableFlag("europa", pos=(centerx - btn_w * 1 - btn_marg * 1 - btn_mid, centery)),
            ClickableFlag("asia", pos=(centerx - btn_mid, centery)),
            ClickableFlag("south_america", pos=(centerx + btn_mid, centery)),
            ClickableFlag("africa", pos=(centerx + btn_w * 1 + btn_marg * 1 + btn_mid, centery)),
            ClickableFlag("oceania", pos=(centerx + btn_w * 2 + btn_marg * 2 + btn_mid, centery)),
        )

        # CLICK TO START
        self.play_zone = PlayZone(self)

        # CARDS
        self.cards_zone = CardsZone(self)
        self.choose_card_zone = ChooseCardZone(self)

        # SOLDIERS TRANSFER
        self.transfer = Transfer(self)

        # RIGHT CLICK ZONE
        self.right_click_zone = RightClickZone(self)

        # TODOS
        self.step = None
        self.step_from_id = {}

        self.step = None
        self.step_from_id = {}
        self._init_steps()

        # Start music
        if self.memory.music_is_on:
            self.sounds.start_music()

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
            self.info_right_zone.hide()
        Step(self, 1, start_choosenbplayers, end=self.choose_nb_players_zone.hide)

        def start_choosecolor():
            self.choose_color_zone.show()
            self.set_tuto_ref_text_id(28)
        def end_choosecolor():
            self.choose_color_zone.hide()
            self.info_right_zone.show()
        Step(self, 10, start_choosecolor, end_choosecolor)

        def start_pickregion():
            self.set_tuto_ref_text_id(29)
            self.pick_region()
        Step(self, 11, start=start_pickregion)

        def start_build():
            self.info_left_zone.show()
            self.cards_zone.show()

            for region in self.current_player.regions:
                if region.structure.is_empty:
                    region.structure.show()
                else:
                    if region.structure.is_under_construction:
                        region.structure.end_construction()
                    region.structure.produce()

            if self.current_player.can_build():
                self.set_tuto_ref_text_id(31)
                self.info_left_zone.highlight(self.info_left_zone.build_btn)
            else:
                self.set_step(21)
        def end_build():
            for region in self.current_player.regions:
                if region.structure.is_empty:
                    region.structure.hide()
            if self.choose_card_zone.is_visible:
                self.choose_card_zone.random_choice()
        Step(self, 20, start=start_build, end=end_build)

        def start_attack():
            if self.current_player.can_attack():
                self.set_tuto_ref_text_id(32)
                self.info_left_zone.highlight(self.info_left_zone.attack_btn)
            else:
                self.set_step(22)
        def end_attack():
            if self.transferring:
                self.end_transfer(self.transfer.from_region)
            if self.choose_card_zone.is_visible:
                self.choose_card_zone.random_choice()
        Step(self, 21, start=start_attack, end=end_attack)

        def start_reorganization():
            if self.current_player.can_move_troops():
                self.set_tuto_ref_text_id(33)
                self.info_left_zone.highlight(self.info_left_zone.reorganisation_btn)
            else:
                for player in self.players.values():
                    if player.can_play():
                        return self.next_player()
                self.set_winner(None)
        def end_reorganization():
            if self.transferring:
                self.end_transfer(self.transfer.from_region)
            if self.choose_card_zone.is_visible:
                self.choose_card_zone.random_choice()
        Step(self, 22, start=start_reorganization, end=end_reorganization)

        self.step = self.step_from_id[0]
        self.set_step(0)

    def _set_connected_to_network(self, boolean):
        if boolean:
            raise PermissionError("Can only set game.connected_to_network to False")
        if lang_manager.is_connected_to_network is False:
            return
        lang_manager._is_connected_to_network = False
        self.settings_zone.connection_btn.text_widget.set_ref_text(11)
        # self.settings_zone.connection_btn.enable()
        TmpMessage(self, text_id=34)
    connected_to_network = property(lambda self: lang_manager.is_connected_to_network, _set_connected_to_network)
    current_player = property(lambda self: self.players[self.current_player_id])
    last_selected_region = property(lambda self: self.region_info_zone.last_target)
    selected_region = property(lambda self: self.region_info_zone.target if self.region_info_zone.target
                                            else self.info_boat_zone.target)
    transferring = property(lambda self: self.transfer.from_region is not None)

    def end_transfer(self, region=None):

        assert self.transferring
        if region is None:
            region = self.selected_region
        assert region is not None

        if self.transfer.mode == self.transfer.BOAT_MODE:  # landing the boat

            self.sounds.build.play()

            boat = self.transfer.boat
            boat.wake()

            if self.transfer.from_region is region:  # landing back home
                boat.set_pos(center=Boat.get_valid_center(region))

            else:  # invade region

                boat.set_pos(center=Boat.get_valid_center(region))
                boat.set_region(region)
                assert self.transfer.amount == boat.nb_soldiers
                boat.rem_soldiers(self.transfer.amount)

                if region.owner is None:
                    self.current_player.conquer(region)
                    region.add_soldiers(self.transfer.amount)

                else:
                    deaths = min(self.transfer.amount, region.nb_soldiers)
                    attackers_left = self.transfer.amount - deaths
                    attacked_player = region.owner
                    region.rem_soldiers(deaths)
                    attacked_player.update_soldiers_title()
                    if attacked_player.nb_soldiers == 0:
                        attacked_player.die(attacker=self.current_player)

                    if attackers_left > 0:
                        self.current_player.conquer(region)
                        region.add_soldiers(attackers_left)
                    self.current_player.update_soldiers_title()

                if region.owner is self.current_player:  # region is conquered
                    if self.transfer.has_flag:
                        self.current_player.flag.set_region(region)

                discarded_card = None
                for card in self.cards_zone.current_hand:
                    if hasattr(card, "region") and card.region is region:
                        discarded_card = card
                        break
                assert discarded_card is not None, PermissionError("A boat cannot navigate without using a card")
                discarded_card.discard()

            boat.layer.sort()
            
            self.transfer.end()  # reset transfer
            self.cards_zone.update_invade_btns()  # hide invade button

            self.current_player.flag.show()
            self.current_player.flag.set_touchable_by_mouse(False)
            self.transfer.zone.flag.sleep()

        else:
            refused_soldiers = None  # may happen when adding soldiers to boat
            if region.owner is None:
                self.current_player.conquer(region)
                refused_soldiers = region.add_soldiers(self.transfer.amount)
            elif region.owner is self.transfer.owner:
                refused_soldiers = region.add_soldiers(self.transfer.amount)
            else:
                deaths = min(self.transfer.amount, region.nb_soldiers)
                attackers_left = self.transfer.amount - deaths
                attacked_player = region.owner
                region.rem_soldiers(deaths)
                attacked_player.update_soldiers_title()
                if attacked_player.nb_soldiers == 0:
                    attacked_player.die(attacker=self.current_player)

                if attackers_left > 0:
                    self.current_player.conquer(region)
                    refused_soldiers = region.add_soldiers(attackers_left)
                self.current_player.update_soldiers_title()

            if refused_soldiers is not None:
                self.transfer.set_amount(refused_soldiers)

            else:
                self.transfer.end()

        if self.step.id == 21 and self.winner_info_zone.is_hidden:
            if not self.current_player.can_attack():
                self.set_step(22)
        elif self.step.id == 22:
            if not self.current_player.can_move_troops():
                self.next_player()

    def handle_event(self, event):

        if event.type == bp.MOUSEBUTTONDOWN and event.button == 3:  # right click
            if not self.right_click_zone.collidemouse():
                self.right_click_zone.hide()

    def handle_link_motion(self, rel):

        if self.step.id >= 11 and not self.sail.need_to_be_open():

            self.map.move(*rel)

    def handle_mousebuttondown(self, event):

        if event.button == 3 and self.step.id >= 11 and not self.sail.need_to_be_open():

            if not self.transferring:

                with bp.paint_lock:


                    # rightclick_zone = RightClickZone(self, event)
                    # rightclick_zone.add_btn(btn_text_id=93, btn_command=recenter)

                    # self.scene.right_click_zone.reset()
                    # self.scene.right_click_zone.add_btn(btn_text_id=93, btn_command=recenter)
                    self.scene.right_click_zone.open(mode=RightClickZone.INGAME_MODE)

    def handle_resize(self):

        super().handle_resize()

        text = f"{self.rect.width} × {self.rect.height}"
        self.settings_zone.resolution_btn.set_text(text)

        self.nextstep_zone.resize_width(self.rect.height)
        self.nextstep_zone.circle.set_radius(self.auto_rect.centery)
        self.nextstep_zone.set_pos(x=-self.rect.h)

    def handle_scene_open(self):

        import os
        os.environ['SDL_VIDEO_WINDOW_POS'] = "-1000,300"
        os.environ['SDL_VIDEO_CENTERED'] = '0'

    def next_player(self):

        with bp.paint_lock:

            set_build = False

            if self.selected_region:
                self.region_info_zone.close()

            if self.current_player_id == -1:
                # start of the game
                set_build = True

            elif self.step.id >= 20:

                set_build = True
                self.step.end()

                if self.turn_index >= 0 and self.current_player_id == len(self.players) - 1:
                    self.turn_index += 1

            self.current_player_id = (self.current_player_id + 1) % len(self.players)
            if not self.current_player.is_alive:
                self.next_player()
                return

            if set_build:
                self.set_step(20)
                if not self.winner:
                    self.playerturn_zone.show()

            if self.time_left.is_running:
                self.time_left.cancel()
            if self.step.id >= 20:
                self.time_left.start()

            set_cursor(self.current_player.name)

            self.signal.PLAYER_TURN.emit()

    def next_step(self):

        if self.step.id == 22:
            self.next_player()
        else:
            self.set_step(self.step.id + 1)

    def newgame_setup(self):

        # TODO : mute soldier sounds during reset

        self.winner = None

        for player in self.players.values():
            for card in player.cards:
                if card is not None:
                    self.draw_pile.append(card)
        self.draw_pile.merge_with_discard_pile()
        self.draw_pile.shuffle()

        for r in self.regions.values():
            r.flag = None
            r.structure.destroy()
            for boat in r.boats:
                boat.kill()
            r.boats = []

        for p in self.players.values():
            for r in tuple(p.regions):
                r.rem_soldiers(r.nb_soldiers)
            p.flag.kill()
        self.players = {}
        self.flags = []

        for w in self.choose_color_zone.children:
            if isinstance(w, bp.Button):
                w.enable()

        for z in tuple(self.info_right_zone.children):
            z.kill()
        if self.playerturn_zone is not None:
            self.playerturn_zone.kill()
            self.playerturn_zone = None
        self.info_left_zone.hide()
        self.cards_zone.hide()
        self.cards_zone.reset()
        self.winner_info_zone.hide()
        if self.time_left.is_running:
            self.time_left.cancel()

        self.map.map_image.pos_manager.config(pos=(0, 0))

        set_cursor("default")

    def pick_region(self):

        picked = self.draw_pile.pick()

        self.region_info_zone.open(picked)
        # self.map.region_select(picked)

        player = self.current_player
        player.choose_region_attemps += 1
        if player.choose_region_attemps < self.MAX_CHOOSE_REGION_ATTEMPTS:
            self.rc_yes.show()
            self.rc_no.show()
        else:
            self.rc_yes.command()

    def set_step(self, index):

        self.step.end()

        if self.transferring:
            raise AssertionError

        self.step = self.step_from_id[index]

        if self.selected_region is not None:
            self.region_info_zone.close()
        self.step.start()
        if self.winner:
            return  # draw

        if self.step.id >= 20:
            if self.nextstep_zone.circle_animator.is_running:
                self.nextstep_zone.circle_animator.cancel()
            if not self.nextstep_zone.circle_animator.is_paused:  # can be paused by PlayerTurnZone
                self.nextstep_zone.circle_animator.start()
            self.nextstep_zone.set_pos(right=0)
            self.nextstep_zone.show()

    def set_tuto_ref_text_id(self, text_id):
        self.tuto_ref_text_id = text_id
        if isinstance(self.tuto_text, TranslatableText):
            self.tuto_text.set_ref_text(text_id)
        else:
            self.tuto_text = text_id

    def set_winner(self, winner):

        if winner is not None:
            self.sounds.win.play()

        if winner is None:
            self.winner_info_zone.title.set_text(lang_manager.get_text_from_id(96))
            self.winner_info_zone.panel.set_background_color(BackgroundedZone.STYLE["background_color"])
            self.winner = "draw"
        else:
            self.winner_info_zone.title.complete_text()
            self.winner_info_zone.panel.set_background_color(winner.color)
            self.winner = winner
        self.nextstep_zone.circle_animator.cancel()
        self.nextstep_zone.hide()
        self.time_left.pause()
        self.region_info_zone.close()
        self.winner_info_zone.show()
        self.winner_info_zone.panel.show()
        self.set_tuto_ref_text_id(45)

    def start_transfer(self, region):

        self.playerturn_zone.hide()
        self.region_info_zone.close()
        self.info_boat_zone.close()

        if isinstance(region, Boat):

            boat = region

            if self.step.id == 21:  # boat transfer

                self.sounds.build.play()

                assert not self.transferring
                assert boat.nb_soldiers > 0

                self.transfer.from_region = boat.region
                self.transfer.destination_names = boat.get_destination_names()
                self.transfer.owner = boat.owner
                self.transfer.boat = boat
                boat.sleep()
                self.transfer.set_mode(Transfer.BOAT_MODE, amount=boat.nb_soldiers)

                self.current_player.flag.set_touchable_by_mouse(True)

            elif self.step.id == 22:  # boat's soldiers transfer

                # 2 actions :
                #   - pick soldiers from boat
                #   - add soldiers to boat

                if boat.nb_soldiers <= boat.MIN:  # Cannot pick soldiers from boat, so we put soldiers in the boat
                    if self.transferring:
                        self.end_transfer(boat)
                    return

                if self.transferring and self.transfer.from_region != boat:
                    if boat.region.name in self.transfer.destination_names:
                        self.end_transfer(boat)
                    return

                region = boat.region
                self.transfer.from_region = boat
                self.transfer.destination_names = region.all_allied_neighbors
                self.transfer.destination_names.add(region.name)
                self.transfer.owner = region.owner
                amount = boat.nb_soldiers - boat.MIN if bp.keyboard.mod.maj else 1
                boat.rem_soldiers(amount)
                self.transfer.set_mode(Transfer.SOLDIERS_MODE, amount=self.transfer.amount + amount)

            else:
                raise PermissionError(f"Cannot transfer during step n°{self.step.id}")

            self.cards_zone.update_invade_btns()

        elif self.transferring:

            if self.transfer.mode == self.transfer.BOAT_MODE:  # landing the boat
                self.end_transfer(region)

            elif self.transfer.from_region is region:
                if region.nb_soldiers <= region.MIN:
                    self.end_transfer(region)
                else:
                    self.region_info_zone.close()
                    amount = region.nb_soldiers - region.MIN if bp.keyboard.mod.maj else 1
                    region.rem_soldiers(amount)
                    self.transfer.set_amount(self.transfer.amount + amount)
            else:
                self.end_transfer(region)

        else:
            if region.nb_soldiers <= region.MIN:
                return

            self.transfer.from_region = region
            if self.step.id == 21:
                self.transfer.destination_names = region.neighbors
            elif self.step.id == 22:
                self.transfer.destination_names = region.all_allied_neighbors
            else:
                raise PermissionError(f"Cannot transfer during step n°{self.step.id}")
            self.transfer.owner = region.owner
            amount = region.nb_soldiers - region.MIN if bp.keyboard.mod.maj else 1
            region.rem_soldiers(amount)
            self.transfer.set_mode(Transfer.SOLDIERS_MODE, amount=amount)
