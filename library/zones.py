
import math
import random
import baopig as bp
from baopig.googletrans import Dictionnary, TranslatableText, PartiallyTranslatableText, dicts, lang_manager,\
    LANGUAGES_TRANSLATED
import pygame
from library.images import FLAGS_BIG, SOLDIERS, boat_back, boat_front
from library.loading import logo, screen_size, screen_sizes
from library.buttons import PE_Button, PE_Button_Text, TransferButton
from library.region import SoldiersContainer, Structure, back, front, hover


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

        self.max_radius = sum(screen_size) / 2
        self.animator = bp.RepeatingTimer(.03, self.animate)

        from baopig.pybao import WeakList
        self._targets = WeakList()

    def need_to_be_open(self):

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

        if self.need_to_be_open():
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

        if self.need_to_be_open():
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

    INGAME_MODE = 0
    CUSTOM_MODE = 1

    def __init__(self, game):

        BackgroundedZone.__init__(self, game, layer=game.extra_layer, visible=False, padding=(2, 6))
        bp.Focusable.__init__(self, game)

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
                btn.parent.hide()

        RightClickButton(self, text_id=btn_text_id, command=btn_command, pos=(0, 10000),
                         background_color=(0, 0, 0, 0), size=(220, 32), padding=2,
                         text_style={"font_height":20})
        self.pack()
        self.adapt()

    def handle_defocus(self):

        if self.scene.focused_widget.parent is not self:
            self.hide()

    def open(self, mode, custom_btns=()):

        self.scene.right_click_zone.reset()

        if mode == self.INGAME_MODE:
            def recenter():
                self.scene.map.pos_manager.config(pos=(0, 0))
            self.scene.right_click_zone.add_btn(btn_text_id=93, btn_command=recenter)

        elif mode == self.CUSTOM_MODE:

            for btn in custom_btns:
                self.scene.right_click_zone.add_btn(btn_text_id=btn[0], btn_command=btn[1])

        else:
            raise ValueError(f"Unknwon mode : {mode}")

        self.layer.move_on_top(self)
        self.set_pos(topleft=bp.mouse.pos)
        self.show()
        self.scene.focus(self)

    def reset(self):

        for child in tuple(self.children):
            child.kill()


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


class MaintainableByFocus(bp.Widget):
    """ Class for widgets who need to be open as long as they have a focused maintainer """

    def __init__(self, parent, is_valid_maintainer):

        bp.Widget.__init__(self, parent)

        self._maintainer_ref = lambda: None  # this is the child that is focused
        self.is_valid_maintainer = is_valid_maintainer

    maintainer = property(lambda self: self._maintainer_ref())

    def _handle_maintainer_defocus(self):

        self.maintainer.signal.DEFOCUS.disconnect(self._handle_maintainer_defocus)

        focused_widget = self.scene.focused_widget
        if focused_widget is None:
            return self.close()

        if self.is_valid_maintainer(focused_widget):
            self._maintainer_ref = focused_widget.get_weakref()
            self.maintainer.signal.DEFOCUS.connect(self._handle_maintainer_defocus, owner=self)

        else:
            self.close()

    def close(self):
        """ Stuff to do when there is no focused maintainer anymore """

    def open(self, maintainer):

        if not self.is_valid_maintainer(maintainer):
            raise PermissionError(f"Invalid maintainer : {maintainer}")

        self._maintainer_ref = maintainer.get_weakref()
        self.maintainer.signal.DEFOCUS.connect(self._handle_maintainer_defocus, owner=self)


