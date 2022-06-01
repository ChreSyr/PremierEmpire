
import baopig as bp


class Game(bp.Scene):

    def __init__(self, app):

        bp.Scene.__init__(self, app)

        self.regions = []
        map_zone = bp.Zone(self, size=(1225, 753), background_color="gray", sticky="center")
        world_image = WorldImage(map_zone)
        RegionImage("alaska", map_zone, pos=(93, 50), title_center=(130, 110), flag_midbottom=(133, 77))
        RegionImage("territoires_du_nord_ouest", map_zone, pos=(152, 38), title_center=(220, 85),
                    flag_midbottom=(271, 76), build_center=(220, 80), max_width=100)
        RegionImage("alberta", map_zone, pos=(158, 103), title_center=(211, 141), flag_midbottom=(190, 130),
                    build_center=(220, 141))
        RegionImage("quebec", map_zone, pos=(308, 95), title_center=(342, 157), flag_midbottom=(337, 132))
        RegionImage("ontario", map_zone, pos=(249, 103), title_center=(281, 153), flag_midbottom=(271, 132))
        RegionImage("groenland", map_zone, pos=(337, -1), title_center=(420, 48), flag_midbottom=(455, 63))
        RegionImage("western", map_zone, pos=(159, 174), title_center=(210, 212), flag_midbottom=(178, 237))
        RegionImage("etats_unis", map_zone, pos=(215, 173), title_center=(270, 245), flag_midbottom=(248, 259),
                    build_center=(290, 235))
        RegionImage("mexique", map_zone, pos=(165, 259), title_center=(200, 315), max_width=30, flag_midbottom=(192, 300))

        bp.Image(map_zone, bp.load("images/mine.png"), pos=(380, 430))
        bp.Image(map_zone, bp.load("images/camp.png"), pos=(260, 490))
        self.flags = [
            bp.Image(map_zone, bp.load("images/flag_north_america.png"), pos=(260, 70), visible=False),
            bp.Image(map_zone, bp.load("images/flag_europa.png"), pos=(640, 30)),
            bp.Image(map_zone, bp.load("images/flag_asia.png"), pos=(720, 300)),
            bp.Image(map_zone, bp.load("images/flag_south_america.png"), pos=(300, 420)),
            bp.Image(map_zone, bp.load("images/flag_africa.png"), pos=(630, 610)),
            bp.Image(map_zone, bp.load("images/flag_oceania.png"), pos=(1000, 442)),
        ]

        # Parameters
        param_zone = bp.Zone(self, size=(160, "100%"), background_color="gray", visible=False)
        btn_layer = bp.GridLayer(param_zone, nbcols=1, col_width=param_zone.width, row_height=70)
        btn = bp.Button(parent=param_zone, text="Hi !", row=0, sticky="center", command=param_zone.hide)
        btn2 = bp.Button(parent=param_zone, text="Quitter", row=1, sticky="center", command=app.exit)
        settings_btn = bp.Button(self, text="=", command=param_zone.show, width=35, text_style={"font_height":40})
        settings_btn.move_behind(param_zone)

        self.print_zone = bp.Zone(self, pos=(map_zone.right, 0), size=(self.w - map_zone.right, self.h))
        self.player_colors = ["Jaune", "Bleu", "Vert", "Violet", "Gris", "Rouge"]
        self.current_player_index = 0

        self.turn_index = 0  # 0 is the setup, 1 is the first turn

        world_image.signal.REGION_SELECT.connect(self.handle_region_select)
        world_image.signal.REGION_UNSELECT.connect(self.handle_region_unselect)

        self.print_zone.set_style_for(bp.Text, pos_location="center", max_width=self.print_zone.w - 20)
        self.au_tour_de = bp.Text(self.print_zone, f"AU TOUR DE : {self.current_player_color}", pos=("50%", 30))
        self.todo = "place flag"
        self.todo_text = bp.Text(self.print_zone, "Choisissez la région où poser votre drapeau", pos=("50%", 100))
        def next():
            flag = self.flags[self.current_player_index]
            flag.show()
            self.todo = "next step"
        self.confirm_button = bp.Button(self, "V", size=(35, 35), visible=False, background_color="green4", command=next)
        self.cancel_button = bp.Button(self, "X", size=(35, 35), visible=False, background_color="red4")
        self.need_confirmation = True

    current_player_color = property(lambda self: self.player_colors[self.current_player_index])

    def handle_region_select(self, region):

        if self.need_confirmation:
            self.confirm_button.move_at((region.abs_hitbox.left - 10, region.abs_hitbox.top), key="topright")
            self.cancel_button.move_at((region.abs_hitbox.left - 10, self.confirm_button.bottom + 10), key="topright")
            self.confirm_button.show()
            self.cancel_button.show()

        if self.todo == "place flag":
            flag = self.flags[self.current_player_index]
            flag.move_at(region.flag_midbottom, "midbottom")
            flag.show()

    def handle_region_unselect(self):

        self.confirm_button.hide()
        self.cancel_button.hide()

        if self.todo == "place flag":
            flag = self.flags[self.current_player_index]
            flag.hide()

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

        if self.selected_region is not None:
            self.selected_region.hide()
        self.selected_region = None
        self.signal.REGION_UNSELECT.emit()

    def validate(self):

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
                    print(region.title.text, region.center, bp.mouse.x - self.abs.left, bp.mouse.y - self.abs.top)
                return
        if self.selected_region is not None:
            self.selected_region.hide()
            self.selected_region = None
            self.signal.REGION_UNSELECT.emit()
        print(bp.mouse.x - self.abs.left, bp.mouse.y - self.abs.top)


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
app = bp.Application(name="PremierEmpire", theme=theme, size=(1600, 837))
game = Game(app)


if __name__ == "__main__":
    app.launch()
