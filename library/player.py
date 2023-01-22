
import baopig as bp
load = bp.image.load
from baopig.googletrans import dicts, lang_manager, TranslatableText
from library.images import SOLDIERS
from library.region import Structure, Boat, Region
from library.zones import BackgroundedZone


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
    f = load("images/flags.png")
    w, h = f.get_size()
    w = w / 3
    h = h / 2
    FLAGS = {
        "north_america": f.subsurface(0, 0, w, h),
        "europa": f.subsurface(w, 0, w, h),
        "asia": f.subsurface( 2 *w, 0, w, h),
        "south_america": f.subsurface(0, h, w, h),
        "africa": f.subsurface(w, h, w, h),
        "oceania": f.subsurface( 2 *w, h, w, h),
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
        self.flag = bp.Image(game.map, Player.FLAGS[continent], name=str(self.id), touchable=False,
                             visible=False, ref=game.map.map_image)
        self.flag_region = None
        self.choose_region_attemps = 0

        self.gold = 6
        self.regions = {}  # ex: {Region("alaska"): (Soldier1, Soldier2, Soldier3)}
        self.neighboring_regions = set()
        self.cards = [None] * 3
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

    def _update_neighboring_regions(self):

        self.neighboring_regions = set()
        for region in self.regions:
            for neighbour_name in region.neighbors:
                neighbour = self.game.regions[neighbour_name]
                if neighbour not in self.regions:
                    self.neighboring_regions.add(neighbour)

    def can_attack(self):

        can_attack = False
        for region, soldiers in self.regions.items():
            if len(soldiers) > 1:
                for neighbour_name in region.neighbors:
                    neighbour = self.game.regions[neighbour_name]
                    if neighbour.owner != region.owner:
                        can_attack = True
                        break
                if can_attack:
                    break
        return can_attack

    def can_build(self):
        """ Return True if, after selling all its cards, a player has at least 3 gold """

        num_cards = 3 - self.cards.count(None)
        return self.gold + num_cards * 2 >= 3

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
                gold_earned = flag_owner.gold
                self.change_gold(+gold_earned)
                flag_owner.change_gold(-gold_earned)
                if flag_owner is not self:  # else, the player conquers an empty region where he left his flag
                    flag_owner.die()

                alive_players = 0
                for p in self.game.players.values():
                    if p.is_alive:
                        alive_players += 1
                if alive_players == 0:
                    raise AssertionError
                if alive_players == 1:
                    assert self.is_alive

                    self.game.set_winner(self)

            elif region.owner is not None:
                region.owner.unconquer(region)

            self.regions[region] = []
            self._update_neighboring_regions()
            region.owner = self

            region.update_all_allied_neighbors(set())

        else:
            assert isinstance(region, Boat)
            boat = region

            self.boats.append(boat)
            boat.owner = self

    def die(self):

        for region in tuple(self.regions):
            region.rem_soldiers(region.nb_soldiers)
        for boat in tuple(self.boats):
            boat.rem_soldiers(boat.nb_soldiers)
        self.flag_region.flag = None
        self.flag.hide()
        for card in self.cards:
            if card is not None:
                self.game.discard_pile.append(card)
        if not self.game.draw_pile:
            self.game.draw_pile.merge_with_discard_pile()
            self.game.draw_pile.shuffle()
        self.cards = [None] * 3
        self.is_alive = False

    def move_flag(self, region):

        if self.flag_region is not None:
            self.flag_region.flag = None
        self.flag_region = region
        region.flag = self.flag

    def unconquer(self, region):

        s_list = self.regions.pop(region)
        assert not s_list, "A region must be empty before it is unconquered"
        self._update_neighboring_regions()
        old_owner, region.owner = region.owner, None
        region.all_allied_neighbors = {region}

        for neighbour_name in region.neighbors:
            neighbour = self.game.regions[neighbour_name]
            if neighbour.owner is old_owner:
                neighbour.update_all_allied_neighbors(set())

    def update_soldiers_title(self):

        nb_soldiers = sum(len(s_list) for s_list in self.regions.values())
        nb_soldiers += sum(boat.nb_soldiers for boat in self.boats)
        if self.game.current_player is self:
            nb_soldiers += self.game.transfert_amount
        self.soldiers_title.set_text(str(nb_soldiers))