class InfoZone(BackgroundedZone, bp.Focusable, bp.MaintainableByFocus):

    class RegionTitle(TranslatableText):

        def set_region(self, region):
            if region.upper_name == self.text:
                return
            self.set_ref_text(region.upper_name_id)

    def __init__(self, game):

        BackgroundedZone.__init__(self, game, size=(152, 152), visible=False, layer=game.game_layer,
                                  ref=game.map.map_image)
        bp.Focusable.__init__(self, game)

        def is_valid_maintainer(widget):

            if isinstance(widget, SoldiersContainer) and self.target is None:
                return True

            if widget.is_asleep:  # usefull in this particular case
                return False

            while True:

                if widget is self:
                    return True

                widget = widget.parent
                if widget.scene == widget:
                    return False
        bp.MaintainableByFocus.__init__(self, game, is_valid_maintainer=is_valid_maintainer)

        self._target_ref = lambda: None

        self.title_outline = bp.Rectangle(self, size=(self.rect.w, 44), color=(0, 0, 0, 0),
                                          border_width=2, border_color="black")

    target = property(lambda self: None if self.is_hidden else self._target_ref())
    last_target = property(lambda self: self._target_ref())

    def _handle_maintainer_defocus_tbr(self):

        self._maintainer.signal.DEFOCUS.disconnect(self._handle_maintainer_defocus)

        focused = self.scene.focused_widget
        if focused is None:
            return self.close()

        widget = focused

        if widget.is_asleep:  # usefull in this particular case
            return self.close()

        while True:

            if widget is self:
                break

            widget = widget.parent
            if widget.scene == widget:
                return self.close()

        self._maintainer = focused
        self._maintainer.signal.DEFOCUS.connect(self._handle_maintainer_defocus, owner=self)

    def close(self):

        if self.is_hidden:
            return

        self.target.handle_unhover()
        self.target.hover.sleep()

        self.hide()

    def open(self, target):

        self._target_ref = lambda: None
        super().open(maintainer=target)
        self._target_ref = target.get_weakref()

        # self._maintainer = target
        # self._maintainer.signal.DEFOCUS.connect(self._handle_maintainer_defocus, owner=self)

        with bp.paint_lock:
            self.set_pos(midleft=(target.abs_rect.right + 10, target.abs_rect.centery))
            self.show()

            target.hover.wake()


class BoatInfoZone(InfoZone):

    def __init__(self, game):

        InfoZone.__init__(self, game)

        self.region_title = self.RegionTitle(self, align_mode="center", sticky="center", ref=self.title_outline,
                         max_width=self.rect.w - 10, text_id=48)

        self.continent = "north_america"

        boat = pygame.Surface(front.get_size(), pygame.SRCALPHA)
        boat.blit(back, (2, 0))
        boat.blit(hover, (0, 0))
        bp.Image(self, sticky="center", image=back, pos=(0, 6))
        self.soldiers_zone = bp.Zone(self, sticky="center", pos=(0, -2), spacing=-1)
        bp.Image(self, sticky="center", image=hover, pos=(0, 8))

        self.soldiers = ()
        for i in range(self.scene.MAX_SOLDIERS_IN_BOAT):
            soldier = bp.Image(self.soldiers_zone, image=SOLDIERS[self.continent])
            soldier.sleep()
            self.soldiers += (soldier,)

        class PlusMinusButton(PE_Button):

            def handle_validate(btn):

                if self.target.owner and self.target.region.owner != self.target.owner:
                    return
                if self.target.owner is None and self.target.region.owner != self.scene.current_player:
                    return

                with bp.paint_lock:
                    if btn.text == "+":
                        if self.target.nb_soldiers < 5 and self.target.region.nb_soldiers > 1:
                            self.target.add_soldiers(1)
                            self.target.region.rem_soldiers(1)
                            self.soldiers[self.target.nb_soldiers-1].wake()
                            self.soldiers_zone.pack(axis="horizontal")
                            self.soldiers_zone.adapt()
                    else:
                        if self.target.nb_soldiers > 0:
                            self.target.rem_soldiers(1)
                            self.target.region.add_soldiers(1)
                            self.soldiers[self.target.nb_soldiers].sleep()
                            self.soldiers_zone.pack(axis="horizontal")
                            self.soldiers_zone.adapt()

        self.set_style_for(PlusMinusButton, width=25, height=25, padding=0)

        self.minus = PlusMinusButton(self, midleft=(6, self.soldiers_zone.rect.centery + 5), text="-", translatable=False)
        self.plus = PlusMinusButton(self, midright=(self.rect.width - 6, self.soldiers_zone.rect.centery + 5), text="+",
                                    translatable=False)
        self.invade_btn = TransferButton(game, zone=self, text_id=4)
        self.import_btn = TransferButton(game, zone=self, text_id=20)

    def open(self, boat):

        with bp.paint_lock:

            super().open(boat)

            owner = boat.owner if boat.owner else boat.region.owner
            if owner and owner.continent != self.continent:
                self.continent = owner.continent
                for soldier in self.soldiers:
                    soldier.set_surface(SOLDIERS[self.continent])

            self.update_nb_soldiers(boat)

            self.region_title.set_region(boat.region)

            if self.scene.step.id == 22 and (boat.owner == self.scene.current_player == boat.region.owner or
                                             (boat.owner is None and self.scene.current_player == boat.region.owner)):
                self.minus.show()
                self.plus.show()
            else:
                self.minus.hide()
                self.plus.hide()

            self.invade_btn.hide()
            self.import_btn.hide()
            if self.scene.transferring:
                if self.scene.step.id == 21:
                    if boat.owner != self.scene.transfer.owner and boat.region.owner is self.scene.transfer.owner:
                        self.invade_btn.show()
                elif self.scene.step.id == 22:
                    if boat.region is self.scene.transfer.from_region or \
                            boat.region.name in self.scene.transfer.destination_names:
                        self.import_btn.show()

    def update_nb_soldiers(self, boat):

            for i in range(self.scene.MAX_SOLDIERS_IN_BOAT):
                if i < boat.nb_soldiers:
                    self.soldiers[i].wake()
                else:
                    self.soldiers[i].sleep()

            self.soldiers_zone.pack(axis="horizontal")
            self.soldiers_zone.adapt()


