
import os
os.chdir(os.path.dirname(os.path.realpath(__file__)))
import random
import baopig as bp

# NOTE for v.1.5 : jouer en réseau
# NOTE for v.2 : entrer son nom de joueur
# NOTE for v.2 : un bâtiment avantageant les pays avec beaucoup de frontières
# NOTE for v.2 : des stratégies différentes, comme au 7 wonders
# NOTE for v.2 : des alliances
# NOTE for v.2 : de la musique !!!


class Player:

    NAMES = {
        "north_america": "Jaune",
        "europa": "Bleu",
        "asia": "Vert",
        "oceania": "Violet",
        "africa": "Gris",
        "south_america": "Rouge",
    }
    COLORS = {
        "north_america": (242, 219, 0),
        "europa": (0, 82, 255),
        "asia": (0, 201, 0),
        "oceania": (214, 0, 153),
        "africa": (108, 124, 111),
        "south_america": (243, 0, 0),
    }
    s = bp.load("images/soldiers.png")
    SOLDIERS = {
        "north_america": s.subsurface(0, 0, 14, 14),
        "europa": s.subsurface(14, 0, 14, 14),
        "asia": s.subsurface(28, 0, 14, 14),
        "south_america": s.subsurface(0, 14, 14, 14),
        "africa": s.subsurface(14, 14, 14, 14),
        "oceania": s.subsurface(28, 14, 14, 14),
        # "black": bp.load("images/builds.png").subsurface(38, 38, 14, 14)
    }
    f = bp.load("images/flags.png")
    FLAGS = {
        "north_america": f.subsurface(0, 0, 36, 60),
        "europa": f.subsurface(36, 0, 36, 60),
        "asia": f.subsurface(72, 0, 36, 60),
        "south_america": f.subsurface(0, 60, 36, 60),
        "africa": f.subsurface(36, 60, 36, 60),
        "oceania": f.subsurface(72, 60, 36, 60),
    }

    def __init__(self, game, continent):

        self.game = game
        self.is_alive = True
        self.id = len(game.players)
        if self.id in (p.id for p in game.players.values()):
            raise IndexError
        game.players[self.id] = self
        self.continent = continent.upper().replace("_", " ")
        self.name = Player.NAMES[continent]
        self.color = Player.COLORS[continent]
        self.soldier_icon = Player.SOLDIERS[continent]
        self.flag = bp.Image(game.map, Player.FLAGS[continent], name=str(self.id),
                             visible=False, touchable=False, layer=game.map.frontof_regions_layer)
        self.flag_region = None

        self.gold = 6
        self.regions = {}  # {Region("alaska"): (Soldier1, Soldier2, Soldier3)}
        self.neighboring_regions = set()

        z = bp.Zone(game.info_right_zone, size=("100%", 100), pos=(0, 97 * len(game.info_right_zone.children)))
        bp.Rectangle(z, size=z.size)
        bp.Rectangle(z, size=(z.w, 32), color=self.color)
        bp.Text(z, self.continent, pos=("50%", 10), pos_location="midtop")
        g = bp.DynamicText(z, lambda: str(self.gold), pos=(10, 40))
        bp.Image(z, Region.MINE, pos_ref=g, pos=(-4, -8), pos_ref_location="topright")
        self.soldiers_title = bp.Text(z, "0", pos=(10, 65))
        bp.Image(z, self.soldier_icon, pos_ref=self.soldiers_title, pos=(4, -2), pos_ref_location="topright",
                 name="soldier")

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
            self.game.set_todo(5)

    def check_build(self):
        
        has_fully_built = self.has_fully_built()
        if has_fully_built or self.gold < 3:

            # self.game.TmpMessage(self.game, msg="Fin de l'étape : CONSTRUCTION", explain="Tous vos pays possèdent déjà "
            #     "un bâtiment" if has_fully_built else "Vous n'avez pas assez d'or (il en faut 3 au minimum)")
            self.game.set_todo(4)

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
                self.game.info_winner_title.set_text(self.continent + " a gagné !")
                self.game.info_winner_panel.set_color(self.color)
                self.game.info_winner_zone.show()
                self.game.newgame_btn.enable()
                self.game.tuto_zone.hide()

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


