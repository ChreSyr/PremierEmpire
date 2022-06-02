
import baopig as bp


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
        "north_america": (255, 237, 0),
        "europa": (0, 82, 255),
        "asia": (0, 201, 0),
        "oceania": (214, 0, 153),
        "africa": (108, 124, 111),
        "south_america": (243, 0, 0),
    }

    def __init__(self, game, continent):

        self.game = game
        self.id = len(game.players)
        if self.id in (p.id for p in game.players):
            raise IndexError
        self.continent = continent.upper().replace("_", " ")
        self.name = Player.NAMES[continent]
        self.color = Player.COLORS[continent]

        self.gold = 6
        self.regions = {}

        z = bp.Zone(game.info_right_zone, size=("100%", 100), pos=(0, 97 * len(game.info_right_zone.children)))
        bp.Rectangle(z, size=z.size)
        bp.Rectangle(z, size=(z.w, 32), color=self.color)
        bp.Text(z, self.continent, pos=("50%", 10), pos_location="midtop")
        bp.DynamicText(z, lambda: "Or : " + str(self.gold), pos=(10, 50))

    def build_stuff(self):

        for region in self.regions:
            if region.build_state == "construction":
                region.end_construction()
            else:
                region.build_circle.show()
            region.produce()

    def has_fully_built(self):

        for r in self.regions:
            if r.build_state == "empty":
                return False
        return True


