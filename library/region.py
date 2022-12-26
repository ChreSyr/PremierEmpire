
import random
import baopig as bp
from baopig.googletrans import dicts


class Structure(bp.Image):

    BUILDS = bp.image.load("images/builds.png")
    WIP = BUILDS.subsurface(0, 0, 30, 30)
    DONE = BUILDS.subsurface(30, 0, 30, 30)
    MINE = BUILDS.subsurface(0, 30, 30, 30)
    CAMP = BUILDS.subsurface(30, 30, 30, 30)

    def __init__(self, region, image, center):

        bp.Image.__init__(self, region.parent, image=image, center=center, visible=False, ref=region.parent.map_image)

        self.region = region
        # State :
        # 0 = empty
        # 1 = under construction
        # 2 = built
        self._state = 0
        self.icon = None

    is_empty = property(lambda self: self._state == 0)
    is_under_construction = property(lambda self: self._state == 1)
    is_built = property(lambda self: self._state == 2)

    def destroy(self):

        if self.icon is not None:
            self.icon.kill()
        self.icon = None

        self.hide()
        self.set_surface(Structure.WIP)
        self._state = 0
    
    def end_construction(self):
        
        if not self.is_under_construction:
            raise PermissionError
        
        self.set_surface(Structure.DONE)
        self._state = 2
    
    def produce(self):
        
        if self.icon.name == "mine":
            self.region.owner.change_gold(+4)
        elif self.icon.name == "camp":
            self.region.add_soldiers(3)

    def start_construction(self, build_name):

        self._state = 1
        self.show()
        self.icon = bp.Image(self.parent, getattr(Structure, build_name.upper()), name=build_name,
                             center=self.rect.center - bp.Vector2(self.parent.map_image.rect.topleft),
                             ref=self.parent.map_image)


class Region(bp.Image):

    def __init__(self, name_id, parent, center, flag_midbottom=None, build_center=None, neighbors=()):

        self.upper_name_id = name_id
        self.upper_name = dicts["fr"][name_id]
        name = self.upper_name.lower().replace(" ", "_").replace("-", "_").replace("é", "e")

        bp.Image.__init__(self, parent, bp.image.load(f"images/{name}.png"), center=center, name=name,
                          visible=False, layer=parent.regions_layer, ref=parent.map_image)

        self.mask = bp.mask.from_surface(self.surface)
        self.structure = Structure(self, image=Structure.WIP,
                                   center=build_center if build_center is not None else center)
        if flag_midbottom is None:
            flag_midbottom = self.structure.rect.midtop
        self.flag_midbottom = flag_midbottom
        self.build = None
        self.build_state = "empty"
        self.owner = None
        self.neighbors = neighbors
        self.all_allied_neighbors = []
        self.flag = None

        self.scene.regions[self.name] = self
        if len(self.scene.draw_pile) < 8:
            self.scene.draw_pile.append(self)

        # self.build_rect = bp.Rectangle(parent, color="red", pos=self.structure.rect.topleft, size=self.structure.rect.size)
        # self.flag_rect = bp.Rectangle(parent, color="blue", midbottom=flag_midbottom, size=(36, 60))

    game = property(lambda self: self.scene)
    soldiers_amount = property(lambda self: len(self.owner.regions[self]) if self.owner is not None else 0)

    def add_soldiers(self, amount):

        if self.owner is None:
            raise PermissionError("This country is unoccupied")

        ref = self.parent.map_image
        padding = 5
        for i in range(amount):
            ok = x = y = 0
            while ok == 0:
                x, y = random.randint(padding, self.rect.w - padding), random.randint(padding, self.rect.h - padding)
                ok = self.mask.get_at((x, y))
                if ok == 1:
                    pixel = self.surface.get_at((x, y))
                    if pixel != (207, 157, 89, 255):
                        ok = 0
            layer = self.parent.frontof_regions_layer if self is self.parent.hovered_region else \
                self.parent.behind_regions_layer
            self.owner.regions[self].append(
                bp.Image(self.parent, self.owner.soldier_icon, layer=layer, ref=ref,
                         center=(x + self.rect.left - ref.rect.left, y + self.rect.top - ref.rect.top))
            )

        self.owner.soldiers_title.set_text(str(sum(len(s_list) for s_list in self.owner.regions.values())))

    def get_hovered(self):

        try:
            return self.mask.get_at((bp.mouse.x - self.abs_rect.left, bp.mouse.y - self.abs_rect.top)) == 1
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
            self.structure.swap_layer(self.parent.behind_regions_layer)
            if self.structure.icon is not None:
                self.structure.icon.swap_layer(self.parent.behind_regions_layer)

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
            self.structure.swap_layer(self.parent.frontof_regions_layer)
            if self.structure.icon is not None:
                self.structure.icon.swap_layer(self.parent.frontof_regions_layer)

    def update_all_allied_neighbors(self, allied_neighbors=None):

        allied_neighbors.add(self)
        for r_name in self.neighbors:
            r = self.game.regions[r_name]
            if r.owner is self.owner:  # r is an allied neighbour
                if r in allied_neighbors:
                    continue
                r.update_all_allied_neighbors(allied_neighbors)
        self.all_allied_neighbors = allied_neighbors
