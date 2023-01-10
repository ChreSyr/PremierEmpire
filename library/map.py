
import baopig as bp
from library.zones import RightClickZone
from library.region import Region


class Map(bp.Zone, bp.LinkableByMouse):

    IMAGE = bp.image.load("images/map.png")

    def __init__(self, parent):

        bp.Zone.__init__(self, parent, size=bp.pygame.display.list_modes()[0], sticky="center")
        bp.LinkableByMouse.__init__(self, parent)

        self.selected_region = None
        self.hovered_region = None

        self.background_layer = bp.Layer(self, bp.Image, name="background_layer", level=self.layers_manager.BACKGROUND)
        self.behind_regions_layer = bp.Layer(self, weight=0, name="0",
                                             default_sortkey=lambda w: (w.rect.bottom, w.rect.centerx))
        self.regions_layer = bp.Layer(self, weight=1, name="1")
        self.frontof_regions_layer = bp.Layer(self, weight=2, name="2",
                                              default_sortkey=lambda w: (w.rect.bottom, w.rect.centerx))

        self.create_signal("REGION_SELECT")
        self.create_signal("REGION_UNSELECT")

        self.map_image = bp.Image(self, Map.IMAGE, sticky="center", layer=self.background_layer)

        # SAIL
        self.sail = bp.Circle(self, (0, 0, 0, 63), radius=0, center=(0, 0), visible=False,
                              layer=self.regions_layer, ref=self.map_image)
        def mapsail_open_animate():
            self.sail.set_radius(self.sail.radius + 60)
            if self.sail.radius >= 250:
                self.sail_open_animator.cancel()
        self.sail_open_animator = bp.RepeatingTimer(.03, mapsail_open_animate)
        def mapsail_close_animate():
            self.sail.set_radius(self.sail.radius - 60)
            if self.sail.radius <= 0:
                self.sail_close_animator.cancel()
                self.sail.hide()
        self.sail_close_animator = bp.RepeatingTimer(.02, mapsail_close_animate)

        self._create_regions()

    def _create_regions(self):

        # NORTH AMERICA
        Region(48, self, center=(133, 103), flag_midbottom=(133, 77),
               neighbors=("territoires_du_nord_ouest", "alberta", "kamchatka"))
        Region(49, self, center=(231, 73), flag_midbottom=(271, 76),
               build_center=(220, 80), neighbors=("alaska", "alberta", "ontario", "groenland"))
        Region(50, self, center=(207, 141), flag_midbottom=(190, 130), build_center=(220, 141),
               neighbors=("alaska", "territoires_du_nord_ouest", "ontario", "western"))
        Region(51, self, center=(348, 158), flag_midbottom=(337, 132),
               neighbors=("groenland", "ontario", "etats_unis"))
        Region(52, self, center=(290, 157), flag_midbottom=(273, 140),
               neighbors=("territoires_du_nord_ouest", "alberta", "western", "etats_unis", "quebec", "groenland"))
        Region(53, self, center=(417, 71), flag_midbottom=(455, 63),
               neighbors=("territoires_du_nord_ouest", "ontario", "quebec", "islande"))
        Region(54, self, center=(212, 225), flag_midbottom=(178, 237),
               neighbors=("alberta", "ontario", "etats_unis", "mexique"))
        Region(55, self, center=(280, 235), flag_midbottom=(248, 259), build_center=(290, 235),
               neighbors=("western", "ontario", "quebec", "mexique"))
        Region(56, self, center=(204, 327), flag_midbottom=(192, 300),
               neighbors=("western", "etats_unis", "venezuela"))

        # EUROPA
        Region(57, self, center=(568, 129), flag_midbottom=(569, 121), build_center=(549, 125),
               neighbors=("groenland", "scandinavie", "grande_bretagne"))
        Region(58, self, center=(644, 121), flag_midbottom=(654, 90), build_center=(630, 115),
               neighbors=("islande", "europe_du_nord", "grande_bretagne", "russie"))
        Region(59, self, center=(539, 206), flag_midbottom=(526, 204), build_center=None,
               neighbors=("scandinavie", "islande", "europe_du_nord", "europe_occidentale"))
        Region(60, self, center=(561, 311), flag_midbottom=(570, 267), build_center=None,
               neighbors=("grande_bretagne", "europe_du_nord", "europe_meridionale", "afrique_subsaharienne"))
        Region(61, self, center=(627, 219), flag_midbottom=(633, 220), build_center=(604, 238),
               neighbors=("europe_meridionale", "europe_occidentale", "grande_bretagne", "scandinavie", "russie"))
        Region(62, self, center=(629, 308), flag_midbottom=(631, 289), build_center=None,
               neighbors=("europe_du_nord", "europe_occidentale", "russie", "afrique_subsaharienne", "egypte", "moyen_orient"))
        Region(63, self, center=(750, 201), flag_midbottom=(748, 176), build_center=(728, 198),
               neighbors=("scandinavie", "europe_du_nord", "europe_meridionale", "moyen_orient", "afghanistan", "oural"))

        # ASIA
        Region(64, self, center=(731, 409), flag_midbottom=(734, 389), build_center=(737, 422),
               neighbors=("europe_meridionale", "russie", "afghanistan", "inde", "egypte", "afrique_orientale"))
        Region(65, self, center=(799, 282), flag_midbottom=(802, 278), build_center=(785, 287),
               neighbors=("moyen_orient", "inde", "chine", "russie", "oural"))
        Region(66, self, center=(850, 162), flag_midbottom=(848, 176), build_center=(850, 200),
               neighbors=("russie", "afghanistan", "siberie", "chine"))
        Region(67, self, center=(853, 410), flag_midbottom=(845, 399), build_center=(854, 428),
               neighbors=("moyen_orient", "afghanistan", "chine", "siam"))
        Region(68, self, center=(924, 329), flag_midbottom=(927, 338), build_center=(974, 358),
               neighbors=("siam", "inde", "afghanistan", "oural", "siberie", "mongolie"))
        Region(69, self, center=(902, 153), flag_midbottom=(908, 113), build_center=(909, 150),
               neighbors=("oural", "chine", "mongolie", "tchita", "yakoutie"))
        Region(70, self, center=(932, 440), flag_midbottom=(939, 428), build_center=None,
               neighbors=("inde", "chine", "indonesie"))
        Region(71, self, center=(965, 267), flag_midbottom=(954, 263), build_center=(974, 272),
               neighbors=("chine", "siberie", "tchita", "kamchatka", "japon"))
        Region(72, self, center=(1068, 263), flag_midbottom=(1078, 217), build_center=(1071, 266),
               neighbors=("kamchatka", "mongolie"))
        Region(73, self, center=(961, 198), flag_midbottom=(954, 190), build_center=(943, 207),
               neighbors=("siberie", "mongolie", "kamchatka", "yakoutie"))
        Region(74, self, center=(976, 113), flag_midbottom=(986, 93), build_center=(964, 122),
               neighbors=("kamchatka", "tchita", "siberie"))
        Region(75, self, center=(1059, 172), flag_midbottom=(1061, 115), build_center=(1091, 115),
               neighbors=("yakoutie", "tchita", "mongolie", "japon", "alaska"))

        # SOUTH AMERICA
        Region(76, self, center=(290, 406), flag_midbottom=(292, 385), build_center=(260, 405),
               neighbors=("mexique", "perou", "bresil"))
        Region(77, self, center=(341, 497), flag_midbottom=(367, 477), build_center=(396, 507),
               neighbors=("venezuela", "perou", "argentine", "afrique_subsaharienne"))
        Region(78, self, center=(282, 495), flag_midbottom=(261, 488), build_center=(299, 519),
               neighbors=("venezuela", "bresil", "argentine"))
        Region(79, self, center=(315, 640), flag_midbottom=(304, 619), build_center=(301, 649),
               neighbors=("perou", "bresil"))

        # AFRICA
        Region(80, self, center=(580, 464), flag_midbottom=(571, 460), build_center=(544, 509),
               neighbors=("bresil", "europe_occidentale", "europe_meridionale", "egypte", "afrique_orientale", "afrique_centrale"))
        Region(81, self, center=(648, 420), flag_midbottom=(657, 419), build_center=(665, 420),
               neighbors=("afrique_subsaharienne", "afrique_orientale", "europe_meridionale", "moyen_orient"))
        Region(82, self, center=(661, 587), flag_midbottom=(650, 575),
               neighbors=("afrique_subsaharienne", "afrique_du_sud", "afrique_orientale"))
        Region(83, self, center=(707, 554), flag_midbottom=(700, 519), build_center=(731, 540),
               neighbors=("afrique_subsaharienne", "egypte", "afrique_centrale", "afrique_du_sud", "madacascar", "moyen_orient"))
        Region(84, self, center=(666, 677), flag_midbottom=(654, 683), build_center=(656, 712),
               neighbors=("afrique_centrale", "afrique_orientale", "madacascar"))
        Region(85, self, center=(747, 682), flag_midbottom=(755, 666), build_center=(736, 690),
               neighbors=("afrique_orientale", "afrique_du_sud"))

        # SOUTH AMERICA
        Region(86, self, center=(922, 535), flag_midbottom=(930, 528), build_center=None,
               neighbors=("siam", "nouvelle_guinee", "australie_occidentale"))
        Region(87, self, center=(1022, 516), flag_midbottom=(1009, 497), build_center=(1029, 513),
               neighbors=("australie_occidentale", "australie_orientale", "indonesie"))
        Region(88, self, center=(981, 647), flag_midbottom=(956, 636), build_center=None,
               neighbors=("nouvelle_guinee", "australie_orientale", "indonesie"))
        Region(89, self, center=(1048, 644), flag_midbottom=(1044, 624), build_center=(1074, 662),
               neighbors=("nouvelle_guinee", "australie_occidentale"))

        self.parent.regions_list = list(self.parent.regions.values())

    def region_select(self, region):

        if self.selected_region is not None:
            self.hovered_region.hide()
        self.hovered_region = self.selected_region = region
        self.hovered_region.show()
        self.signal.REGION_SELECT.emit(region)

    def region_unselect(self):

        if self.selected_region is None:
            return

        self.hovered_region.hide()
        self.selected_region = self.hovered_region = None
        self.signal.REGION_UNSELECT.emit()

    def handle_link(self):

        if self.parent.step.id < 20:
            return

        for region in self.parent.regions.values():
            if region.get_hovered():
                if region is self.selected_region:
                    self.region_unselect()
                else:
                    self.region_select(region)
                return
        self.region_unselect()

    def handle_link_motion(self, rel):

        if self.scene.step.id >= 11:

            self.map_image.move(*rel)

    def handle_mousebuttondown(self, event):

        if event.button == 3 and not self.scene.transferring:

            if self.scene.step.id in (21, 22):
                if self.is_hovered:
                    for region in self.scene.current_player.regions:
                        if region.get_hovered():
                            return  # a transfert will start

            with bp.paint_lock:

                def recenter():
                    self.map_image.pos_manager.config(pos=(0, 0))

                rightclick_zone = RightClickZone(self.scene, event)
                rightclick_zone.add_btn(btn_text_id=93, btn_command=recenter)