class Game(bp.Scene):

    def __init__(self, app):

        bp.Scene.__init__(self, app, background_color="gray")

        self.players = []
        self.regions = {}
        self.flags = []
        self.current_player_id = 0
        self.turn_index = 0  # 0 is the setup, 1 is the first turn
        self.last_selected_region = None

        # MAP
        map_zone = bp.Zone(self, size=(1225, 753), background_color="gray", sticky="center")
        self.world = WorldImage(map_zone)
        RegionImage("alaska", map_zone, center=(133, 103), flag_midbottom=(133, 77),
                    neighbors=("territoires_du_nord_ouest", "alberta"),
                    title_center=(130, 110))
        RegionImage("territoires_du_nord_ouest", map_zone, center=(231, 73), flag_midbottom=(271, 76),
                    build_center=(220, 80), neighbors=("alaska", "alberta", "ontario", "groenland"),
                    title_center=(220, 85), max_width=100)
        RegionImage("alberta", map_zone, center=(207, 141), flag_midbottom=(190, 130), build_center=(220, 141),
                    neighbors=("alaska", "territoires_du_nord_ouest", "ontario", "western"),
                    title_center=(211, 141))
        RegionImage("quebec", map_zone, center=(348, 158), flag_midbottom=(337, 132),
                    neighbors=("groenland", "ontario", "etats_unis"),
                    title_center=(342, 157))
        RegionImage("ontario", map_zone, center=(290, 157), flag_midbottom=(273, 140),
                    neighbors=("territoires_du_nord_ouest", "alberta", "western", "etats_unis", "quebec", "groenland"),
                    title_center=(281, 153))
        RegionImage("groenland", map_zone, center=(417, 71), flag_midbottom=(455, 63),
                    neighbors=("territoires_du_nord_ouest", "ontario", "quebec"),
                    title_center=(420, 48))
        RegionImage("western", map_zone, center=(212, 225), flag_midbottom=(178, 237),
                    neighbors=("alberta", "ontario", "etats_unis", "mexique"),
                    title_center=(210, 212))
        RegionImage("etats_unis", map_zone, center=(280, 235), flag_midbottom=(248, 259), build_center=(290, 235),
                    neighbors=("western", "ontario", "quebec", "mexique"),
                    title_center=(270, 245))
        RegionImage("mexique", map_zone, center=(204, 327), flag_midbottom=(192, 300),
                    neighbors=("western", "etats_unis"),
                    title_center=(200, 315), max_width=30)

        # PARAMETERS
        param_zone = bp.Zone(self, size=(160, "100%"), background_color="gray", visible=False)
        btn_layer = bp.GridLayer(param_zone, nbcols=1, col_width=param_zone.width, row_height=70)
        btn = bp.Button(parent=param_zone, text="Hide", row=0, sticky="center", command=param_zone.hide)
        btn = bp.Button(parent=param_zone, text="Start", row=1, sticky="center",
                        command=bp.PackedFunctions(param_zone.hide, bp.PrefilledFunction(self.set_todo, 0)))
        btn2 = bp.Button(parent=param_zone, text="Quit", row=2, sticky="center", command=app.exit)
        settings_btn = bp.Button(self, text="=", command=param_zone.show, width=35, text_style={"font_height":40})
        settings_btn.move_behind(param_zone)

        # INGAME INFORMATIONS
        self.info_top_zone = bp.Zone(self, sticky="midtop", size=(map_zone.w, map_zone.top), visible=False)
        self.au_tour_de_colored_rect = bp.Rectangle(self.info_top_zone, size=("100%", "100%"), border_width=0)
        self.au_tour_de = bp.Text(self.info_top_zone, "", sticky="center")
        def next_todo_command():
            if self.todo.id == 5:
                self.next_player()
                self.set_todo(3)
            else:
                self.set_todo(self.todo.id + 1)
        next_todo = bp.Button(self.info_top_zone, "Next  ->", pos=(map_zone.w - 3, 3), pos_location="topright",
                              visible=False, command=next_todo_command)
        self.info_right_zone = bp.Zone(self, sticky="topright", size=(self.w - map_zone.right, self.h))
        self.info_country_zone = bp.Zone(self, size=(150, 150), visible=False)
        self.info_country_zone.set_style_for(bp.Text, color="black", max_width=self.info_country_zone.w - 10)
        r = bp.Rectangle(self.info_country_zone, size=self.info_country_zone.size)
        r2 = bp.Rectangle(self.info_country_zone, size=(r.w, 40), color=(0, 0, 0, 0))
        self.info_country_title = bp.Text(self.info_country_zone, "", align_mode="center", sticky="center", pos_ref=r2)
        self.info_country_soldiers = bp.Text(self.info_country_zone, "", pos=(5, r2.bottom + 5))

        # FLAG CHOOSE
        self.choose_color_zone = bp.Zone(self, size=map_zone.size, background_color=(0, 0, 0, 0), sticky="center",
                                         visible=False)
        r = bp.Rectangle(self.choose_color_zone, size=self.center, sticky="center",
                         color="darkslategray", border_width=2, border_color="black")
        done = bp.Button(self.choose_color_zone, "No more player", command=self.next_turn, width=150, visible=False,
                         pos=(-5, -5), pos_ref=r, pos_ref_location="bottomright", pos_location="bottomright")
        r2 = bp.Rectangle(self.choose_color_zone, size=(r.w, 50), pos=(r.left, r.top - 46), color="black")
        bp.Text(self.choose_color_zone, "Choisis ton peuple", pos=r2.center, pos_location="center", font_height=30)
        class ClickableFlag(bp.Button):
            def __init__(btn, continent,pos):
                bp.Button.__init__(btn, self.choose_color_zone, background_color="gray",
                                   size=(36*3, 60*3), pos=pos, pos_location="center")
                btn.continent = continent
                btn.flag = bp.Image(btn, bp.load(f"images/flag_{continent}.png"), sticky="center")
            def validate(btn, *args, **kwargs):
                self.players.append(Player(self, btn.continent))
                self.next_player()
                self.flags.append(bp.Image(map_zone, bp.load(f"images/flag_{btn.continent}.png"),
                                           visible=False, touchable=False))
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
        hibou_zone = bp.Zone(self, size=self.center, sticky="bottomright", visible=False)
        hibou = bp.Image(hibou_zone, bp.load("images/hibou.png"), sticky="bottomright")
        bulle = bp.Image(hibou_zone, bp.load("images/hibou_bulle.png"), pos=hibou.midtop, pos_location="midbottom")
        bulle_text = bp.Text(hibou_zone, "", pos=(bulle.left + 10, bulle.top + 10), max_width=bulle.width - 20,
                             align_mode="center", color="black")
        bp.Button(hibou_zone, text="Close tutorial", sticky="bottomright",
                  command=bp.PackedFunctions(hibou_zone.hide, hibou_zone.lock_visibility))

        # TODOS
        class Todo:
            @staticmethod
            def confirm_place_flag():
                flag = self.flags[self.current_player_id]
                flag.show()
                self.current_player.regions[self.last_selected_region] = 3  # 3 soldiers in this region
                self.last_selected_region.owner = self.current_player
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
            Todo(0, "owl presentation", f_start=(hibou_zone.show, bp.PrefilledFunction(bulle_text.set_text,
                 "Salut !\nMoi c'est Ponny la chouette !\nClique quelque part pour commencer !"))),
            Todo(1, "choose color",
                 f_start=(self.choose_color_zone.show, hibou_zone.hide,
                          self.info_top_zone.hide, self.info_right_zone.hide),
                 f_end=(self.choose_color_zone.hide, hibou_zone.show,
                        self.info_top_zone.show, self.info_right_zone.show)),
            Todo(2, "place flag", confirm=Todo.confirm_place_flag,
                 f_start=(bp.PrefilledFunction(bulle_text.set_text,
                 "Clique sur un pays pour y planter ton drapeau !"),)),
            Todo(3, "build", f_start=(next_todo.show, lambda: self.current_player.build_stuff(),
                 bp.PrefilledFunction(bulle_text.set_text,
                 "Tu peux maintenant construire des bâtiments ! Les mines rapportent 2 kilos d'or par tour "
                 "et les camps rapportent 3 soldats par tour ! Chaque bâtiment te coûte 3 kilos d'or.")),
                 f_end=(lambda: tuple(r.build_circle.hide() for r in self.current_player.regions),)),
            Todo(4, "attack", f_start=(bp.PrefilledFunction(bulle_text.set_text,
                 "C'est le moment d'étandre ton territoire ! Clique sur tes pays limitrophes pour les envahir !"),),
                 f_end=()),
            Todo(5, "troops movement", f_start=(bp.PrefilledFunction(bulle_text.set_text,
                 "Avant de finir ton tour, réorganise tes troupes, tu dois être prêt à une attaque de tes adversaires !"),),
                 f_end=()),
        ]
        self.todo = Todo(-1)

        # CONFIRMATION
        self.confirm_zone = bp.Zone(self, size=(42, 76), visible=False)
        #self.confirm_zone.theme.colors.border = (0, 0, 0, 0)
        bp.Rectangle(self.confirm_zone, size=self.confirm_zone.size, color="darkslategray")
        bp.Button(self.confirm_zone, size=(30, 30), pos=(6, 6), background_color="green4", focus=-1,
                  background_image=RegionImage.BUILDS.subsurface(0, 60, 30, 30),
                  command=bp.PackedFunctions(lambda: self.todo.confirm(), self.world.unselect))
        bp.Button(self.confirm_zone, size=(30, 30), pos=(6, 40), background_color="red4", focus=-1,
                  background_image=RegionImage.BUILDS.subsurface(30, 60, 30, 30),
                  command=self.world.unselect)

        # CHOOSE BUILD
        self.choose_build_zone = bp.Zone(self, size=(42, 76), visible=False)
        bp.Rectangle(self.choose_build_zone, size=self.confirm_zone.size, color="darkslategray")
        def build(build_name):
            self.last_selected_region.start_construction(build_name)
            self.current_player.gold -= 3
            if self.current_player.gold < 3 or self.current_player.has_fully_built():
                self.set_todo(4)
        bp.Button(self.choose_build_zone, "", size=(30, 30), pos=(6, 6),
                  command=bp.PackedFunctions(bp.PrefilledFunction(build, "mine"), self.world.unselect),
                  background_color="darkslategray", background_image=RegionImage.MINE)
        bp.Button(self.choose_build_zone, "", size=(30, 30), pos=(6, 40),
                  command=bp.PackedFunctions(bp.PrefilledFunction(build, "camp"), self.world.unselect),
                  background_color="darkslategray", background_image=RegionImage.CAMP)

        # SETUP
        self.world.signal.REGION_SELECT.connect(self.handle_region_select)
        self.world.signal.REGION_UNSELECT.connect(self.handle_region_unselect)

    current_player = property(lambda self: self.players[self.current_player_id])

    def handle_region_select(self, region):

        self.last_selected_region = region

        self.info_country_zone.move_at((region.abs.right + 5, region.abs.centery), key="midleft")
        self.info_country_title.set_text(region.name.upper().replace("_", " "))
        self.info_country_soldiers.set_text(f"{region.soldiers} slodats" if region.soldiers else "")
        self.info_country_zone.show()

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
        self.au_tour_de.set_text(f"AU TOUR DE : {self.current_player.continent}")
        self.au_tour_de_colored_rect.set_color(self.current_player.color)

    def next_turn(self):

        self.turn_index += 1
        self.current_player_id = -1
        self.next_player()
        self.set_todo(3)

    def set_todo(self, index):

        self.todo.end()
        self.todo = self.todo_list[index]
        if self.world.selected_region is not None:
            self.world.unselect()
        self.todo.start()

    def receive(self, event):

        # Tutorial first click
        if self.todo.id == 0:
            if event.type == bp.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.set_todo(1)

        # Region sail
        elif self.todo.id > 1:
            if event.type == bp.MOUSEMOTION:
                if self.world.selected_region is None:
                    if self.world.collidemouse():
                        for region in self.regions.values():
                            if self.todo.text == "place flag" and region.owner is not None:
                                continue
                            if region.get_hovered():
                                if self.world.hovered_region is region:
                                    return
                                if self.world.hovered_region is not None:
                                    self.world.hovered_region.sail.hide()
                                self.world.hovered_region = region
                                region.sail.show()
                                return
                    if self.world.hovered_region is not None:
                        self.world.hovered_region.sail.hide()
                    self.world.hovered_region = None

    def run(self):
        pass