class RegionInfoZone(InfoZone):

    def __init__(self, game):

        InfoZone.__init__(self, game)

        self.region_title = self.RegionTitle(self, align_mode="center", sticky="center", ref=self.title_outline,
                                             max_width=self.rect.w - 10, text_id=48)

        self.soldier_zone = bp.Zone(self, sticky="center", pos=(0, -10), spacing=5)
        self.soldier_amount = bp.Text(self.soldier_zone, "")
        self.soldier_icon = bp.Image(self.soldier_zone, SOLDIERS["asia"])

        game.region_info_zone = self
        self.invade_btn = TransferButton(game, zone=self, text_id=4)
        self.back_btn = TransferButton(game, zone=self, text_id=19)
        self.import_btn = TransferButton(game, zone=self, text_id=20)
        self.choose_build_zone = ChooseBuildZone(self)

        for region in game.regions.values():
            region.info_zone = self

    def open(self, region=None):

        region = self.scene.selected_region if region is None else region

        super().open(region)

        self.region_title.set_region(region)

        if region.owner is None:
            self.soldier_zone.hide()
        else:
            self.soldier_amount.set_text(str(region.nb_soldiers))
            self.soldier_icon.set_surface(region.owner.soldier_icon)
            self.soldier_zone.pack(axis="horizontal")
            self.soldier_zone.adapt()
            self.soldier_zone.show()

        self.invade_btn.hide()
        self.back_btn.hide()
        self.import_btn.hide()

        if self.scene.step.id == 20 and region.owner is self.scene.current_player:
            self.choose_build_zone.update()
        else:
            self.choose_build_zone.hide()
        if self.scene.step.id == 21 and self.scene.transferring:
            if region.name in self.scene.transfer.destination_names and region.owner != self.scene.transfer.owner:
                self.invade_btn.show()
            elif region is self.scene.transfer.from_region:
                self.back_btn.show()
        elif self.scene.step.id == 22 and self.scene.transferring:
            if region is self.scene.transfer.from_region:
                self.back_btn.show()
            elif region.name in self.scene.transfer.destination_names:
                self.import_btn.show()


class CardTemplate(BackgroundedZone):

    FULL_SIZE = (152, int(152 * 1.6))
    COMPACT_SIZE = (152, 44)

    def __init__(self, parent, region, **kwargs):

        if "size" not in kwargs:
            kwargs["size"] = self.FULL_SIZE

        BackgroundedZone.__init__(self, parent, **kwargs)

        self.region = region

        self.title_zone = BackgroundedZone(self, size=CardTemplate.COMPACT_SIZE)
        self.title = TranslatableText(self.title_zone, text_id=region.upper_name_id, sticky="center",
                                      max_width=self.content_rect.w - 6, align_mode="center")