class Game(bp.Scene):

    class TmpMessage(bp.Zone, bp.Clickable):

        def __init__(self, game, msg, explain):

            bp.Zone.__init__(self, game, size=("25%", "25%"), pos=game.settings_btn.bottomleft)
            bp.Clickable.__init__(self)

            r = bp.Rectangle(self, size=self.size)
            msg_w = bp.Text(self, msg, max_width=r.w - 10, font_height=self.get_style_for(bp.Text)["font_height"] + 7,
                            align_mode="center", pos=(5, 5))
            r2 = bp.Rectangle(self, size=(r.w, msg_w.h + 10), color=(0, 0, 0, 0))
            bp.Text(self, explain, max_width=r.w - 10, pos=(5, 5), pos_ref=r2, pos_ref_location="bottomleft")

            self.timer = bp.Timer(3, command=self.kill)
            self.timer.start()

        def handle_link(self):

            self.timer.cancel()
            self.kill()

    def __init__(self, app):

        bp.Scene.__init__(self, app, background_color=(96, 163, 150))

        self.players = {}
        self.regions = {}
        self.flags = []
        self.current_player_id = 0
        self.turn_index = 0  # 0 is the setup, 1 is the first turn
        self.last_selected_region = None

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
        self.next_sail = bp.Zone(map, pos=(-map.h, 0), size=(map.h, "100%"), layer_level=2)
        def nextsail_animate():
            self.next_sail.move(dx=max(abs(self.next_sail.centerx - map.auto.centerx) / 5, 20))
            if self.next_sail.left >= self.map.width:
                self.nextsail_animator.cancel()
        self.nextsail_animator = bp.RepeatingTimer(.04, nextsail_animate)
        bp.Circle(self.next_sail, (0, 0, 0, 63), center=("50%", "50%"), radius=map.auto.centery)
        nextsail_text = bp.Text(self.next_sail, "HELLO !!", font_height=50, color="orange", bold=True,
                                sticky="center", pos_ref=map)

        # PARAMETERS
        param_zone = bp.Zone(self, size=(160, 211), visible=False, layer_level=2)
        bp.Rectangle(param_zone, size=("100%", "100%"), layer_level=0)
        bp.GridLayer(param_zone, nbcols=1, col_width=param_zone.width, row_height=70)
        bp.Button(parent=param_zone, text="Hide", row=0, sticky="center", command=param_zone.hide)
        self.newgame_btn = bp.Button(parent=param_zone, text="New game", row=1, sticky="center")
        self.newgame_btn.disable()
        self.newgame_btn.command = lambda: param_zone.hide() or self.set_todo(0) or self.newgame_btn.disable()
        bp.Button(parent=param_zone, text="Quit", row=2, sticky="center", command=app.exit)
        self.settings_btn = bp.Button(self, text="=", command=param_zone.show, width=35, text_style={"font_height": 40})

        # INFORMATION ON TOP & RIGHT
        self.info_right_zone = bp.Zone(self, sticky="topright", size=("10%", "100%"))
        self.info_top_zone = bp.Zone(self, sticky="midtop", size=("80%", "5%"), visible=False)
        self.au_tour_de = bp.Text(self.info_top_zone, "", sticky="center")
        def next_todo_command():
            if self.todo.id == 5:
                self.next_player()
                self.set_todo(3)
            else:
                self.set_todo(self.todo.id + 1)
        self.next_todo = bp.Button(self.info_top_zone, "Next  ->", pos=(-3, 3), pos_location="topright",
                                   pos_ref_location="topright", visible=False, command=next_todo_command)

        # INFORMATION AT LEFT
        self.info_left_zone = bp.Zone(self, sticky="midleft", size=("10%", "50%"), visible=False)
        gl = bp.GridLayer(self.info_left_zone, nbcols=1, nbrows=4, col_width=self.info_left_zone.w)
        self.time_left = bp.Timer(90, lambda: self.next_player() or self.set_todo(3))
        z0 = bp.Zone(self.info_left_zone, size=("100%", "10%"), row=0)
        bp.Rectangle(z0, size=("100%", "100%"), color=theme.colors.border)
        t0 = bp.DynamicText(z0, lambda: bp.format_time(self.time_left.get_time_left(), formatter="%M:%S"),
                            sticky="center", align_mode="center")
        z1 = bp.Zone(self.info_left_zone, size=("100%", "30%"), row=1)
        re1 = bp.Rectangle(z1, size=("100%", "100%"))
        t1 = bp.Text(z1, "CONSTRUCTION", sticky="center", align_mode="center")
        z2 = bp.Zone(self.info_left_zone, size=("100%", "30%"), row=2)
        re2 = bp.Rectangle(z2, size=("100%", "100%"))
        t2 = bp.Text(z2, "ATTAQUE", sticky="center", align_mode="center")
        z3 = bp.Zone(self.info_left_zone, size=("100%", "30%"), row=3)
        re3 = bp.Rectangle(z3, size=("100%", "100%"))
        t3 = bp.Text(z3, "REORGANISATION", sticky="center", align_mode="center")
        def update_gridlayer():
            gl.set_col_width(self.info_left_zone.w)
            for t in t0, t1, t2, t3:
                try:
                    t.set_max_width(gl.col_width - 10)
                except PermissionError:
                    pass
        self.info_left_zone.signal.RESIZE.connect(update_gridlayer)

        # INFO COUNTRY
        self.info_country_on_hover = False
        self.info_country_zone = bp.Zone(self, size=(150, 150), visible=False)
        r = bp.Rectangle(self.info_country_zone, size=self.info_country_zone.size)
        r2 = bp.Rectangle(self.info_country_zone, size=(r.w, 40), color=(0, 0, 0, 0))
        self.invade_btn = bp.Button(self.info_country_zone, "ENVAHIR", pos=(75, 145), pos_location="midbottom",
                                    width=140, command=self.end_transfert)
        self.back_btn = bp.Button(self.info_country_zone, "RENTRER", pos=(75, 145), pos_location="midbottom",
                                  width=140, command=self.end_transfert)
        self.import_btn = bp.Button(self.info_country_zone, "IMPORTER", pos=(75, 145), pos_location="midbottom",
                                    width=140, command=self.end_transfert)
        info_country_title = bp.Text(self.info_country_zone, "", align_mode="center", sticky="center", pos_ref=r2,
                                     max_width=self.info_country_zone.w - 10)
        self.info_csa = bp.Text(self.info_country_zone, "", pos=(5, r2.bottom + 5))
        self.info_csi = bp.Image(self.info_country_zone, Player.SOLDIERS["asia"],
                                 pos_ref=self.info_csa, pos=(4, -2), pos_ref_location="topright")
        def handle_infocountry_change(region=None):
            region = self.map.selected_region if region is None else region

            self.info_country_zone.move_at((region.abs.right + 5, region.abs.centery), key="midleft")
            info_country_title.set_text(region.name.upper().replace("_", " "))
            if region.owner is None:
                self.info_csi.hide()
                self.info_csa.hide()
            else:
                self.info_csi.show()
                self.info_csa.show()
                self.info_csi.set_surface(region.owner.soldier_icon)
                self.info_csa.set_text(str(region.soldiers_amount))
            self.info_country_zone.show()

            self.invade_btn.hide()
            self.back_btn.hide()
            self.import_btn.hide()
            if self.todo.text == "attack" and self.transferring:
                if region.name in self.transfert_from.neighbors and region.owner != self.transfert_from.owner:
                    self.invade_btn.show()
                elif region is self.transfert_from:
                    self.back_btn.show()
            elif self.todo.text == "troops movement" and self.transferring:
                if region is self.transfert_from:
                    self.back_btn.show()
                elif region in self.transfert_from.all_allied_neighbors:
                    self.import_btn.show()
        self.handle_infocountry_change = handle_infocountry_change
        self.map.signal.REGION_SELECT.connect(handle_infocountry_change)

        # WINNER INFO
        self.info_winner_zone = bp.Zone(self, size=map.size, background_color=(0, 0, 0, 63), sticky="center",
                                        visible=False)
        self.info_winner_panel = rw1 = bp.Rectangle(self.info_winner_zone, size=("40%", "40%"), sticky="center")
        self.info_winner_title = bp.Text(self.info_winner_zone, "ASIA a gagné !", max_width=rw1.w - 10,
                                         font_height=self.info_winner_zone.get_style_for(bp.Text)["font_height"] + 15,
                                         align_mode="center", pos=(rw1.left + 5, rw1.top + 5))
        rw2 = bp.Rectangle(self.info_winner_zone, size=(rw1.w, self.info_winner_title.h + 10), pos=rw1.pos,
                           color=(0, 0, 0, 0))
        self.info_winner_subtitle = bp.Text(self.info_winner_zone, "Bravo à tous, bel effort.", max_width=rw1.w - 10,
                                            pos=(5, 5), pos_ref=rw2, pos_ref_location="bottomleft")
        def ok():
            self.info_winner_zone.hide()
        bp.Button(self.info_winner_zone, "OK", pos=(rw1.centerx, rw1.bottom - 5), pos_location="bottom", command=ok)

        # FLAG CHOOSE
        self.choose_color_zone = bp.Zone(self, size=("50%", 468), sticky="center", visible=False)
        r2 = bp.Rectangle(self.choose_color_zone, size=("100%", 50), color="black")
        r = bp.Rectangle(self.choose_color_zone, size=("100%", self.choose_color_zone.h - r2.h + 3), sticky="bottom")
        done = bp.Button(self.choose_color_zone, "No more player", command=self.next_turn, width=150, visible=False,
                         pos=(-5, -5), pos_ref=r, pos_ref_location="bottomright", pos_location="bottomright")
        bp.Text(self.choose_color_zone, "Choisis ton peuple", pos=r2.center, pos_location="center", font_height=30,
                color=theme.colors.border)
        class ClickableFlag(bp.Button):
            def __init__(btn, continent, pos):
                bp.Button.__init__(btn, self.choose_color_zone, background_color="gray",
                                   size=(36*3, 60*3), pos=pos, pos_location="center")
                btn.continent = continent
                btn.flag = bp.Image(btn, Player.FLAGS[continent], sticky="center")
            def validate(btn, *args, **kwargs):
                Player(self, btn.continent)
                self.next_player()
                self.flags.append(self.current_player.flag)
                self.set_todo(2)
                btn.disable()
                if len(self.players) > 1:
                    done.show()
        ClickableFlag("north_america", pos=(r.centerx - 36*3 - 20, r.centery - 60*1.5 - 10))
        ClickableFlag("europa", pos=(r.centerx, r.centery - 60*1.5 - 10))
        ClickableFlag("asia", pos=(r.centerx + 36*3 + 20, r.centery - 60*1.5 - 10))
        ClickableFlag("south_america", pos=(r.centerx - 36*3 - 20, r.centery + 60*1.5 + 10))
        ClickableFlag("africa", pos=(r.centerx, r.centery + 60*1.5 + 10))
        ClickableFlag("oceania", pos=(r.centerx + 36*3 + 20, r.centery + 60*1.5 + 10))

        # TUTORIAL
        self.tuto_zone = hibou_zone = bp.Zone(self, size=(305, 400), sticky="bottomright", visible=False)
        hibou = bp.Image(hibou_zone, bp.load("images/hibou.png"), sticky="bottomright")
        bulle = bp.Image(hibou_zone, bp.load("images/hibou_bulle.png"), pos=hibou.midtop, pos_location="midbottom")
        bulle_text = bp.Text(hibou_zone, "", pos=(bulle.left + 10, bulle.top + 10), max_width=bulle.width - 20,
                             align_mode="center")
        bp.Button(hibou_zone, text="Bye Bye Pony", sticky="bottomright", command=hibou_zone.hide)
        open = bp.Button(self, text="Pony, help !", sticky="bottomright", visible=False, command=hibou_zone.show)
        open.move_behind(hibou_zone)

        # CLICK TO START
        clicktostart = bp.TextLabel(self, "CLICK TO START", bold=True, font_height=80, sticky="center", visible=False,
                                    touchable=False, background_color="white", height=200, width=1100)

        # CONFIRMATION
        self.confirm_zone = bp.Zone(self, size=(42, 76), visible=False)
        bp.Rectangle(self.confirm_zone, size=self.confirm_zone.size)
        bp.Button(self.confirm_zone, size=(30, 30), pos=(6, 6), background_color="green4", focus=-1,
                  background_image=Region.BUILDS.subsurface(0, 60, 30, 30),
                  command=bp.PackedFunctions(lambda: self.todo.confirm(), self.map.region_unselect))
        bp.Button(self.confirm_zone, size=(30, 30), pos=(6, 40), background_color="red4", focus=-1,
                  background_image=Region.BUILDS.subsurface(30, 60, 30, 30),
                  command=self.map.region_unselect)

        # CHOOSE BUILD
        self.choose_build_zone = bp.Zone(self, size=(42, 76), visible=False)
        bp.Rectangle(self.choose_build_zone, size=self.confirm_zone.size)

        def build(build_name):
            self.last_selected_region.start_construction(build_name)
            self.current_player.gold -= 3
            self.current_player.check_build()
            self.map.region_unselect()

        bp.Button(self.choose_build_zone, "", size=(30, 30), pos=(6, 6), background_image=Region.MINE,
                  command=bp.PrefilledFunction(build, "mine"), background_color=(0, 0, 0, 0))
        bp.Button(self.choose_build_zone, "", size=(30, 30), pos=(6, 40), background_image=Region.CAMP,
                  command=bp.PrefilledFunction(build, "camp"), background_color=(0, 0, 0, 0))

        # SOLDIERS TRANSFERT
        self.transfert_from = None
        self.transfert_zone = bp.Zone(self, size=(35, 24), visible=False, touchable=False, padding=4)
        bp.Rectangle(self.transfert_zone, size=("100%", "100%"))
        self.transfert_amount = 0
        self.transfert_title = bp.Text(self.transfert_zone, "", pos=(5, 7))
        self.transfert_icon = bp.Image(self.transfert_zone, Player.SOLDIERS["asia"],
                                       pos_ref=self.transfert_title, pos=(4, -2), pos_ref_location="topright")
        def handle_mouse_motion():
            self.transfert_zone.move_at((bp.mouse.x + 12, bp.mouse.y))
        bp.mouse.signal.MOTION.connect(handle_mouse_motion)

        # TODOS
        class Todo:
            @staticmethod
            def confirm_place_flag():
                flag = self.flags[self.current_player_id]
                flag.swap_layer(map.behind_regions_layer)
                flag.show()
                # self.current_player.regions[self.last_selected_region] = 3  # 3 soldiers in this region
                self.current_player.conquer(self.last_selected_region)
                self.current_player.move_flag(self.last_selected_region)
                self.last_selected_region.add_soldiers(3)
                if len(self.players) == 6:
                    self.next_turn()
                else:
                    self.set_todo(1)

            def __init__(self, id, text="", confirm=None, f_start=(), f_end=()):
                self.id = id
                self.text = text
                self.confirm = confirm
                self.need_confirmation = confirm is not None
                self.f_start = f_start
                self.f_end = f_end

            def start(self):
                for f in self.f_start:
                    f()

            def end(self):
                for f in self.f_end:
                    f()

        self.todo_list = [
            Todo(0, "owl presentation", f_start=(open.show, done.hide, bp.PrefilledFunction(bulle_text.set_text,
                 "Salut !\nMoi c'est Pony la chouette !\nClique quelque part pour commencer !"), self.newgame_setup,
                                                 clicktostart.show), f_end=(clicktostart.hide,)),
            Todo(1, "choose color",
                 f_start=(self.choose_color_zone.show, bp.PrefilledFunction(bulle_text.set_text,
                 "Choisis un peuple, cette étape est facile !"), self.info_top_zone.hide, self.info_right_zone.hide),
                 f_end=(self.choose_color_zone.hide, self.info_top_zone.show, self.info_right_zone.show)),
            Todo(2, "place flag", confirm=Todo.confirm_place_flag, f_start=(bp.PrefilledFunction(bulle_text.set_text,
                 "Clique sur un pays pour y planter ton drapeau !\n"
                 "Pendant la partie, tu devras le protéger à tous prix !"),)),
            Todo(3, "build", f_start=(self.next_todo.show, self.info_left_zone.show,
                 bp.PrefilledFunction(bulle_text.set_text,
                 "Tu peux maintenant construire des bâtiments ! Les mines rapportent 4 kilos d'or par tour "
                 "et les camps rapportent 3 soldats par tour ! Chaque bâtiment te coûte 3 kilos d'or."),
                 bp.PrefilledFunction(re1.set_color, "orange"),
                 bp.PrefilledFunction(nextsail_text.set_text, "CONSTRUCTION"),
                 lambda: self.current_player.build_stuff()),
                 f_end=(lambda: tuple(r.build_circle.hide() for r in self.current_player.regions),
                 bp.PrefilledFunction(re1.set_color, theme.get_style_for(bp.Rectangle)["color"]))),
            Todo(4, "attack", f_start=(bp.PrefilledFunction(bulle_text.set_text,
                 "C'est le moment d'étandre ton territoire ! Utilise le clic droit de ta souris pour prendre des soldats puis clique sur tes pays limitrophes pour les envahir !"),
                 bp.PrefilledFunction(re2.set_color, "orange"),
                 bp.PrefilledFunction(nextsail_text.set_text, "ATTAQUE"),
                 lambda: self.current_player.check_attack()),
                 f_end=(bp.PrefilledFunction(re2.set_color, theme.get_style_for(bp.Rectangle)["color"]),)),
            Todo(5, "troops movement", f_start=(bp.PrefilledFunction(bulle_text.set_text, "Avant de finir ton tour, "
                 "réorganise tes troupes, tu dois être prêt à une attaque de tes adversaires !"),
                 bp.PrefilledFunction(re3.set_color, "orange"),
                 bp.PrefilledFunction(nextsail_text.set_text, "REORGANISATION"),
                 lambda: self.current_player.check_movement()),
                 f_end=(bp.PrefilledFunction(re3.set_color, theme.get_style_for(bp.Rectangle)["color"]),)),
        ]
        self.todo = Todo(-1)
        self.set_todo(0)

        # SETUP
        self.map.signal.REGION_SELECT.connect(self.handle_region_select)
        self.map.signal.REGION_UNSELECT.connect(self.handle_region_unselect)

    current_player = property(lambda self: self.players[self.current_player_id])
    transferring = property(lambda self: self.transfert_from is not None)

    def end_transfert(self, region=None):

        assert self.transferring
        if region is None:
            region = self.map.selected_region

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

        if self.todo.text == "attack" and self.info_winner_zone.is_hidden:
            self.current_player.check_attack()
        elif self.todo.text == "troops movement":
            self.current_player.check_movement()

    def handle_region_select(self, region):

        if self.mapsail_close_animator.is_running:
            self.mapsail_close_animator.cancel()
        if self.mapsail_open_animator.is_running:
            self.mapsail_open_animator.cancel()
        self.map_sail.move_at(region.center, key="center")
        self.map_sail.set_radius(60)
        self.mapsail_open_animator.start()
        self.map_sail.show()

        self.last_selected_region = region

        if self.todo.text == "place flag":
            flag = self.flags[self.current_player_id]
            if region.owner is not None:
                flag.hide()
                self.confirm_zone.hide()
                return
            flag.move_at(region.flag_midbottom, "midbottom")
            flag.show()
            self.confirm_zone.move_at((region.abs.left - 5, region.abs.centery), key="midright")
            self.confirm_zone.show()

        if self.todo.text == "build":
            if region in self.current_player.regions and region.build_state == "empty":
                self.choose_build_zone.move_at((region.abs.left - 5, region.abs.centery), key="midright")
                self.choose_build_zone.show()
            else:
                self.choose_build_zone.hide()

    def handle_region_unselect(self):

        if self.mapsail_open_animator.is_running:
            self.mapsail_open_animator.cancel()
        self.mapsail_close_animator.start()

        self.info_country_zone.hide()
        self.confirm_zone.hide()
        self.choose_build_zone.hide()

        if self.todo.text == "place flag":
            flag = self.flags[self.current_player_id]
            flag.hide()

    def next_player(self):

        if self.turn_index > 0 and self.current_player_id == len(self.players) - 1:
            self.turn_index += 1
        self.current_player_id = (self.current_player_id + 1) % len(self.players)
        if not self.current_player.is_alive:
            return self.next_player()
        self.au_tour_de.set_text(f"AU TOUR DE : {self.current_player.continent}")
        self.info_top_zone.set_background_color(self.current_player.color)

        if self.time_left.is_running:
            self.time_left.cancel()
        if self.todo.id > 2:
            self.time_left.start()

    def next_turn(self):

        self.turn_index += 1
        self.current_player_id = -1
        self.next_player()
        if self.todo.id < 3:
            self.time_left.start()
        self.set_todo(3)
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
        self.info_winner_zone.hide()
        if self.time_left.is_running:
            self.time_left.cancel()

    def receive(self, event):

        # Tutorial first click
        if self.todo.id == 0:
            if event.type == bp.MOUSEBUTTONDOWN:
                if event.button == 1 and self.map.is_hovered:
                    self.set_todo(1)

        # Region sail
        elif self.todo.id > 1:
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
                                self.info_country_zone.show()

                            hoverable = False
                            if self.todo.text == "place flag":
                                if region.owner is None:
                                    hoverable = True
                            if self.todo.text == "build":
                                if region.owner is self.current_player and region.build_state == "empty":
                                    hoverable = True
                            elif self.todo.text == "attack":
                                if self.transferring:
                                    if region is self.transfert_from:
                                        hoverable = True
                                    elif region.name in self.transfert_from.neighbors and \
                                            region.owner != self.transfert_from.owner:
                                        hoverable = True
                                elif region in self.current_player.regions:
                                    hoverable = True
                            if self.todo.text == "troops movement":
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
                        if ctrl_hovered is None and self.info_country_zone.is_visible:
                            self.info_country_zone.hide()
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
                            self.info_country_zone.hide()

            elif event.type == bp.MOUSEBUTTONDOWN and event.button == 3:  # right click
                if self.todo.text in ("attack", "troops movement"):
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

    def set_todo(self, index):

        if self.transferring:
            self.end_transfert(self.transfert_from)

        self.todo.end()
        self.todo = self.todo_list[index]
        if self.map.selected_region is not None:
            self.map.region_unselect()
        self.todo.start()

        if index > 2:
            self.next_sail.right = 0
            if self.nextsail_animator.is_running:
                self.nextsail_animator.cancel()
            self.nextsail_animator.start()

    def transfert(self, region):

        if self.transferring:
            if self.transfert_from is region:
                if region.soldiers_amount < 2:
                    self.back_btn.validate(region)
                else:
                    self.map.region_unselect()
                    amount = region.soldiers_amount - 1 if bp.keyboard.mod.maj else 1
                    self.transfert_amount += amount
                    region.rem_soldiers(amount)
                    self.transfert_title.set_text(str(self.transfert_amount))
                    self.transfert_zone.resize_width(self.transfert_icon.right + self.transfert_zone.padding.right)
            else:
                if self.todo.text == "troops movement":
                    self.import_btn.validate(region)
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
            self.transfert_zone.resize_width(self.transfert_icon.right + self.transfert_zone.padding.right)
            self.transfert_zone.show()


