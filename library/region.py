
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
            self.region.owner.change_gold( + self.scene.PRODUCTION_MINE)
        elif self.icon.name == "camp":
            self.region.add_soldiers( + self.scene.PRODUCTION_CAMP)
            self.region.owner.update_soldiers_title()

    def start_construction(self, build_name):

        assert self._state == 0
        self._state = 1
        self.show()
        self._name = build_name.upper()
        self.icon = bp.Image(self.parent, getattr(Structure, self.name), name=build_name, touchable=False,
                             center=self.rect.center - bp.Vector2(self.parent.map_image.rect.topleft),
                             ref=self.parent.map_image, layer=self.layer)


class SoldiersContainer(bp.Focusable):

    MAX = None
    MIN = 0

    def __init__(self, parent, owner, hover, info_zone):

        if not hasattr(self, "_is_focused"):
            bp.Focusable.__init__(self, parent)

        self.hover = hover
        self.info_zone = info_zone
        self.ignore_next_link = False

        self.owner = owner
        self._nb_soldiers = 0

        self.hover.sleep()

    has_infozone_open = property(lambda self: self.info_zone.is_visible and self.info_zone.target is self)

    def add_soldiers(self, amount):
        """ Add soldiers -> return the amount of refused soldiers """

    def handle_focus(self):

        if self.scene.step.id >= 20:
            self.info_zone.open(self)
            self.ignore_next_link = True
        else:
            self.defocus()

    def handle_hover(self):

        if self.scene.step.id < 20:
            return
        self.hover.wake()

    def handle_link(self):

        if self.ignore_next_link:
            self.ignore_next_link = False
        else:
            self.defocus()

    def handle_unhover(self):

        if self.has_infozone_open:
            return
        self.hover.sleep()

    def handle_link_motion(self, rel):

        self.scene.handle_link_motion(rel)

    def rem_soldiers(self, amount):
        """ Remove soldiers """


class Boat(bp.Zone, SoldiersContainer):

    MAX = 5
    TOP_PADDING = 11

    def __init__(self, region):

        ref = region.parent.map_image

        top_padding = Boat.TOP_PADDING

        bp.Zone.__init__(self, region.parent, ref=ref,
                         size=(front.get_width(), front.get_height() + top_padding),
                         center= - bp.Vector2(ref.rect.topleft) + Boat.get_valid_center(region))

        self._region = region
        self._nb_soldiers = 0

        region.boats.append(self)

        self.back = bp.Image(self, image=back, pos=(front.get_width() / 2 - back.get_width() / 2,
                                                         top_padding))

        self.soldiers_zone = bp.Zone(self, size=(0, 22), sticky="midtop", spacing=-1)
        self.soldiers = ()
        for _ in range(5):
            soldier = bp.Image(self.soldiers_zone, image=self.region.owner.soldier_icon)
            soldier.sleep()
            self.soldiers += (soldier,)
        self.front = bp.Image(self, image=front, pos=(0, top_padding))

        SoldiersContainer.__init__(self, self.parent, owner=region.owner,
                                    hover=bp.Image(self, image=hover, pos=(0, top_padding)),
                                    info_zone=self.scene.info_boat_zone)

        self.owner.boats.append(self)
        self.add_soldiers(random.randint(1, 5))
        self.owner.update_soldiers_title()

    all_allied_neighbors = property(lambda self: self.region.all_allied_neighbors)
    default_owner = property(lambda self: self.owner if self.owner is not None else self.region.owner)
    nb_soldiers = property(lambda self: self._nb_soldiers)
    region = property(lambda self: self._region)

    def add_soldiers(self, amount):

        refused_soldiers = None
        if amount + self.nb_soldiers > self.MAX:
            refused_soldiers = amount + self.nb_soldiers - self.MAX
            amount = self.MAX - self.nb_soldiers

        if self.owner is None:
            self.owner = self.region.owner
            self.owner.boats.append(self)

            for soldier_image in self.soldiers:
                soldier_image.set_surface(self.owner.soldier_icon)

        old_nb_soldiers = self._nb_soldiers
        self._nb_soldiers += amount

        for i in range(amount):
            self.soldiers[old_nb_soldiers + i].wake()
        self.soldiers_zone.pack(axis="horizontal")
        self.soldiers_zone.adapt()

        return refused_soldiers

    def get_destination_names(self):
        
        if self.nb_soldiers == 0:
            raise PermissionError("A boat cannot navigate without soldiers")
    
        return tuple(card.name for card in self.owner.cards if card is not None and card.owner != self.owner)

    @staticmethod
    def get_valid_center(region):

        ok = x = y = 0
        while ok == 0:
            x, y = random.randint(0, region.rect.w - 1), random.randint(0, region.rect.h - 1)
            ok = region.mask.get_at((x, y))
            if ok == 0:
                ok = 1
                abs_pos = pygame.Vector2(x, y) + region.rect.topleft
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

        ans = x + region.rect.left, y + region.rect.top - Boat.TOP_PADDING / 2
        return ans

        ref = region.parent
        return x + region.rect.left - ref.rect.left, y + region.rect.top - ref.rect.top - Boat.TOP_PADDING / 2

    def handle_focus(self):

        if self is self.scene.transfer.boat:  # don't open boat info if this boat is being transferred
            return

        super().handle_focus()

    def handle_mousebuttondown(self, event):

        if event.type == bp.MOUSEBUTTONDOWN and event.button in (1, 3):  # left or right click

            if self.scene.step.id == 21:  # attack

                # 1 action :
                #   - pick boat
                if self.scene.transferring and self.owner != self.scene.current_player and event.button == 3:
                    return self.scene.end_transfer(self)  # invading this boat

                if self.scene.transferring:
                    return
                if self.owner != self.scene.current_player:
                    return

                self.scene.start_transfer(self)

            elif self.scene.step.id == 22 and event.button == 3:  # movement and right click

                # 2 actions :
                #   - pick soldiers from boat
                #   - add soldiers to boat

                if self.default_owner != self.scene.current_player:
                    return

                self.scene.start_transfer(self)

    def rem_soldiers(self, amount):

        assert self.nb_soldiers - amount >= 0

        self._nb_soldiers -= amount

        if self.nb_soldiers == 0:
            self.owner.boats.remove(self)
            self.owner = None

        for i in range(amount):
            self.soldiers_zone.default_layer[-1].sleep()
        self.soldiers_zone.pack(axis="horizontal")
        self.soldiers_zone.adapt()

    def set_region(self, region):

        self.region.boats.remove(self)
        self._region = region
        region.boats.append(self)