class WorldImage(bp.Image, bp.Clickable):

    def __init__(self, parent):

        bp.Image.__init__(self, parent, bp.load("images/world.png"))
        bp.Clickable.__init__(self)
        self.selected_region = None
        self.hovered_region = None

        self.create_signal("REGION_SELECT")
        self.create_signal("REGION_UNSELECT")

    def unselect(self):

        if self.selected_region is None:
            return

        self.selected_region.hide()
        self.hovered_region.sail.hide()
        self.selected_region = None
        self.signal.REGION_UNSELECT.emit()

    def handle_link(self):

        if self.parent.parent.todo.id < 2:
            return

        for region in self.parent.parent.regions.values():
            if region.get_hovered():
                if region is self.selected_region:
                    return
                else:
                    if self.selected_region is not None:
                        self.selected_region.hide()
                        self.hovered_region.sail.hide()
                    self.hovered_region = self.selected_region = region
                    self.hovered_region.sail.show()
                    self.signal.REGION_SELECT.emit(region)
                    #print(region.title.text, region.center, bp.mouse.x - self.abs.left, bp.mouse.y - self.abs.top)
                return
        self.unselect()
        # print(bp.mouse.x - self.abs.left, bp.mouse.y - self.abs.top)

    def validateTBR(self):

        if self.parent.parent.todo.id < 2:
            return

        for region in self.parent.parent.regions.values():
            if region.get_hovered():
                if region is self.selected_region:
                    return
                else:
                    if self.selected_region is not None:
                        self.selected_region.hide()
                        self.hovered_region.sail.hide()
                    region.show()
                    self.selected_region = region
                    self.hovered_region = self.selected_region
                    self.hovered_region.sail.show()
                    self.signal.REGION_SELECT.emit(region)
                    #print(region.title.text, region.center, bp.mouse.x - self.abs.left, bp.mouse.y - self.abs.top)
                return
        if self.selected_region is not None:
            self.selected_region.hide()
            self.hovered_region.sail.hide()
            self.selected_region = None
            self.signal.REGION_UNSELECT.emit()
        # print(bp.mouse.x - self.abs.left, bp.mouse.y - self.abs.top)