class Map(bp.Zone, bp.Clickable, bp.Hoverable):

    IMAGE = bp.load("images/map.png")

    def __init__(self, parent):

        bp.Zone.__init__(self, parent, size=Map.IMAGE.get_size(), background_image=Map.IMAGE, sticky="center")
        bp.Clickable.__init__(self)
        bp.Hoverable.__init__(self)

        self.selected_region = None
        self.hovered_region = None

        self.behind_regions_layer = bp.Layer(self, weight=0, name="0", default_sortkey=lambda w: (w.bottom, w.centerx))
        self.regions_layer = bp.Layer(self, weight=1, name="1")
        self.frontof_regions_layer = bp.Layer(self, weight=2, name="2", default_sortkey=lambda w: (w.bottom, w.centerx))

        self.create_signal("REGION_SELECT")
        self.create_signal("REGION_UNSELECT")

        self.sail = bp.Circle(self, (0, 0, 0, 63), (0, 0), radius=0, touchable=False, visible=False,
                              layer=self.regions_layer)
        self._create_regions()

    def _create_regions(self):

        # NORTH AMERICA
        Region("alaska", self, center=(133, 103), flag_midbottom=(133, 77),
               neighbors=("territoires_du_nord_ouest", "alberta", "kamchatka"))
        Region("territoires_du_nord_ouest", self, center=(231, 73), flag_midbottom=(271, 76),
               build_center=(220, 80), neighbors=("alaska", "alberta", "ontario", "groenland"))
        Region("alberta", self, center=(207, 141), flag_midbottom=(190, 130), build_center=(220, 141),
               neighbors=("alaska", "territoires_du_nord_ouest", "ontario", "western"))
        Region("quebec", self, center=(348, 158), flag_midbottom=(337, 132),
               neighbors=("groenland", "ontario", "etats_unis"))
        Region("ontario", self, center=(290, 157), flag_midbottom=(273, 140),
               neighbors=("territoires_du_nord_ouest", "alberta", "western", "etats_unis", "quebec", "groenland"))
        Region("groenland", self, center=(417, 71), flag_midbottom=(455, 63),
               neighbors=("territoires_du_nord_ouest", "ontario", "quebec", "islande"))
        Region("western", self, center=(212, 225), flag_midbottom=(178, 237),
               neighbors=("alberta", "ontario", "etats_unis", "mexique"))
        Region("etats_unis", self, center=(280, 235), flag_midbottom=(248, 259), build_center=(290, 235),
               neighbors=("western", "ontario", "quebec", "mexique"))
        Region("mexique", self, center=(204, 327), flag_midbottom=(192, 300),
               neighbors=("western", "etats_unis", "venezuela"))

        # EUROPA
        Region("islande", self, center=(568, 129), flag_midbottom=(569, 121), build_center=(549, 125),
               neighbors=("groenland", "scandinavie", "grande_bretagne"))
        Region("scandinavie", self, center=(644, 121), flag_midbottom=(654, 90), build_center=(630, 115),
               neighbors=("islande", "europe_du_nord", "grande_bretagne", "russie"))
        Region("grande_bretagne", self, center=(539, 206), flag_midbottom=(526, 204), build_center=None,
               neighbors=("scandinavie", "islande", "europe_du_nord", "europe_occidentale"))
        Region("europe_occidentale", self, center=(561, 311), flag_midbottom=(570, 267), build_center=None,
               neighbors=("grande_bretagne", "europe_du_nord", "europe_meridionale", "afrique_subsaharienne"))
        Region("europe_du_nord", self, center=(627, 219), flag_midbottom=(633, 220), build_center=(604, 238),
               neighbors=("europe_meridionale", "europe_occidentale", "grande_bretagne", "scandinavie", "russie"))
        Region("europe_meridionale", self, center=(629, 308), flag_midbottom=(631, 289), build_center=None,
               neighbors=("europe_du_nord", "europe_occidentale", "russie", "afrique_subsaharienne", "egypte", "moyen-orient"))
        Region("russie", self, center=(750, 201), flag_midbottom=(748, 176), build_center=(728, 198),
               neighbors=("scandinavie", "europe_du_nord", "europe_meridionale", "moyen-orient", "afghanistan", "oural"))

        # ASIA
        Region("moyen-orient", self, center=(731, 409), flag_midbottom=(734, 389), build_center=(737, 422),
               neighbors=("europe_meridionale", "russie", "afghanistan", "inde", "egypte", "afrique_orientale"))
        Region("afghanistan", self, center=(799, 282), flag_midbottom=(802, 278), build_center=(785, 287),
               neighbors=("moyen-orient", "inde", "chine", "russie", "oural"))
        Region("oural", self, center=(850, 162), flag_midbottom=(848, 176), build_center=(850, 200),
               neighbors=("russie", "afghanistan", "siberie", "chine"))
        Region("inde", self, center=(853, 410), flag_midbottom=(845, 399), build_center=(854, 428),
               neighbors=("moyen-orient", "afghanistan", "chine", "siam"))
        Region("chine", self, center=(924, 329), flag_midbottom=(927, 338), build_center=(974, 358),
               neighbors=("siam", "inde", "afghanistan", "oural", "siberie", "mongolie"))
        Region("siberie", self, center=(902, 153), flag_midbottom=(908, 113), build_center=(909, 150),
               neighbors=("oural", "chine", "mongolie", "tchita", "yakoutie"))
        Region("siam", self, center=(932, 440), flag_midbottom=(939, 428), build_center=None,
               neighbors=("inde", "chine", "indonesie"))
        Region("mongolie", self, center=(965, 267), flag_midbottom=(954, 263), build_center=(974, 272),
               neighbors=("chine", "siberie", "tchita", "kamchatka", "japon"))
        Region("japon", self, center=(1068, 263), flag_midbottom=(1078, 217), build_center=(1071, 266),
               neighbors=("kamchatka", "mongolie"))
        Region("tchita", self, center=(961, 198), flag_midbottom=(954, 190), build_center=(943, 207),
               neighbors=("siberie", "mongolie", "kamchatka", "yakoutie"))
        Region("yakoutie", self, center=(976, 113), flag_midbottom=(986, 93), build_center=(964, 122),
               neighbors=("kamchatka", "tchita", "siberie"))
        Region("kamchatka", self, center=(1059, 172), flag_midbottom=(1061, 115), build_center=(1091, 115),
               neighbors=("yakoutie", "tchita", "mongolie", "japon", "alaska"))

        # SOUTH AMERICA
        Region("venezuela", self, center=(290, 406), flag_midbottom=(292, 385), build_center=(260, 405),
               neighbors=("mexique", "perou", "bresil"))
        Region("bresil", self, center=(341, 497), flag_midbottom=(367, 477), build_center=(396, 507),
               neighbors=("venezuela", "perou", "argentine", "afrique_subsaharienne"))
        Region("perou", self, center=(282, 495), flag_midbottom=(261, 488), build_center=(299, 519),
               neighbors=("venezuela", "bresil", "argentine"))
        Region("argentine", self, center=(315, 640), flag_midbottom=(304, 619), build_center=(301, 649),
               neighbors=("perou", "bresil"))

        # AFRICA
        Region("afrique_subsaharienne", self, center=(580, 464), flag_midbottom=(571, 460), build_center=(544, 509),
               neighbors=("bresil", "europe_occidentale", "europe_meridionale", "egypte", "afrique_orientale", "afrique_centrale"))
        Region("egypte", self, center=(648, 420), flag_midbottom=(657, 419), build_center=(665, 420),
               neighbors=("afrique_subsaharienne", "afrique_orientale", "europe_meridionale", "moyen-orient"))
        Region("afrique_centrale", self, center=(661, 587), flag_midbottom=(650, 575),
               neighbors=("afrique_subsaharienne", "afrique_du_sud", "afrique_orientale"))
        Region("afrique_orientale", self, center=(707, 554), flag_midbottom=(700, 519), build_center=(731, 540),
               neighbors=("afrique_subsaharienne", "egypte", "afrique_centrale", "afrique_du_sud", "madacascar", "moyen-orient"))
        Region("afrique_du_sud", self, center=(666, 677), flag_midbottom=(654, 683), build_center=(656, 712),
               neighbors=("afrique_centrale", "afrique_orientale", "madacascar"))
        Region("madacascar", self, center=(747, 682), flag_midbottom=(755, 666), build_center=(736, 690),
               neighbors=("afrique_orientale", "afrique_du_sud"))

        # SOUTH AMERICA
        Region("indonesie", self, center=(922, 535), flag_midbottom=(930, 528), build_center=None,
               neighbors=("siam", "nouvelle_guinee", "australie_occidentale"))
        Region("nouvelle_guinee", self, center=(1022, 516), flag_midbottom=(1009, 497), build_center=(1029, 513),
               neighbors=("australie_occidentale", "australie_orientale", "indonesie"))
        Region("australie_occidentale", self, center=(981, 647), flag_midbottom=(956, 636), build_center=None,
               neighbors=("nouvelle_guinee", "australie_orientale", "indonesie"))
        Region("australie_orientale", self, center=(1048, 644), flag_midbottom=(1044, 624), build_center=(1074, 662),
               neighbors=("nouvelle_guinee", "australie_occidentale"))

    def region_unselect(self):

        if self.selected_region is None:
            return

        self.hovered_region.hide()
        self.selected_region = self.hovered_region = None
        self.signal.REGION_UNSELECT.emit()

    def handle_link(self):

        if self.parent.todo.id < 2:
            return

        for region in self.parent.regions.values():
            if region.get_hovered():
                if region is self.selected_region:
                    self.region_unselect()
                else:
                    if self.selected_region is not None:
                        self.hovered_region.hide()
                    self.hovered_region = self.selected_region = region
                    self.hovered_region.show()
                    self.signal.REGION_SELECT.emit(region)
                    #print(region.title.text, region.center, bp.mouse.x - self.abs.left, bp.mouse.y - self.abs.top)
                return
        self.region_unselect()
        # print(bp.mouse.x - self.abs.left, bp.mouse.y - self.abs.top)


