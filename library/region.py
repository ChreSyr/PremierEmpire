
import random
import baopig as bp
import pygame
from baopig.googletrans import dicts
from library.images import load, boat_back, boat_front, boat_front_hover
front = pygame.transform.smoothscale(boat_front, ((59, 20)))
hover = pygame.transform.smoothscale(boat_front_hover, ((59, 20)))
back = pygame.transform.smoothscale(boat_back, ((54, 17)))


class Structure(bp.Image):

    BUILDS = bp.image.load("images/builds.png")
    WIP = BUILDS.subsurface(0, 0, 30, 30)
    DONE = BUILDS.subsurface(30, 0, 30, 30)
    MINE = BUILDS.subsurface(0, 30, 30, 30)
    CAMP = BUILDS.subsurface(30, 30, 30, 30)

    def __init__(self, region, image, center):

        bp.Image.__init__(self, region.parent, image=image, center=center, visible=False, touchable=False,
                          ref=region.parent.map_image)

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
        self._name = "NoName"
    
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

        assert self._state == 0
        self._state = 1
        self.show()
        self._name = build_name.upper()
        self.icon = bp.Image(self.parent, getattr(Structure, self.name), name=build_name, touchable=False,
                             center=self.rect.center - bp.Vector2(self.parent.map_image.rect.topleft),
                             ref=self.parent.map_image, layer=self.layer)


class WidgetWithInfoZone(bp.Focusable):

    def __init__(self, parent, hover, info_zone):

        if not hasattr(self, "_is_focused"):
            bp.Focusable.__init__(self, parent)

        self.hover = hover
        self.info_zone = info_zone
        self.ignore_next_link = False

    has_infozone_open = property(lambda self: self.info_zone.is_visible and self.info_zone.target is self)

    def handle_focus(self):

        self.info_zone.open(self)
        self.ignore_next_link = True

    def handle_hover(self):

        if self.scene.step.id < 20:
            return
        self.hover.show()

    def handle_link(self):

        if self.ignore_next_link:
            self.ignore_next_link = False
        else:
            self.defocus()

    def handle_unhover(self):

        if self.has_infozone_open:
            return
        self.hover.hide()

    def handle_link_motion(self, rel):

        self.scene.handle_link_motion(rel)


class Boat(bp.Zone, WidgetWithInfoZone):

    MAX = 5

    def __init__(self, region):

        ok = x = y = 0
        while ok == 0:
            x, y = random.randint(0, region.rect.w - 1), random.randint(0, region.rect.h - 1)
            ok = region.mask.get_at((x, y))
            if ok == 0:
                ok = 1
                abs_pos = pygame.Vector2(x, y) + region.rect.topleft
                # local_pos = abs_pos - region.parent.map_image.rect.topleft
                # try:
                #     pixel2 = region.parent.map_image.surface.get_at((int(local_pos[0]), int(local_pos[1])))
                # except IndexError:
                #     ok = 0
                #     continue
                # if sum(pixel2[:3]) > 50:
                #     ok = 0
                #     continue
                for neighbor_name in region.neighbors:
                    neighbor = region.scene.regions[neighbor_name]
                    local_pos = abs_pos - neighbor.rect.topleft
                    try:
                        if neighbor.mask.get_at(local_pos) == 1:
                            ok = 0
                            break
                    except IndexError:
                        pass
            else:
                ok = 0

        ref = region.parent.map_image

        top_padding = 11

        bp.Zone.__init__(self, region.parent, ref=ref,
                         size=(front.get_width(), front.get_height() + top_padding),
                         center=(x + region.rect.left - ref.rect.left,
                                 y + region.rect.top - ref.rect.top - top_padding / 2))

        self._owner = None
        self._region = region
        self._nb_soldiers = 0

        region.boats.append(self)

        self.back = bp.Image(self, image=back, pos=(front.get_width() / 2 - back.get_width() / 2,
                                                         top_padding))
        self.soldiers_zone = bp.Zone(self, size=(0, 22), sticky="midtop", spacing=-1)
        self.front = bp.Image(self, image=front, pos=(0, top_padding))

        WidgetWithInfoZone.__init__(self, self.parent,
                                    hover=bp.Image(self, image=hover, pos=(0, top_padding), visible=False),
                                    info_zone=self.scene.info_boat_zone)

        for i in range(random.randint(1, 5)):
            self.add_soldier()

    nb_soldiers = property(lambda self: self._nb_soldiers)
    owner = property(lambda self: self._owner)
    region = property(lambda self: self._region)

    def add_soldier(self):

        assert self.nb_soldiers < 5

        if self.owner is None:
            self._owner = self.region.owner
            self.owner.boats.append(self)

        self._nb_soldiers += 1
        bp.Image(self.soldiers_zone, image=self.region.owner.soldier_icon)
        self.soldiers_zone.pack(axis="horizontal")
        self.soldiers_zone.adapt()

    def remove_all_soldiers(self):

        self.owner.boats.remove(self)
        for soldier in tuple(self.soldiers_zone.default_layer):
            soldier.kill()
        self._nb_soldiers = 0
        self._owner = None