class CardsZone(BackgroundedZone, bp.Focusable, bp.MaintainableByFocus):

    class Card(CardTemplate, bp.LinkableByMouse):

        def __init__(self, cards_zone, region, slot_id):

            CardTemplate.__init__(self, cards_zone, region=region, size=cards_zone.current_slot_size,
                                  pos=cards_zone.add_buttons[slot_id].rect.topleft)
            bp.LinkableByMouse.__init__(self, cards_zone)

            self.slot_id = slot_id
            self.purchase_turn = self.scene.turn_index

            self.sell_btn = PE_Button(self, text_id=98, pos=(0, -6), sticky="midbottom", visible=False,
                                      command=self.sell)
            self.sell_btn.sleep()

            def invade():
                self.scene.end_transfer(region=region)
                cards_zone.close()
            self.invade_btn = PE_Button(self, text_id=4, pos=(0, -6), sticky="midbottom", visible=False, command=invade)
            self.invade_btn.sleep()

        def decrease(self):
            self.resize(*CardTemplate.COMPACT_SIZE)
            self.sell_btn.sleep()
            self.invade_btn.sleep()

        def discard(self):
            hand = self.parent.current_hand
            for i, card in enumerate(hand):
                if card is self:
                    self.parent.add_buttons[i].show()
                    hand[i] = self.parent.add_buttons[i]
                    self.scene.current_player.cards[i] = None
                    break

            self.scene.discard_pile.append(self.region)
            self.kill()

        def handle_hover(self):

            self.region.hover.wake()

        def handle_link(self):

            self.parent.open()

        def handle_unhover(self):

            if self.region.has_infozone_open:
                return

            self.region.hover.sleep()

        def increase(self):
            self.resize(*CardTemplate.FULL_SIZE)
            self.sell_btn.wake()
            self.invade_btn.wake()

        def sell(self):
            self.discard()
            self.scene.current_player.change_gold( + self.scene.CARD_SELL_PRICE)

        def update_sell_btn(self):

            if self.scene.turn_index > self.purchase_turn:
                self.sell_btn.show()

    class AddCardButton(PE_Button):

        class HoverableDisableSail(PE_Button.STYLE["disable_class"], bp.HoverableByMouse):

            def __init__(self, *args, **kwargs):

                PE_Button.STYLE["disable_class"].__init__(self, *args, **kwargs)
                bp.HoverableByMouse.__init__(self, self.parent)

        from baopig.googletrans import TranslatableIndicator
        class DisableIndicator(TranslatableIndicator):

            def wake(self):

                if not self.scene.draw_pile:
                    self.set_ref_text(text_id=95)
                else:
                    self.set_ref_text(text_id=94)

                super().wake()

        STYLE = PE_Button.STYLE.substyle()
        STYLE.modify(
            disable_class=HoverableDisableSail,
        )

        def __init__(self, cards_zone, slot_id):
            PE_Button.__init__(self, cards_zone, text="+", translatable=False, size=CardTemplate.COMPACT_SIZE,
                               command=self.buy_card)
            self.slot_id = slot_id

            self.DisableIndicator(target=self.disable_sail, parent=self.scene, align_mode="center", text_id=94)

        def buy_card(self):
            if self.disable_sail.is_visible:
                return

            self.scene.choose_card_zone.slot_destination = self.slot_id
            self.scene.choose_card_zone.show()

        def decrease(self):
            self.resize(*CardTemplate.COMPACT_SIZE)

        def handle_link(self):

            if self.disable_sail.is_visible:
                return

            super().handle_link()

        def increase(self):
            self.resize(*CardTemplate.FULL_SIZE)

        def set_touchable_by_mouse(self, val):

            if val:
                self.disable_sail.hide()
            else:
                self.disable_sail.show()

    def __init__(self, game):

        BackgroundedZone.__init__(self, game, sticky="midbottom", pos=(0, 2), visible=False, padding=8, spacing=4)
        bp.Focusable.__init__(self, game)

        def is_valid_maintainer(widget):

            while True:
                if widget is self:
                    return True

                widget = widget.parent
                if widget.scene == widget:
                    return False
        bp.MaintainableByFocus.__init__(self, game, is_valid_maintainer)

        self.set_style_for(
            self.AddCardButton,
            text_style={"font_height": 35},
            padding=0,
        )

        self.toggler = PE_Button(self, text="^", translatable=False, size=(44, 44), command=self.open,
                                 text_style={"font_height": 35}, padding=0)

        self.add_buttons = []
        for i in range(game.CARDS_PER_HAND):
            self.add_buttons.append(self.AddCardButton(self, slot_id=i))

        self.hands = {}  # self.hands[a_player] -> CARDS_PER_HAND widgets (Card or AddCardButton)
        self.current_hand = self.add_buttons.copy()

        self.default_layer.pack(axis="horizontal")
        self.adapt(self.default_layer)

        self.current_player = None

        game.signal.PLAYER_TURN.connect(self.handle_player_turn, owner=self)
        game.draw_pile.signal.UPDATE.connect(self.update, owner=self)

    current_slot_size = property(lambda self: CardTemplate.FULL_SIZE if self.is_open else CardTemplate.COMPACT_SIZE)
    is_open = property(lambda self: self.rect.height > 150)

    def add_card(self, region, slot_id):  # called by ChooseCardZone.Card.handle_link()

        if self.scene.transferring and self.scene.transfer.mode == 1:  # BOAT_MODE
            self.scene.transfer.destination_names += (region.name,)

        card = self.Card(self, region=region, slot_id=slot_id)
        self.current_hand[slot_id] = card

        self.scene.current_player.cards[slot_id] = region
        self.scene.current_player.change_gold( - self.scene.CARD_PRICE)

    def close(self):

        for slot in self.current_hand:
            slot.decrease()
        for btn in self.add_buttons:
            btn.decrease()

        self.resize_height(44 + self.padding.top * 2)

        self.toggler.set_text("^")
        self.toggler.command = self.open

    def handle_focus(self):

        self.open(maintainer=self)

    def handle_player_turn(self):

        if self.scene.step.id < 20:
            return

        if self.is_open:
            self.close()

        for slot in self.current_hand:
            slot.hide()

        try:
            self.current_hand = self.hands[self.scene.current_player]

        except KeyError:
            flag_region_card = self.Card(self, region=self.scene.current_player.flag.region, slot_id=0)
            self.current_hand = bp.pybao.WeakList((flag_region_card,) + tuple(self.add_buttons[1:]))
            self.hands[self.scene.current_player] = self.current_hand

        for slot in self.current_hand:
            slot.show()

        # if not self.scene.players:
        #     return

        if self.current_player is not None:
            self.current_player.signal.CHANGE_GOLD.disconnect(self.update)
        self.current_player = self.scene.current_player
        self.current_player.signal.CHANGE_GOLD.connect(self.update, owner=self)

        # Update add buttons
        self.update()

        # Update sell button visibility
        for slot in self.current_hand:
            if isinstance(slot, CardsZone.Card):
                slot.update_sell_btn()

    def open(self, maintainer=None):

        if maintainer is None:
            return self.scene.focus(self)

        super().open(maintainer)

        for slot in self.current_hand:
            slot.increase()
        for btn in self.add_buttons:
            btn.increase()

        self.resize_height(CardTemplate.FULL_SIZE[1] + self.padding.top * 2)

        self.toggler.set_text("-")
        self.toggler.command = self.close

    def reset(self):

        for slots in self.hands.values():
            for widget in slots:
                if not isinstance(widget, PE_Button):
                    widget.kill()

    def update(self):

        if self.current_player is None:
            return

        if self.current_player.gold < self.scene.CARD_PRICE or \
                (not self.scene.draw_pile and not self.scene.discard_pile):
            for btn in self.add_buttons:
                btn.disable()
        else:
            for btn in self.add_buttons:
                btn.enable()

        self.update_invade_btns()

    def update_invade_btns(self):

        def can_invade(region):
            # mode == 1 for Transfer.BOAT_MODE
            return self.scene.transferring and self.scene.transfer.mode == 1 and \
                   region.name in self.scene.transfer.destination_names and region.owner != self.scene.transfer.owner

        for card in self.current_hand:
            if not hasattr(card, "region"):
                continue
            if can_invade(card.region):
                card.invade_btn.show()
            else:
                card.invade_btn.hide()


