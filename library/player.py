
import baopig as bp

load = bp.image.load
from baopig.googletrans import dicts, lang_manager, TranslatableText
from library.images import FLAGS, SOLDIERS
from library.region import Structure, Boat, Region
from library.zones import BackgroundedZone


class Flag(bp.Image, bp.LinkableByMouse):

    def __init__(self, player):

        bp.Image.__init__(self, player.game.map, image=FLAGS[player.continent], name=str(player.id),
                          touchable=False, visible=False, ref=player.game.map.map_image)
        bp.LinkableByMouse.__init__(self, self.parent)

        self.region = None
        self.game = player.game
        self.player = player

        scale = 1.1
        self.center = None
        self.hover = bp.transform.smoothscale(self.surface, size=bp.Vector2(self.rect.size) * scale)

    def handle_hover(self):

        self.center = self.rect.center
        self.set_surface(self.hover)
        self.set_pos(center=self.center)

    def handle_unhover(self):

        self.set_surface(FLAGS[self.player.continent])
        self.set_pos(center=self.center)
        self.center = None

    def handle_mousebuttondown(self, event):

        if event.button == 3:  # right click
            self.hide()
            self.game.transfer.add_flag()

    def set_region(self, region):

        if self.region is not None:
            self.region.flag = None
        self.region = region
        region.flag = self

        self.set_pos(midbottom=region.flag_midbottom + bp.Vector2(self.parent.map_image.rect.topleft))
        self.show()


