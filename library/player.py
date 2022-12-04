
import baopig as bp
load = bp.image.load
from language import dicts, lang_manager, TranslatableText
from .region import Region
from .zones import BackgroundedZone


class Player:

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
    s = load("images/soldiers.png")
    w, h = s.get_size()
    w = w / 3
    h = h / 2
    SOLDIERS = {
        "north_america": s.subsurface(0, 0, w, h),
        "europa": s.subsurface(w, 0, w, h),
        "asia": s.subsurface( 2 *w, 0, w, h),
        "south_america": s.subsurface(0, h, w, h),
        "africa": s.subsurface(w, h, w, h),
        "oceania": s.subsurface( 2 *w, h, w, h),
        # "black": load("images/builds.png").subsurface(38, 38, 14, 14)
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
    f_big = load("images/flags_big.png")
    w, h = f_big.get_size()
    w = w / 3
    h = h / 2
    FLAGS_BIG = {
        "north_america": f_big.subsurface(0, 0, w, h),
        "europa": f_big.subsurface(w, 0, w, h),
        "asia": f_big.subsurface( 2 *w, 0, w, h),
        "south_america": f_big.subsurface(0, h, w, h),
        "africa": f_big.subsurface(w, h, w, h),
        "oceania": f_big.subsurface( 2 *w, h, w, h),
    }

    def __init__(self, game, continent):

        self.game = game
        self.is_alive = True
        self.id = len(game.players)
        if self.id in (p.id for p in game.players.values()):
            raise IndexError
        game.players[self.id] = self
        self.continent = continent.upper().replace("_", " ")
        self.name_id = Player.NAMES[continent]
        self.name = dicts.get(self.name_id, "fr")
        if lang_manager.ref_language == lang_manager.language:
            self.translated_name = self.name
        else:
            # self.translated_name = translator.translate(self.name, src=lang_manager.ref_language,
            #                                             dest=lang_manager.language)
            self.translated_name = dicts.get(self.name_id, lang_manager.language)
            # self.translated_name = dicts[lang_manager.language][self.name_id]

        self.color = Player.COLORS[continent]
        self.soldier_icon = Player.SOLDIERS[continent]
        self.flag = bp.Image(game.map, Player.FLAGS[continent], name=str(self.id),
                             visible=False, layer=game.map.frontof_regions_layer)
        self.flag_region = None
        self.choose_region_attemps = 0

        self.gold = 6
        self.regions = {}  # ex: {Region("alaska"): (Soldier1, Soldier2, Soldier3)}
        self.neighboring_regions = set()

        z = BackgroundedZone(game.info_right_zone, size=("100%", 104), pos=(0, 1000))
        colored_rect = bp.Rectangle(z, size=(z.rect.w, 42), color=self.color, border_width=2, border_color="black")
        TranslatableText(z, text_id=self.name_id, ref=colored_rect, sticky="center")
        self.gold_tracker = bp.Text(z, str(self.gold), pos=(10, 50))
        bp.Image(z, Region.MINE, ref=self.gold_tracker, pos=(-4, -8), refloc="topright")
        self.soldiers_title = bp.Text(z, "0", pos=(10, 75))
        bp.Image(z, self.soldier_icon, ref=self.soldiers_title, pos=(4, -4), refloc="topright",
                 name="soldier")
        game.info_right_zone.pack()
        game.info_right_zone.adapt()

    def _update_neighboring_regions(self):

        self.neighboring_regions = set()
        for region in self.regions:
            for neighbour_name in region.neighbors:
                neighbour = self.game.regions[neighbour_name]
                if neighbour not in self.regions:
                    self.neighboring_regions.add(neighbour)

    def build_stuff(self):

        for region in self.regions:
            if region.build_state == "construction":
                region.end_construction()
            else:
                region.build_circle.show()
            region.produce()

        self.check_build()

    def change_gold(self, delta):

        self.gold += delta
        assert self.gold >= 0
        self.gold_tracker.set_text(str(self.gold))

    def check_attack(self):

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
        if can_attack is False:
            self.game.set_todo(22)

    def check_build(self):

        has_fully_built = self.has_fully_built()
        if has_fully_built or self.gold < 3:

            # self.game.TmpMessage(self.game, msg="Fin de l'étape : CONSTRUCTION", explain="Tous vos pays possèdent déjà "
            #     "un bâtiment" if has_fully_built else "Vous n'avez pas assez d'or (il en faut 3 au minimum)")
            self.game.set_todo(21)

    def check_movement(self):

        can_attack = False
        for region, soldiers in self.regions.items():
            if len(soldiers) > 1 and len(region.all_allied_neighbors) > 1:
                can_attack = True
                break
        if can_attack is False:
            self.game.next_todo.validate()

    def conquer(self, region):

        if region.flag is not None:
            flag_owner = self.game.players[int(region.flag.name)]
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

                self.game.time_left.pause()
                self.game.map.region_unselect()
                self.game.winner_info_zone.title.complete_text()
                self.game.winner_info_zone.panel.set_color(self.color)
                self.game.winner_info_zone.show()
                self.game.newgame_btn.enable()
                if self.game.tutoring:
                    self.game.set_tuto_ref_text_id(45)

        elif region.owner is not None:
            region.owner.unconquer(region)

        self.regions[region] = []
        self._update_neighboring_regions()
        region.owner = self

        region.update_all_allied_neighbors(set())

    def die(self):

        for region in tuple(self.regions):
            region.rem_soldiers(region.soldiers_amount)
        self.flag_region.flag = None
        self.flag.hide()
        self.is_alive = False

    def has_fully_built(self):

        for r in self.regions:
            if r.build_state == "empty":
                return False
        return True

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

        soldiers_amount = sum(len(s_list) for s_list in self.regions.values())
        if self.game.current_player is self:
            soldiers_amount += self.game.transfert_amount
        self.soldiers_title.set_text(str(soldiers_amount))
