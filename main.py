
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
        self.name = Player.NAMES[continent]
        self.color = Player.COLORS[continent]

        self.gold = 6

        z = bp.Zone(game.info_zone, size=("100%", 100), pos=(0, 97 * len(game.info_zone.children)))
        bp.Rectangle(z, size=z.size)
        bp.Rectangle(z, size=(z.w, 32), color=self.color)
        bp.Text(z, continent.upper().replace("_", " "), pos=("50%", 10), pos_location="midtop")
        bp.DynamicText(z, lambda: "Or : " + str(self.gold), pos=(10, 50))


class Game(bp.Scene):

    def __init__(self, app):

        bp.Scene.__init__(self, app)

        self.players = []
        self.regions = []
        self.flags = []
        self.current_player_id = 0
        self.turn_index = 0  # 0 is the setup, 1 is the first turn

        # MAP
        map_zone = bp.Zone(self, size=(1225, 753), background_color="gray", sticky="center")
        world_image = WorldImage(map_zone)
        RegionImage("alaska", map_zone, pos=(93, 50), title_center=(130, 110), flag_midbottom=(133, 77))
        RegionImage("territoires_du_nord_ouest", map_zone, pos=(152, 38), title_center=(220, 85),
                    flag_midbottom=(271, 76), build_center=(220, 80), max_width=100)
        RegionImage("alberta", map_zone, pos=(158, 103), title_center=(211, 141), flag_midbottom=(190, 130),
                    build_center=(220, 141))
        RegionImage("quebec", map_zone, pos=(308, 95), title_center=(342, 157), flag_midbottom=(337, 132))
        RegionImage("ontario", map_zone, pos=(249, 103), title_center=(281, 153), flag_midbottom=(273, 140))
        RegionImage("groenland", map_zone, pos=(337, -1), title_center=(420, 48), flag_midbottom=(455, 63))
        RegionImage("western", map_zone, pos=(159, 174), title_center=(210, 212), flag_midbottom=(178, 237))
        RegionImage("etats_unis", map_zone, pos=(215, 173), title_center=(270, 245), flag_midbottom=(248, 259),
                    build_center=(290, 235))
        RegionImage("mexique", map_zone, pos=(165, 259), title_center=(200, 315), max_width=30, flag_midbottom=(192, 300))

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
        self.au_tour_de_colored_rect = bp.Rectangle(self, size=(map_zone.width, map_zone.top), pos=(map_zone.left, 0),
                                                    border_width=0)
        self.au_tour_de = bp.Text(self, "AU TOUR DE : -", pos=("50%", map_zone.top / 2), pos_location="center")
        self.info_zone = bp.Zone(self, pos=(map_zone.right, 0), size=(self.w - map_zone.right, self.h))
        self.info_zone.set_style_for(bp.Text, max_width=self.info_zone.w - 20)

        # FLAG CHOOSE
        self.choose_color_zone = bp.Zone(self, size=(1225, 753), background_color=(0, 0, 0, 60), sticky="center", visible=False)
        r = bp.Rectangle(self.choose_color_zone, size=self.center, sticky="center",
                         color="darkslategray", border_width=2, border_color="black")
        def no_more_player_command():
            self.set_todo(3)
            self.next_player()
        done = bp.Button(self.choose_color_zone, "No more player", command=no_more_player_command,
                         pos=(-5, -5), pos_ref=r, pos_ref_location="bottomright", pos_location="bottomright",
                         width=150, visible=False)
        r2 = bp.Rectangle(self.choose_color_zone, size=(r.w, 50), pos=(r.left, r.top - 46), color="black")
        bp.Text(self.choose_color_zone, "Choisissez votre peuple", pos=r2.center, pos_location="center", font_height=30)
        class ClickableFlag(bp.Button):
            def __init__(btn, continent,pos):
                bp.Button.__init__(btn, self.choose_color_zone, background_color="gray",
                                   size=(36*3, 60*3), pos=pos, pos_location="center")
                btn.continent = continent
                btn.flag = bp.Image(btn, bp.image.load(f"images/flag_{continent}.png"), sticky="center")
            def validate(btn, *args, **kwargs):
                self.players.append(Player(self, btn.continent))
                self.next_player()
                self.flags.append(bp.Image(map_zone, bp.load(f"images/flag_{btn.continent}.png"), visible=False))
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
        hibou = bp.Image(hibou_zone, bp.image.load("images/hibou.png"), sticky="bottomright")
        bulle = bp.Image(hibou_zone, bp.image.load("images/hibou_bulle.png"), pos=hibou.midtop, pos_location="midbottom")
        bulle_text = bp.Text(hibou_zone, "", pos=(bulle.left + 10, bulle.top + 10), max_width=bulle.width - 20,
                             align_mode="center", color="black")
        bp.Button(hibou_zone, text="Close tutorial", sticky="bottomright",
                  command=bp.PackedFunctions(hibou_zone.hide, hibou_zone.lock_visibility))

        # TODOS
        class Todo:
            @staticmethod
            def confirm_choose_color():
                pass
            @staticmethod
            def confirm_place_flag():
                flag = self.flags[self.current_player_id]
                flag.show()
                if len(self.players) == 6:
                    self.set_todo(3)
                    self.next_player()
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
                 "Salut ! Moi c'est Ponny la chouette !\nClique quelque part pour commencer !"))),
            Todo(1, "choose color",
                 f_start=(self.choose_color_zone.show, hibou_zone.hide,
                          bp.PrefilledFunction(self.au_tour_de.set_text, "AU TOUR DE : -"),
                          bp.PrefilledFunction(self.au_tour_de_colored_rect.set_color, self.background_color)),
                 f_end=(self.choose_color_zone.hide, hibou_zone.show)),
            Todo(2, "place flag", confirm=Todo.confirm_place_flag,
                 f_start=(bp.PrefilledFunction(bulle_text.set_text,
                 "Clique sur un pays pour y planter ton drapeau !"),)),
            Todo(3, "build", f_start=(bp.PrefilledFunction(bulle_text.set_text,
                 "Tu peux maintenant construire des bâtiments ! Les mines rapportent 2 kilos d'or par tour "
                 "et les camps rapportent 3 soldats par tour !"),))
        ]
        self.todo = None

        # Confirmation
        self.confirm_zone = bp.Zone(self, size=(47, 87), visible=False)
        bp.Rectangle(self.confirm_zone, size=self.confirm_zone.size, color="darkslategray")
        def confirm():
            self.todo.confirm()
        self.confirm_button = bp.Button(self.confirm_zone, "V", size=(35, 35), pos=(6, 6),
                                        background_color="green4", command=confirm)
        self.cancel_button = bp.Button(self.confirm_zone, "X", size=(35, 35), pos=(6, 46),
                                       background_color="red4")

        # SETUP
        world_image.signal.REGION_SELECT.connect(self.handle_region_select)
        world_image.signal.REGION_UNSELECT.connect(self.handle_region_unselect)

    current_player = property(lambda self: self.players[self.current_player_id])

    def handle_region_select(self, region):

        if self.todo.need_confirmation:
            self.confirm_zone.move_at((region.abs_hitbox.left - 5, region.abs_hitbox.top), key="topright")
            self.confirm_zone.show()

        if self.todo.text == "place flag":
            flag = self.flags[self.current_player_id]
            flag.move_at(region.flag_midbottom, "midbottom")
            flag.show()

    def handle_region_unselect(self):

        self.confirm_zone.hide()

        if self.todo.id == "place flag":
            flag = self.flags[self.current_player_id]
            flag.hide()

    def next_player(self):

        self.current_player_id = (self.current_player_id + 1) % len(self.players)
        self.au_tour_de.set_text(f"AU TOUR DE : {self.current_player.name}")
        self.au_tour_de_colored_rect.set_color(self.current_player.color)

    def set_todo(self, index):

        try:
            self.todo.end()
        except AttributeError:
            pass

        self.todo = self.todo_list[index]
        self.todo.start()

    def receive(self, event):

        try:
            if self.todo.id == 0:
                if event.type == bp.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.set_todo(1)
        except AttributeError:
            pass

    def run(self):
        pass