class Region(bp.Zone, SoldiersContainer):

    MIN = 1

    def __init__(self, name_id, parent, center, flag_midbottom=None, build_center=None, neighbors=()):

        self.upper_name_id = name_id
        self.upper_name = dicts["fr"][name_id]
        name = self.upper_name.lower().replace(" ", "_").replace("-", "_").replace("é", "e")

        hover = load(name)
        bp.Zone.__init__(self, parent, size=hover.get_size(), center=center, name=name,
                         layer=parent.background_layer, ref=parent.map_image)
        SoldiersContainer.__init__(self, parent, owner=None, hover=bp.Image(self, hover),
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
        self.neighbors = neighbors
        self.all_allied_neighbors = []
        self.flag = None

        self.scene.regions[self.name] = self
        self.scene.draw_pile.append(self)

    default_owner = property(lambda self: self.owner)
    game = property(lambda self: self.scene)
    nb_soldiers = property(lambda self: len(self.owner.regions[self]) if self.owner is not None else 0)

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

    def collidemouse(self):

        if self.is_hidden:
            return False

        try:
            return self.mask.get_at((bp.mouse.x - self.abs_rect.left, bp.mouse.y - self.abs_rect.top)) == 1
        except IndexError:
            return False

    def handle_mousebuttondown(self, event):

        if event.type == bp.MOUSEBUTTONDOWN and event.button == 3:  # right click

            if self.scene.step.id == 21:  # attack

                # 4 actions :
                #   - pick troops
                #   - invade empty region
                #   - invade enemy region
                #   - land boat

                # cannot move troops if :

                if self.owner is None:
                    if self.name not in self.scene.transfer.destination_names:
                        return

                elif self.owner is self.scene.current_player:
                    if self.scene.transferring and self.scene.transfer.from_region != self:
                        return

                else:
                    if not self.scene.transferring:
                        return
                    if self is self.scene.transfer.from_region:  # mostly for rapatriate boat to a region with different owner
                        return self.scene.start_transfer(self)
                    if self.name not in self.scene.transfer.destination_names:
                        return

                self.scene.start_transfer(self)

            elif self.scene.step.id == 22:  # movement

                # 2 actions:
                #   - pick troops
                #   - move troops to allied neighbor

                if self.scene.current_player != self.owner:
                    return

                if self.scene.transferring:
                    if self.scene.transfer.from_region != self:
                        if self.name not in self.scene.transfer.destination_names:
                            return

                self.scene.start_transfer(self)

    def rem_soldiers(self, amount):

        if self.owner is None:
            raise PermissionError("This country is unoccupied")
        if self.nb_soldiers < amount:
            raise PermissionError

        for i in range(amount):
            self.owner.regions[self].pop(0).kill()

        if self.nb_soldiers == 0:
            self.owner.unconquer(self)

    def update_all_allied_neighbors(self, allied_neighbors=None):

        allied_neighbors.add(self.name)
        for region_name in self.neighbors:
            region = self.game.regions[region_name]
            if region.owner is self.owner:  # region is an allied neighbour
                if region.name in allied_neighbors:
                    continue
                region.update_all_allied_neighbors(allied_neighbors)
        self.all_allied_neighbors = allied_neighbors