class Player(bp.Communicative):

    NAMES = {
        "north_america": 39,  # Jaune
        "europa": 40,         # Bleu
        "asia": 41,           # Vert
        "oceania": 42,        # Violet
        "africa": 43,         # Gris
        "south_america": 44,  # Rouge
    }
    COLORS = {
        "north_america": (242, 219, 0),  # Jaune
        "europa": (0, 82, 255),          # Bleu
        "asia": (0, 201, 0),             # Vert
        "south_america": (243, 0, 0),    # Violet
        "africa": (108, 124, 111),       # Gris
        "oceania": (214, 0, 153),        # Rouge
    }

    def __init__(self, game, continent):

        bp.Communicative.__init__(self)

        self.game = game
        self.is_alive = True
        self.id = len(game.players)
        if self.id in (p.id for p in game.players.values()):
            raise IndexError
        game.players[self.id] = self
        # self.continent = continent.upper().replace("_", " ")
        self.continent = continent
        self.name_id = Player.NAMES[continent]
        self.name = dicts["fr"][self.name_id]
        if lang_manager.ref_language == lang_manager.language:
            self.translated_name = self.name
        else:
            self.translated_name = lang_manager.get_text_from_id(self.name_id)

        self.color = Player.COLORS[continent]
        self.soldier_icon = SOLDIERS[continent]
        self.flag = Flag(self)
        self.choose_region_attemps = 0

        self.gold = game.START_GOLD
        self.regions = {}  # ex: {Region("alaska"): (Soldier1, Soldier2, Soldier3)}
        self.neighboring_regions = set()
        self.cards = [None] * self.game.CARDS_PER_HAND
        self.boats = []

        z = BackgroundedZone(game.info_right_zone, size=("100%", 104), pos=(0, 1000))
        colored_rect = bp.Rectangle(z, size=(z.rect.w, 42), color=self.color, border_width=2, border_color="black")
        TranslatableText(z, text_id=self.name_id, ref=colored_rect, sticky="center")
        self.gold_tracker = bp.Text(z, str(self.gold), pos=(10, 50))
        bp.Image(z, Structure.MINE, ref=self.gold_tracker, pos=(-4, -8), refloc="topright")
        self.soldiers_title = bp.Text(z, "0", pos=(10, 75))
        bp.Image(z, self.soldier_icon, ref=self.soldiers_title, pos=(4, -4), refloc="topright",
                 name="soldier")
        game.info_right_zone.pack()
        game.info_right_zone.adapt()

        self.create_signal("CHANGE_GOLD")

    nb_soldiers = property(lambda self:
                               sum(len(s_list) for s_list in self.regions.values()) +
                               sum(boat.nb_soldiers for boat in self.boats) +
                               (self.game.transfer.amount if self.game.current_player is self else 0)
                           )

    def _update_neighboring_regions(self):

        self.neighboring_regions = set()
        for region in self.regions:
            for neighbour_name in region.neighbors:
                neighbour = self.game.regions[neighbour_name]
                if neighbour not in self.regions:
                    self.neighboring_regions.add(neighbour)

    def can_attack(self):

        for region, soldiers in self.regions.items():
            if len(soldiers) > 1:
                for neighbour_name in region.neighbors:
                    neighbour = self.game.regions[neighbour_name]
                    if neighbour.owner != region.owner:
                        return True  # can attack with a soldiers transfer

        if self.boats:
            for region in self.cards:
                if region is None:
                    if self.gold >= self.game.CARD_PRICE:
                        return True  # can buy a card and then attack with a boat
                    continue
                if region.owner != self:
                    return True  # can attack with a boat

        return False

    def can_build(self):
        """ Return True if, after selling all its cards, a player has enough gold to build """

        num_cards = self.game.CARDS_PER_HAND - self.cards.count(None)
        return self.gold + num_cards * self.game.CARD_SELL_PRICE >= self.game.BUILD_PRICE

    def can_move_troops(self):

        for region, soldiers in self.regions.items():
            if len(soldiers) > 1:
                if len(region.all_allied_neighbors) > 1:
                    return True
                for boat in region.boats:
                    if boat.nb_soldiers == 0:
                        return True
        for boat in self.boats:
            if boat.nb_soldiers > 0:
                if boat.region.owner is boat.owner:
                    return True
        return False

    def can_play(self):

        for region in self.regions:
            if region.structure.name == "CAMP":
                return True
        return self.can_build() or self.can_attack() or self.can_move_troops()

    def change_gold(self, delta):

        self.gold += delta
        assert self.gold >= 0
        self.gold_tracker.set_text(str(self.gold))

        if self.game.step.id == 20 and not self.can_build():
            self.game.set_step(21)

        self.signal.CHANGE_GOLD.emit()

    def check_movement(self):

        can_move = False
        for region, soldiers in self.regions.items():
            if len(soldiers) > 1 and len(region.all_allied_neighbors) > 1:
                can_move = True
                break
        if can_move is False:
            self.game.next_step()

    def conquer(self, region):

        if isinstance(region, Region):
            if region.flag is not None:
                flag_owner = self.game.players[int(region.flag.name)]
                if flag_owner is not self:  # else, the player conquers an empty region where he left his flag
                    flag_owner.die(attacker=self)

            elif region.owner is not None:
                region.owner.unconquer(region)

            self.regions[region] = []
            self._update_neighboring_regions()
            region.owner = self

            region.update_all_allied_neighbors(set())

        else:
            assert isinstance(region, Boat)

    def die(self, attacker):

        attacker.change_gold( + self.gold)
        self.change_gold( - self.gold)

        for region in tuple(self.regions):
            region.rem_soldiers(region.nb_soldiers)
        for boat in tuple(self.boats):
            boat.rem_soldiers(boat.nb_soldiers)
        self.update_soldiers_title()
        self.flag.region.flag = None
        self.flag.hide()
        for card in self.cards:
            if card is not None:
                self.game.discard_pile.append(card)
        self.cards = [None] * self.game.CARDS_PER_HAND
        self.is_alive = False

        # check for game end
        alive_players = 0
        for p in self.game.players.values():
            if p.is_alive:
                alive_players += 1
        if alive_players == 0:
            raise AssertionError
        if alive_players == 1:
            assert attacker.is_alive

            self.game.set_winner(attacker)

    def unconquer(self, region):

        s_list = self.regions.pop(region)
        assert not s_list, "A region must be empty before it is unconquered"
        self._update_neighboring_regions()
        old_owner, region.owner = region.owner, None
        region.all_allied_neighbors = {region.name}

        for neighbour_name in region.neighbors:
            neighbour = self.game.regions[neighbour_name]
            if neighbour.owner is old_owner:
                neighbour.update_all_allied_neighbors(set())

    def update_soldiers_title(self):

        return self.soldiers_title.set_text(str(self.nb_soldiers))

        # nb_soldiers = sum(len(s_list) for s_list in self.regions.values())
        # nb_soldiers += sum(boat.nb_soldiers for boat in self.boats)
        # if self.game.current_player is self:
        #     nb_soldiers += self.game.transfer.amount
        # self.soldiers_title.set_text(str(nb_soldiers))