class WorldImage(bp.Image, bp.Clickable):

    def __init__(self, parent):

        bp.Image.__init__(self, parent, bp.load("images/world.png"))
        bp.Clickable.__init__(self)
        self.selected_region = None

        self.create_signal("REGION_SELECT")
        self.create_signal("REGION_UNSELECT")

    def handle_defocus(self):

        if self.selected_region is None:
            return

        self.selected_region.hide()
        self.selected_region = None
        self.signal.REGION_UNSELECT.emit()

    def validate(self):

        if self.parent.parent.todo is None:
            return

        for region in self.parent.parent.regions:
            if region.abs_hitbox.collidepoint(bp.mouse.pos):  # TODO : alpha collision
                if region is self.selected_region:
                    return
                else:
                    if self.selected_region is not None:
                        self.selected_region.hide()
                    region.show()
                    self.selected_region = region
                    self.signal.REGION_SELECT.emit(region)
                    #print(region.title.text, region.center, bp.mouse.x - self.abs.left, bp.mouse.y - self.abs.top)
                return
        if self.selected_region is not None:
            self.selected_region.hide()
            self.selected_region = None
            self.signal.REGION_UNSELECT.emit()
        # print(bp.mouse.x - self.abs.left, bp.mouse.y - self.abs.top)


class RegionImage(bp.Image):

    def __init__(self, name, parent, pos, flag_midbottom, build_center=None, title_center=None, max_width=None):

        bp.Image.__init__(self, parent, bp.load("images/"+name+".png"), pos, name=name, touchable=False)

        self.flag_midbottom = flag_midbottom
        self.build = BuildWidget(self, build_center)

        if "_" in name:
            name = name.replace("_", " ")
        self.title = bp.Text(parent, name.upper(), color="black", font_file="JetBrainsMono-ExtraBold.ttf",
                             max_width=max_width, align_mode="center", touchable=False)

        if title_center is None:
            self.title.center = self.center
        else:
            self.title.center = title_center
        parent.parent.regions.append(self)
        self.hide()
        self.title.hide()

        #self.signal.SHOW.connect(self.title.show)
        #self.signal.HIDE.connect(self.title.hide)


class BuildWidget(bp.Image):

    BUILDS = bp.image.load("images/builds.png")
    EMPTY = BUILDS.subsurface(0, 0, 30, 30)
    MINE = BUILDS.subsurface(0, 30, 30, 30)
    CAMP = BUILDS.subsurface(0, 60, 30, 30)

    def __init__(self, region, center=None):

        if center is None:
            center = region.center
        bp.Image.__init__(self, region.parent, BuildWidget.EMPTY,
                          pos=center, pos_location="center", touchable=False)


theme = bp.DarkTheme().subtheme()
theme.colors.content = "green4"
theme.set_style_for(bp.Rectangle, color=theme.colors.scene_background, border_width=2, border_color="black")
app = bp.Application(name="PremierEmpire", theme=theme, size=(1600, 837))
game = Game(app)


if __name__ == "__main__":
    app.launch()