class ChooseCardZone(BackgroundedZone):

    NB_PICKS = 4

    class Card(CardTemplate, bp.LinkableByMouse):

        HOVER_COLOR = bp.Vector3(BackgroundedZone.STYLE["background_color"]) * .8

        def __init__(self, parent, *args, **kwargs):

            CardTemplate.__init__(self, parent, *args, **kwargs)
            bp.LinkableByMouse.__init__(self, parent)

        def handle_hover(self):

            self.set_background_color(self.HOVER_COLOR)
            self.title_zone.set_background_color(self.HOVER_COLOR)

        def handle_link(self):

            self.parent.hide()

            self.scene.cards_zone.add_card(self.region, self.parent.slot_destination)

            for card in self.parent.cards:
                if card is self:
                    continue
                self.scene.discard_pile.append(card.region)

        def handle_unhover(self):

            self.set_background_color(BackgroundedZone.STYLE["background_color"])
            self.title_zone.set_background_color(BackgroundedZone.STYLE["background_color"])

        def set_region(self, region):

            self.region = region
            self.title.set_ref_text(region.upper_name_id)

    def __init__(self, game,  **kwargs):

        spacing = 60
        border_width = BackgroundedZone.STYLE["border_width"]

        BackgroundedZone.__init__(self, game, sticky="center", layer=game.extra_layer, visible=False,
                                  padding=spacing + border_width, spacing=spacing, **kwargs)

        self.cards = [self.Card(self, game.regions["alaska"]) for _ in range(self.NB_PICKS)]
        self.slot_destination = None
        self.pack(axis="horizontal")
        self.adapt()

        game.sail.add_target(self)

    def random_choice(self):

        valid_choices = tuple(card for card in self.cards if card is not None)
        choice = random.choice(valid_choices)
        choice.handle_link()

    def show(self):

        for card in self.cards:
            picked = self.scene.draw_pile.pick()
            if picked is None:
                card.hide()
            else:
                card.set_region(picked)

        super().show()