class RegionImage(bp.Image):

    BUILDS = bp.load("images/builds.png")
    DOTTED = BUILDS.subsurface(0, 0, 30, 30)
    CIRCLE = BUILDS.subsurface(30, 0, 30, 30)
    MINE = BUILDS.subsurface(0, 30, 30, 30)
    CAMP = BUILDS.subsurface(30, 30, 30, 30)

    def __init__(self, name, parent, center, flag_midbottom, build_center=None,
                 title_center=None, max_width=None, neighbors=()):

        bp.Image.__init__(self, parent, bp.load(f"images/{name}.png"), pos=center, pos_location="center", name=name, touchable=False, visible=False)
        # TODO : remove this object ? the sail might be enough

        # bp.Rectangle(parent, pos=flag_midbottom, pos_location="midbottom", size=(36, 60))
        self.sail = bp.Image(parent, self.surface, visible=False, touchable=False, sticky="center", pos_ref=self)
        self.sail_mask = bp.mask.from_surface(self.sail.surface)

        """
        surf = self.sail.surface.copy()
        import random
        flag = random.choice((bp.BLEND_ADD, bp.BLEND_SUB, bp.BLEND_MULT, bp.BLEND_MIN, bp.BLEND_MAX))
        surf.blit(self.surface, (10, 10), special_flags=flag)
        self.sail.set_surface(surf)
        """
        """
        # Gets a black transparent surface from the alpha image
        surf = self.surface.copy()
        surf.blit(self.sail.surface, (-10, -10), special_flags=bp.BLEND_RGBA_MULT)
        self.sail.set_surface(surf)
        """

        self.build_circle = bp.Image(self.parent, image=RegionImage.DOTTED, pos_location="center", touchable=False,
                                     pos=build_center if build_center is not None else self.center, visible=False)
        self.flag_midbottom = flag_midbottom
        self.build = None
        self.build_state = "empty"
        self.owner = None
        self.neighbors = neighbors

        """self.title = bp.Text(parent, self.name, color="black", font_file="JetBrainsMono-ExtraBold.ttf",
                             max_width=max_width, align_mode="center", touchable=False)
        if title_center is None:
            self.title.center = self.center
        else:
            self.title.center = title_center
        self.signal.SHOW.connect(self.title.show)
        self.signal.HIDE.connect(self.title.hide)
        self.title.hide()
        """

        parent.parent.regions[self.name] = self

    soldiers = property(lambda self: self.owner.regions[self] if self.owner is not None else 0)

    def get_hovered(self):

        try:
            return self.sail_mask.get_at((bp.mouse.x - self.abs.left, bp.mouse.y - self.abs.top)) == 1
        except IndexError:
            return False

    def end_construction(self):

        if self.build_state != "construction":
            raise PermissionError
        self.build_circle.set_surface(RegionImage.CIRCLE)
        self.build_state = "producing"

    def start_construction(self, build_name):

        self.build_state = "construction"
        self.build_circle.show()
        self.build_circle.lock_visibility()
        self.build = bp.Image(self.parent, getattr(RegionImage, build_name.upper()), name=build_name,
                              pos=self.build_circle.center, pos_location="center", touchable=False)

    def produce(self):

        if self.build_state != "producing":
            return
        if self.build.name == "mine":
            self.owner.gold += 2
        elif self.build.name == "camp":
            self.owner.regions[self] += 3


theme = bp.DarkTheme().subtheme()
theme.colors.content = "green4"
theme.set_style_for(bp.Rectangle, color=theme.colors.scene_background, border_width=2, border_color="black")
app = bp.Application(name="PremierEmpire", theme=theme, size=(1600, 837))
game = Game(app)


if __name__ == "__main__":
    app.launch()