class Region(bp.Zone, WidgetWithInfoZone):

    def __init__(self, name_id, parent, center, flag_midbottom=None, build_center=None, neighbors=()):

        self.upper_name_id = name_id
        self.upper_name = dicts["fr"][name_id]
        name = self.upper_name.lower().replace(" ", "_").replace("-", "_").replace("é", "e")

        hover = load(name)
        bp.Zone.__init__(self, parent, size=hover.get_size(), center=center, name=name,
                         layer=parent.background_layer, ref=parent.map_image)
        WidgetWithInfoZone.__init__(self, parent, hover=bp.Image(self, hover, visible=False),
                                    info_zone=None)  # will be set at RegionInfoZone's construction

        self.mask = bp.mask.from_surface(hover)
        self.structure = Structure(self, image=Structure.WIP,
                                   center=build_center if build_center is not None else center)
        if flag_midbottom is None:
            flag_midbottom = self.structure.rect.midtop
        self.flag_midbottom = flag_midbottom
        self.build = None
        self.build_state = "empty"
        self.boats = []
        self.owner = None
        self.neighbors = neighbors
        self.all_allied_neighbors = []
        self.flag = None

        self.scene.regions[self.name] = self
        self.scene.draw_pile.append(self)

    game = property(lambda self: self.scene)
    soldiers_amount = property(lambda self: len(self.owner.regions[self]) if self.owner is not None else 0)

    def add_boat(self):

        Boat(self)

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
                    pixel = self.hover.surface.get_at((x, y))
                    # if pixel != (207, 157, 89, 255):
                    #     ok = 0
                    if pixel not in ((207, 157, 89, 255), (207, 146, 63, 255)):
                        ok = 0
            self.owner.regions[self].append(
                bp.Image(self.parent, self.owner.soldier_icon, ref=ref, touchable=False,
                         center=(x + self.rect.left - ref.rect.left, y + self.rect.top - ref.rect.top))
            )

        self.owner.soldiers_title.set_text(str(sum(len(s_list) for s_list in self.owner.regions.values())))

    def collidemouse(self):

        if self.is_hidden:
            return False

        try:
            return self.mask.get_at((bp.mouse.x - self.abs_rect.left, bp.mouse.y - self.abs_rect.top)) == 1
        except IndexError:
            return False

    def handle_mousebuttondown(self, event):

        if not self.scene.current_player is self.owner:
            return
        if event.type == bp.MOUSEBUTTONDOWN and event.button == 3:  # right click
            if self.scene.step.id in (21, 22):
                self.scene.transfert(self)

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

    def update_all_allied_neighbors(self, allied_neighbors=None):

        allied_neighbors.add(self)
        for r_name in self.neighbors:
            r = self.game.regions[r_name]
            if r.owner is self.owner:  # r is an allied neighbour
                if r in allied_neighbors:
                    continue
                r.update_all_allied_neighbors(allied_neighbors)
        self.all_allied_neighbors = allied_neighbors