class ChooseBuildZone(bp.Zone):

    def __init__(self, parent):

        spacing = 7
        size = int((140 - spacing * 2) / 3)
        bp.Zone.__init__(self, parent, visible=False, pos=(0, -6), sticky="midbottom",
                         size=(140, size), spacing=spacing)

        mine_background = pygame.Surface((size, size), pygame.SRCALPHA)
        mine_background.blit(Structure.DONE, (size / 2 - 15, size / 2 - 15))
        camp_background = mine_background.copy()
        mine_background.blit(Structure.MINE, (size / 2 - 15, size / 2 - 15))
        camp_background.blit(Structure.CAMP, (size / 2 - 15, size / 2 - 15))
        boat_background = pygame.Surface((80, 80), pygame.SRCALPHA)
        boat_background.blit(boat_back, (40 - 68 / 2, 40 - 20 / 2))
        boat_background.blit(boat_front, (40 - 73 / 2, 43 - 26 / 2))

        class BuildButton(bp.Button):

            def __init__(btn, image, name):

                bp.Button.__init__(btn, self, "", size=(size, size), background_image=image, name=name)

            def handle_validate(btn):

                if self.scene.current_player.gold < self.scene.BUILD_PRICE:
                    return TmpMessage(self.scene, text_id=97)
                if btn.name == "boat":
                    self.parent.last_target.add_boat()
                else:
                    self.parent.last_target.structure.start_construction(btn.name)
                    self.camp_btn.disable()
                    self.mine_btn.disable()
                self.scene.current_player.change_gold( - self.scene.BUILD_PRICE)
        self.mine_btn = BuildButton(image=mine_background, name="mine")
        self.baot_btn = BuildButton(image=boat_background, name="boat")
        self.camp_btn = BuildButton(image=camp_background, name="camp")
        self.pack(axis="horizontal")

    def update(self):
        self.show()
        if self.scene.last_selected_region.structure.is_empty:
            self.camp_btn.enable()
            self.mine_btn.enable()
        else:
            self.camp_btn.disable()
            self.mine_btn.disable()


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
        self.build_btn = InfoLeftButton(stepbtns_zone, text_id=16, step_id=20)
        self.build_btn.disable()
        self.attack_btn = InfoLeftButton(stepbtns_zone, text_id=17, step_id=21)
        self.reorganisation_btn = InfoLeftButton(stepbtns_zone, text_id=18, step_id=22)
        stepbtns_zone.pack()
        stepbtns_zone.adapt()

        nextstep_zone = bp.Zone(self, padding=(padding, 40, padding, padding))
        self.next_player_btn = PE_Button(nextstep_zone, text_id=15, background_color=self.standard_color,
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

        if btn == self.build_btn:
            self.scene.nextstep_zone.text.set_text(self.build_btn.text)
            self.attack_btn.enable()
            self.reorganisation_btn.enable()
        elif btn == self.attack_btn:
            self.scene.nextstep_zone.text.set_text(self.attack_btn.text)
            self.reorganisation_btn.enable()
        elif btn == self.reorganisation_btn:
            self.scene.nextstep_zone.text.set_text(self.reorganisation_btn.text)
            self.attack_btn.disable()


class NextStepZone(bp.Zone):

    def __init__(self, game):

        bp.Zone.__init__(self, game, pos=(-game.rect.h, 0), size=(game.rect.h, "100%"), layer=game.gameinfo_layer,
                         touchable=False)

        def nextsail_animate():
            self.move(dx=max(abs(self.rect.centerx - game.auto_rect.centerx) / 5, 20))
            if self.rect.left >= game.rect.width:
                self.circle_animator.cancel()
                self.hide()

        self.circle_animator = bp.RepeatingTimer(.04, nextsail_animate)
        self.circle = bp.Circle(self, (0, 0, 0, 63), radius=game.auto_rect.centery, sticky="center")
        self.text = bp.Text(self, "HELLO !!", font_height=50, font_color="orange", font_bold=True, sticky="center",
                            ref=game)


class PlayerTurnZone(BackgroundedZone, bp.Focusable):

    def __init__(self, game):

        BackgroundedZone.__init__(self, game, size=(650, 650), sticky="center", visible=False)
        bp.Focusable.__init__(self, game)

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

        game.map.signal.REGION_SELECT.connect(self.hide, owner=self)

    def handle_defocus(self):

        if self.scene.focused_widget is self.scene.info_left_zone.next_player_btn:
            return
        self.hide()

    def handle_link(self):

        self.defocus()

    def hide(self):

        if self.is_hidden:
            return

        super().hide()

        if self.hide_timer.is_running:
            self.hide_timer.cancel()

        if self.scene.step.id >= 20:
            self.scene.nextstep_zone.circle_animator.resume()

    def show(self):

        was_hidden = self.is_hidden

        super().show()

        self.scene.focus(self)

        self.select_origin = self.select.rect.center
        self.select_dest = self.flags[self.scene.current_player.id].rect.center
        self.select_travel = pygame.Vector2(self.select_dest) - self.select_origin
        if was_hidden:
            self.select_movement = -.2
        else:
            self.select_movement = 0
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
            self.scene.nextstep_zone.circle_animator.pause()


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


class ClosableZone(BackgroundedZone):

    def __init__(self, game, visible=False, **kwargs):

        BackgroundedZone.__init__(self, game, sticky="center", layer=game.extra_layer, visible=visible, **kwargs)

        PE_Button(self, text="X", pos=(-10, 10), sticky="topright", layer_level=2, translatable=False, size=(40, 40),
                  background_color=(150, 20, 20), command=self.close)

        game.sail.add_target(self)

    def close(self):
        """Stuff to do when the X button is pressed"""


class SettingsZone(ClosableZone):

    def __init__(self, game, behind=None, padding=(90, 60), **kwargs):

        ClosableZone.__init__(self, game, spacing=20, padding=padding, visible=bool(behind), **kwargs)

        self.game = game
        self.behind = behind

        if behind:
            PE_Button(self, text="<", pos=(10, 10), layer_level=2, translatable=False, size=(40, 40),
                      command=self.hide, text_style={"font_height": 35}, padding=0)

        self.main_layer = bp.Layer(self)

    def pack_and_adapt(self):

        self.main_layer.pack()
        self.adapt(self.main_layer)
        if self.behind is not None:
            self.resize(width=max(self.rect.width, self.behind.rect.width),
                        height=max(self.rect.height, self.behind.rect.height))

    def close(self):
        if self.behind is not None:
            self.behind.close()
        self.hide()


class SettingsMainZone(SettingsZone):

    def __init__(self, game):

        SettingsZone.__init__(self, game)

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
                        game.draw_pile.append(game.selected_region)
                        alaska = game.regions_list[0]
                        game.draw_pile.remove(alaska)
                        game.region_info_zone.open(alaska)
                        game.rc_yes.validate()
                        game.flag_btns[2].validate()
                        game.draw_pile.append(game.selected_region)
                        alberta = game.regions_list[1]
                        game.draw_pile.remove(alberta)
                        game.region_info_zone.open(alberta)
                        game.rc_yes.validate()
                        qs_zone.close()
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
                        game.draw_pile.append(game.selected_region)
                        alaska = game.regions_list[0]
                        game.draw_pile.remove(alaska)
                        game.region_info_zone.open(alaska)
                        game.rc_yes.validate()
                        game.flag_btns[3].validate()
                        game.draw_pile.append(game.selected_region)
                        groenland = game.regions_list[5]
                        game.draw_pile.remove(groenland)
                        game.region_info_zone.open(groenland)
                        game.rc_yes.validate()
                        game.flag_btns[4].validate()
                        game.draw_pile.append(game.selected_region)
                        western = game.regions_list[6]
                        game.draw_pile.remove(western)
                        game.region_info_zone.open(western)
                        game.rc_yes.validate()
                        qs_zone.close()
            PE_Button(qs_zone, text="2", translatable=False, command=quick_setup2)
            def quick_setup3():
                with bp.paint_lock:
                    if game.step.id == 0:
                        game.set_step(1)
                    if game.step.id == 1:
                        game.nb_players = 2
                        game.set_step(10)
                    if game.step.id == 10:

                        qs_zone.close()

                        alaska = game.regions_list[0]
                        alberta = game.regions_list[2]

                        game.flag_btns[4].validate()  # gray
                        game.draw_pile.append(game.selected_region)
                        game.draw_pile.remove(alaska)
                        game.region_info_zone.open(alaska)
                        game.rc_yes.validate()
                        game.flag_btns[5].validate()  # purple
                        game.draw_pile.append(game.selected_region)
                        game.draw_pile.remove(alberta)
                        game.region_info_zone.open(alberta)
                        game.rc_yes.validate()

                        game.region_info_zone.open(alaska)
                        game.region_info_zone.choose_build_zone.camp_btn.validate()
                        game.next_player()

                        game.next_player()

                        game.next_step()
                        game.start_transfer(alaska)
                        game.start_transfer(alaska)
                        game.start_transfer(alaska)
                        game.start_transfer(alaska)
                        game.end_transfer(alberta)

            PE_Button(qs_zone, text="3", translatable=False, command=quick_setup3)
            def quick_setup4():
                with bp.paint_lock:
                    if game.step.id == 0:
                        game.set_step(1)
                    if game.step.id == 1:
                        game.nb_players = 6
                        game.set_step(10)
                    if game.step.id == 10:
                        game.flag_btns[0].validate()
                        game.rc_yes.validate()
                        game.flag_btns[1].validate()
                        game.rc_yes.validate()
                        game.flag_btns[2].validate()
                        game.rc_yes.validate()
                        game.flag_btns[3].validate()
                        game.rc_yes.validate()
                        game.flag_btns[4].validate()
                        game.rc_yes.validate()
                        game.flag_btns[5].validate()
                        game.rc_yes.validate()
                        qs_zone.close()
            PE_Button(qs_zone, text="4", translatable=False, command=quick_setup4)
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

                if event.button == 3:  # right click

                    def delete():
                        dict_path = f"{os.path.abspath(os.path.dirname(sys.argv[0]))}{os.sep}lang{os.sep}" \
                                    f"dict_{btn.lang_id}.py"
                        assert os.path.exists(dict_path), f"Where is the dict file for {btn.lang_id} ?"
                        os.remove(dict_path)
                        dicts.pop(btn.lang_id)
                        btn.kill()
                        self.pack_and_adapt()

                    custom_btn = (14, delete)
                    self.scene.right_click_zone.open(mode=RightClickZone.CUSTOM_MODE, custom_btns=(custom_btn,))

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


class WinnerInfoZone(bp.Zone, bp.LinkableByMouse):

    def __init__(self, game):

        bp.Zone.__init__(self, game, size=game.map.rect.size, sticky="center", visible=False, layer=game.gameinfo_layer)
        bp.LinkableByMouse.__init__(self, game)

        self.sail = bp.Rectangle(self, size=self.rect.size, color=(0, 0, 0, 63))
        self.panel = bp.Zone(self, size=(640, 400), sticky="center", border_width=2, border_color="black")
        self.title = PartiallyTranslatableText(self.panel, text_id=23, get_args=(lambda : game.current_player.name_id,),
                                               font_height=self.get_style_for(bp.Text)["font_height"] + 15,
                                               pos=(0, 5), sticky="midtop")
        rw2 = bp.Rectangle(self.panel, size=(640, self.title.rect.h + 10),
                           color=(0, 0, 0, 0), border_width=2, border_color="black")  # border
        self.subtitle = TranslatableText(self.panel, text_id=6, max_width=self.panel.rect.w - 14, pos=(7, 5),
                                         ref=rw2, refloc="bottomleft")
        PE_Button(self.panel, text_id=24, sticky="midbottom", pos=(0, -5), command=self.panel.hide)
        self.panel.signal.HIDE.connect(self.sail.hide, owner=self.sail)

    def handle_link_motion(self, rel):

        self.scene.handle_link_motion(rel)

    def handle_mousebuttondown(self, event):

        if event.button == 3:  # right click

            with bp.paint_lock:

                # def recenter():
                #     self.scene.map.map_image.pos_manager.config(pos=(0, 0))

                # rightclick_zone = RightClickZone(self.scene, event)
                # rightclick_zone.add_btn(btn_text_id=93, btn_command=recenter)

                # self.scene.right_click_zone.reset()
                # self.scene.right_click_zone.add_btn(btn_text_id=93, btn_command=recenter)
                self.scene.right_click_zone.open(mode=RightClickZone.INGAME_MODE)