class Region(bp.Image):

    BUILDS = bp.load("images/builds.png")
    DOTTED = BUILDS.subsurface(0, 0, 30, 30)
    CIRCLE = BUILDS.subsurface(30, 0, 30, 30)
    MINE = BUILDS.subsurface(0, 30, 30, 30)
    CAMP = BUILDS.subsurface(30, 30, 30, 30)

    def __init__(self, name, parent, center, flag_midbottom=None, build_center=None, neighbors=()):

        bp.Image.__init__(self, parent, bp.load(f"images/{name}.png"), pos=center, pos_location="center", name=name,
                          touchable=False, visible=False, layer=parent.regions_layer)

        self.mask = bp.mask.from_surface(self.surface)
        self.build_circle = bp.Image(parent, image=Region.DOTTED, visible=False, touchable=False,
                                     pos=build_center if build_center is not None else center, pos_location="center")
        if flag_midbottom is None:
            flag_midbottom = self.build_circle.midtop
        self.flag_midbottom = flag_midbottom
        self.build = None
        self.build_state = "empty"
        self.owner = None
        self.neighbors = neighbors
        self.all_allied_neighbors = []
        self.flag = None

        parent.parent.regions[self.name] = self

        # self.build_rect = bp.Rectangle(parent, color="red", pos=self.build_circle.topleft, size=self.build_circle.size)
        # self.flag_rect = bp.Rectangle(parent, color="blue", pos=flag_midbottom, pos_location="midbottom", size=(36, 60))

    game = property(lambda self: self.scene)
    soldiers_amount = property(lambda self: len(self.owner.regions[self]) if self.owner is not None else 0)

    def add_soldiers(self, amount):

        if self.owner is None:
            raise PermissionError("This country is unoccupied")

        padding = 5
        for i in range(amount):
            ok = 0
            while ok == 0:
                x, y = random.randint(padding, self.w - padding), random.randint(padding, self.h - padding)
                ok = self.mask.get_at((x, y))
                if ok == 1:
                    pixel = self.surface.get_at((x, y))
                    if pixel != (207, 157, 89, 255):
                        ok = 0
            layer = self.parent.frontof_regions_layer if self is self.parent.hovered_region else \
                self.parent.behind_regions_layer
            self.owner.regions[self].append(bp.Image(self.parent, self.owner.soldier_icon, touchable=False,
                                            pos=(x + self.left, y + self.top), pos_location="center", layer=layer))

        self.owner.soldiers_title.set_text(str(sum(len(s_list) for s_list in self.owner.regions.values())))

    def destroy_construction(self):

        if self.build is not None:
            self.build.kill()
        self.build = None
        self.build_circle.lock_visibility(False)
        self.build_circle.hide()
        self.build_circle.set_surface(Region.DOTTED)
        self.build_state = "empty"

    def end_construction(self):

        if self.build_state != "construction":
            raise PermissionError
        self.build_circle.set_surface(Region.CIRCLE)
        self.build_state = "producing"

    def get_hovered(self):

        try:
            return self.mask.get_at((bp.mouse.x - self.abs.left, bp.mouse.y - self.abs.top)) == 1
        except IndexError:
            return False

    def hide(self):

        with bp.paint_lock:
            super().hide()
            if self.owner is None:
                return

            for s in self.owner.regions[self]:
                s.swap_layer(self.parent.behind_regions_layer)
            if self.flag is not None:
                self.flag.swap_layer(self.parent.behind_regions_layer)
            self.build_circle.swap_layer(self.parent.behind_regions_layer)
            if self.build is not None:
                self.build.swap_layer(self.parent.behind_regions_layer)

    def rem_soldiers(self, amount):

        if self.owner is None:
            raise PermissionError("This country is unoccupied")
        if self.soldiers_amount < amount:
            raise PermissionError

        for i in range(amount):
            self.owner.regions[self].pop(0).kill()

        self.owner.update_soldiers_title()

        if self.soldiers_amount == 0:
            self.owner.unconquer(self)

    def show(self):

        with bp.paint_lock:
            super().show()
            if self.owner is None:
                return

            for s in self.owner.regions[self]:
                s.swap_layer(self.parent.frontof_regions_layer)
            if self.flag is not None:
                self.flag.swap_layer(self.parent.frontof_regions_layer)
            self.build_circle.swap_layer(self.parent.frontof_regions_layer)
            if self.build is not None:
                self.build.swap_layer(self.parent.frontof_regions_layer)

    def start_construction(self, build_name):

        self.build_state = "construction"
        self.build_circle.show()
        self.build_circle.lock_visibility()
        self.build = bp.Image(self.parent, getattr(Region, build_name.upper()), name=build_name,
                              pos=self.build_circle.center, pos_location="center", touchable=False)

    def produce(self):

        if self.build_state != "producing":
            return
        if self.build.name == "mine":
            self.owner.gold += 4
        elif self.build.name == "camp":
            self.add_soldiers(3)

    def update_all_allied_neighbors(self, allied_neighbors=None):

        allied_neighbors.add(self)
        for r_name in self.neighbors:
            r = self.game.regions[r_name]
            if r.owner is self.owner:  # r is an allied neighbour
                if r in allied_neighbors:
                    continue
                r.update_all_allied_neighbors(allied_neighbors)
        self.all_allied_neighbors = allied_neighbors


theme = bp.DarkTheme().subtheme()
theme.colors.content = "darkslategray"
# theme.colors.buttontext_font = theme.colors.font
theme.colors.font = "black"
theme.set_style_for(bp.ButtonText, color=theme.colors.border)
theme.set_style_for(bp.Rectangle, color="darkslategray4", border_width=2, border_color="black")
app = bp.Application(name="PremierEmpire", theme=theme, size=(1600, 837))
game = Game(app)


if __name__ == "__main__":
    app.launch()
