

# PORTABILITÉ :
# TODO : Update baopig, puis tester sans la ligne :
#  sys.path.insert(0, 'C:\\Users\\symrb\\Documents\\python\\baopig')
# TODO : Tester le jeu sur un PC Windows sans pygame
# TODO : Tester le jeu sur un MAC
# TODO : Tester le jeu sur un Chromebook (si possible)

# BUGS :

# LANGUES :
# TODO : ref_texts is a .txt (ou un tableau ?)
# TODO : Ajouter un équivalent de ref_texts pour l'anglais
# TODO : Bouton "Autre langue" -> tableau des langues dispo -> ajout d'un nouveau dictionnaire
# TODO : Remplacer le chargement de la langue avec le logo par la souris qui charge
# TODO : Traduire Premier Empire ?
# TODO : Retenir la langue sélectionnée quand on ferme le jeu

# DIVERS :
# TODO : Mettre "Un jour, peut-être en bp.Indicator
# TODO : Griser une étape lorsqu'elle est finie
# TODO : Permettre de cliquer sur une étape pour la commencer
# TODO : Remplacer "Étape suivante" par "Fin du tour"
# TODO : Créer la classe GameStep pour remplacer les Todo

# NOUVEAUTÉS :
# TODO : Permettre d'acheter une carte Région pour 3 or
# TODO : Permettre de construire un bateau
# TODO : Ajouter Region.coast -> endroits où on peut mettre les bateaux
# TODO : Ajouter Region.boats -> tous les bateaux d'une région
# TODO : Permettre d'attaquer avec un bateau les régions qu'on a en carte

# RÈGLES :
# TODO : Choisir si on a un nombre maximum de cartes Région
# TODO : Définir une utilité pour les cartes des régions occupées
# TODO : Définir une façon de se débarrasser de ses cartes Région iutiles ?
# TODO : Choisir si une région a un nombre max de bateaux du même peuple


import os

os.chdir(os.path.dirname(os.path.realpath(__file__)))  # executable from console
import random
import sys
sys.path.insert(0, 'C:\\Users\\symrb\\Documents\\python\\baopig')

import pygame
pygame.init()
screen_sizes = pygame.display.list_modes()
fullscreen_size = screen_sizes[2]

loading_screen = True

def set_progression(prc):

    logo_top, logo_left = fullscreen_size[0] / 2 - logo.get_width() / 2, fullscreen_size[1] / 2 - logo.get_height() / 2
    screen.fill(fuchsia)  # Transparent background
    pygame.draw.rect(screen, (255, 255, 255), pygame.Rect(int(logo_top), int(logo_left),
                                               int(logo.get_width() * prc), logo.get_height()))
    screen.blit(logo, (logo_top, logo_left))
    pygame.display.update()


if loading_screen:
    # LOADING SCREEN

    logo = pygame.image.load("images/logo.png")
    # screen = pygame.display.set_mode(fullscreen_size, pygame.NOFRAME)
    screen = pygame.display.set_mode(fullscreen_size, pygame.NOFRAME | pygame.HIDDEN)
    pygame.display.set_mode(fullscreen_size, pygame.NOFRAME | pygame.SHOWN)
    done = False
    fuchsia = (1, 0, 0)  # Transparency color

    # Transparency
    try:
        import win32api
        import win32con
        import win32gui
        # Create layered window
        hwnd = pygame.display.get_wm_info()["window"]
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE,
                               win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) | win32con.WS_EX_LAYERED)
        # Set window transparency color
        win32gui.SetLayeredWindowAttributes(hwnd, win32api.RGB(*fuchsia), 0, win32con.LWA_COLORKEY)
    except ModuleNotFoundError:
        pass

    set_progression(0)


import baopig as bp
load = bp.image.load

if loading_screen:
    set_progression(.1)

from languages import Dictionnary, Translatable, TranslatableText, PartiallyTranslatableText
from languages import googletrans, load_hardtranslations, dicts, lang_manager, translator

if loading_screen:
    set_progression(.2)

# NOTE for v.1.5 : jouer en réseau
# NOTE for v.2 : entrer son nom de joueur
# NOTE for v.2 : un bâtiment avantageant les pays avec beaucoup de frontières
# NOTE for v.2 : des stratégies différentes, comme au 7 wonders
# NOTE for v.2 : des alliances
# NOTE for v.2 : de la musique !!!


class BackgroundedZone(bp.Zone):
    STYLE = bp.Zone.STYLE.substyle()
    STYLE.modify(
        background_color=(176, 167, 139),
        border_width=2,
        border_color="black"
    )

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
        "asia": s.subsurface(2*w, 0, w, h),
        "south_america": s.subsurface(0, h, w, h),
        "africa": s.subsurface(w, h, w, h),
        "oceania": s.subsurface(2*w, h, w, h),
        # "black": load("images/builds.png").subsurface(38, 38, 14, 14)
    }
    f = load("images/flags.png")
    w, h = f.get_size()
    w = w / 3
    h = h / 2
    FLAGS = {
        "north_america": f.subsurface(0, 0, w, h),
        "europa": f.subsurface(w, 0, w, h),
        "asia": f.subsurface(2*w, 0, w, h),
        "south_america": f.subsurface(0, h, w, h),
        "africa": f.subsurface(w, h, w, h),
        "oceania": f.subsurface(2*w, h, w, h),
    }
    f_big = load("images/flags_big.png")
    w, h = f_big.get_size()
    w = w / 3
    h = h / 2
    FLAGS_BIG = {
        "north_america": f_big.subsurface(0, 0, w, h),
        "europa": f_big.subsurface(w, 0, w, h),
        "asia": f_big.subsurface(2*w, 0, w, h),
        "south_america": f_big.subsurface(0, h, w, h),
        "africa": f_big.subsurface(w, h, w, h),
        "oceania": f_big.subsurface(2*w, h, w, h),
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
                self.game.info_winner_title.complete_text()
                self.game.info_winner_panel.set_color(self.color)
                self.game.info_winner_zone.show()
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


class Game(bp.Scene):

    class TmpMessage(BackgroundedZone, bp.LinkableByMouse):

        def __init__(self, game, text_id, explain_id=None):

            BackgroundedZone.__init__(self, game, size=(300, 100), sticky="midtop", layer_level=2)
            bp.LinkableByMouse.__init__(self, game)

            msg_w = TranslatableText(self, text_id=text_id, max_width=self.rect.w - 10, align_mode="center", pos=(0, 5),
                                     sticky="midtop", font_height=self.get_style_for(bp.Text)["font_height"] + 4)
            r2 = bp.Rectangle(self, size=(self.rect.w, msg_w.rect.h + 10), color=(0, 0, 0, 0), border_width=2)
            if explain_id:
                TranslatableText(self, text_id=explain_id, max_width=self.rect.w - 10,
                                 pos=(5, 5), ref=r2, refloc="bottomleft")

            self.timer = bp.Timer(3, command=self.kill)
            self.timer.start()

        def handle_linkm(self):

            self.timer.cancel()
            self.kill()

    def __init__(self, app):

        bp.Scene.__init__(self, app, background_color=(96, 163, 150))

        self.players = {}
        self.regions = {}
        self.regions_list = None
        self.flags = []
        self.current_player_id = 0
        self.turn_index = 0  # 0 is the setup, 1 is the first turn
        self.last_selected_region = None

        # LAYERS
        self.game_layer = bp.Layer(self, level=1, weight=2)
        self.gameinfo_layer = bp.Layer(self, level=1, weight=3)
        self.gametuto_layer = bp.Layer(self, level=1, weight=4)
        self.extra_layer = bp.Layer(self, level=2, weight=2)
        self.progress_layer = bp.Layer(self, level=2, weight=3)

        # NETWORK
        self._connected_to_network = True

        # TUTORIAL
        self.tutoring = False
        self.tuto_text = 38
        def create_tuto_zone():
            self.tutoring = True
            self.tuto_btn.command = switch_tuto
            self.tuto_btn.text_widget.set_ref_text(8)
            self.tuto_zone = hibou_zone = bp.Zone(self, size=(305, 500), sticky="bottomright",
                                                  layer=self.gametuto_layer)
            hibou1 = bp.Image(hibou_zone, load("images/hibou1.png"), sticky="bottomright", pos=(-30, 50))
            hibou2 = bp.Image(hibou_zone, load("images/hibou2.png"), sticky="bottomright", pos=(-30, 50), visible=False)
            hibou3 = bp.Image(hibou_zone, load("images/hibou3.png"), sticky="bottomright", pos=(-30, 50), visible=False)
            bulle = bp.Image(hibou_zone, load("images/hibou_bulle.png"), midbottom=hibou1.rect.midtop)
            self.tuto_text = TranslatableText(hibou_zone, text_id=self.tuto_text,
                                              pos=(bulle.rect.left + 10, bulle.rect.top + 10),
                                              max_width=bulle.rect.w - 20, align_mode="center")
            def animate_hibou():
                if hibou1.is_visible:
                    hibou1.hide()
                    hibou2.show()
                    self.hibou_animator.set_interval(.45)
                    self.hibou_animator.start()
                elif hibou2.is_visible:
                    hibou2.hide()
                    hibou3.show()
                    self.hibou_animator.start()
                else:
                    hibou3.hide()
                    hibou1.show()
                    self.hibou_animator.set_interval(3 + random.random() * 3)
                    self.hibou_animator.start()
            self.hibou_animator = bp.Timer(.45, animate_hibou)
            self.tuto_zone.signal.HIDE.connect(self.hibou_animator.cancel, owner=None)
            self.tuto_zone.signal.SHOW.connect(self.hibou_animator.start, owner=None)
        def switch_tuto():
            if self.tutoring is False:
                self.tuto_btn.text_widget.set_ref_text(8)
                self.hibou_animator.set_interval(.45)
                self.tuto_zone.show()
                self.tutoring = True
            else:
                self.tuto_btn.text_widget.set_ref_text(7)
                self.tuto_zone.hide()
                self.tutoring = False

        # PARAMETERS
        def close_paramsail():
            if not self.paramsail_animator.is_running:
                self.paramsail_animator.start()
        def toggle_param():
            if param_zone.is_visible:
                param_zone.hide()
                close_paramsail()
            else:
                param_zone.show()
                self.paramsail.set_radius(120)
                self.paramsail.show()
                if not self.paramsail_animator.is_running:
                    self.paramsail_animator.start()
        self.paramsail = bp.Circle(self, (0, 0, 0, 63), radius=120, visible=False, sticky="center", layer_level=2)
        param_zone = BackgroundedZone(self, visible=False, padding=(90, 60), spacing=20, sticky="center",
                                      layer=self.extra_layer)
        param_zone.signal.HIDE.connect(close_paramsail, owner=self.paramsail)
        PE_Button(parent=param_zone, text_id=1, command=param_zone.hide)
        def newgame():
            param_zone.hide()
            self.set_todo(1)
            self.newgame_btn.disable()
        self.newgame_btn = PE_Button(parent=param_zone, text_id=2, command=newgame)
        self.newgame_btn.disable()
        self.tuto_btn = PE_Button(parent=param_zone, text_id=7, command=create_tuto_zone)
        connection_zone = bp.Zone(param_zone)
        self.connection_title = TranslatableText(connection_zone, text_id=9, sticky="midtop", align_mode="center")
        def toggle_connection():
            if self.connected_to_network:
                self.connected_to_network = False
                self.connection_btn.text_widget.set_ref_text(11)
                # if lang_manager.language == "fr":
                #     self.connection_btn.text_widget.set_text("Reconnecter")
            else:
                try:
                    googletrans.Translator.translate(translator, "Bonjour", "fr", "en")
                except Exception:
                    return
                self._connected_to_network = True
                lang_manager.update_language(progress_tracker=self.progress_tracker)
                self.connection_btn.text_widget.set_ref_text(10)
        self.connection_btn = PE_Button(parent=connection_zone, text_id=10, command=toggle_connection,
                                        pos=(0, self.connection_title.rect.bottom + 3))
        connection_zone.adapt()
        lang_zone = bp.Zone(param_zone)
        lang_title = TranslatableText(lang_zone, text_id=12, sticky="midtop")
        self.lang_btn = PE_Button(parent=lang_zone, text="Français", pos=(0, lang_title.rect.bottom + 3),
                                  translatable=False)
        lang_zone.adapt()
        resolution_zone = bp.Zone(param_zone)
        resolution_title = TranslatableText(resolution_zone, text_id=46, sticky="midtop")
        self.resolution_btn = PE_Button(parent=resolution_zone, text=f"{self.rect.width} × {self.rect.height}",
                                        pos=(0, resolution_title.rect.bottom + 3), translatable=False)
        resolution_zone.adapt()
        PE_Button(parent=param_zone, text_id=0, command=app.exit)
        param_zone.default_layer.pack()
        param_zone.adapt(param_zone.default_layer)
        def paramsail_animate():
            if param_zone.is_visible:
                self.paramsail.set_radius(self.paramsail.radius + 60)
                if self.paramsail.radius >= 600:
                    self.paramsail_animator.cancel()
            else:
                self.paramsail.set_radius(self.paramsail.radius - 60)
                if self.paramsail.radius <= 0:
                    self.paramsail_animator.cancel()
                    self.paramsail.hide()
        self.paramsail_animator = bp.RepeatingTimer(.03, paramsail_animate)
        self.settings_btn = PE_Button(self, text_id=13, command=toggle_param, layer=self.extra_layer)

        # LANGUAGE
        def create_lang_choose_zone():
            with bp.paint_lock:
                translator.game = self
                lang_choose_zone = BackgroundedZone(self, padding=(90, 60), spacing=20, sticky="center",
                                                    layer=self.extra_layer)
                self.lang_btn.command = lang_choose_zone.show
                class LangBtn(PE_Button):
                    def __init__(btn, id, text=None):
                        if id not in dicts:
                            dicts[id] = Dictionnary(id)
                        if text is None:
                            text = translator.translate(googletrans.LANGUAGES[id], src="en", dest=id).capitalize()
                        PE_Button.__init__(btn, parent=lang_choose_zone, text=text, translatable=False)
                        btn.id = id
                    def handle_validate(btn):
                        load_hardtranslations(btn.id)
                        lang_manager.set_language(btn.id, progress_tracker=self.progress_tracker)
                        if not self.connected_to_network:
                            Game.TmpMessage(self, text_id=34, explain_id=37)
                        self.lang_btn.text_widget.set_text(btn.text)
                        self.lang_btn.text_widget2.set_text(btn.text)
                PE_Button(lang_choose_zone, text_id=14, command=lang_choose_zone.hide)
                LangBtn(id="es", text="Español")
                LangBtn(id="en", text="English")
                LangBtn(id="fr", text="Français")
                LangBtn(id="it", text="Italiano")
                LangBtn(id="la", text="Latinus")
                lang_choose_zone.pack()
                lang_choose_zone.adapt()
        self.lang_btn.command = create_lang_choose_zone

        # RESOLUTION
        def create_resolution_choose_zone():
            with bp.paint_lock:
                resolution_choose_zone = BackgroundedZone(self, padding=(90, 60), spacing=20, sticky="center",
                                                          layer=self.extra_layer)
                PE_Button(resolution_choose_zone, text_id=14, command=resolution_choose_zone.hide)
                class ResolutionBtn(PE_Button):
                    def __init__(btn, resolution=None):
                        if resolution is None:
                            PE_Button.__init__(btn, resolution_choose_zone, text_id=47)
                        else:
                            PE_Button.__init__(btn, resolution_choose_zone, text=f"{resolution[0]} × {resolution[1]}",
                                               translatable=False)
                        btn.resolution = resolution
                    def handle_validate(btn):
                        if btn.resolution is None:
                            self.application.set_default_size(screen_sizes[0])
                            pygame.display.set_mode(screen_sizes[0], pygame.FULLSCREEN)
                            self.resolution_btn.text_widget.set_text(btn.text)
                            self.resolution_btn.text_widget2.set_text(btn.text)
                        else:
                            self.application.set_default_size(btn.resolution)
                ResolutionBtn()
                for i in range(min(len(screen_sizes), 8)):
                    ResolutionBtn(screen_sizes[i])
                resolution_choose_zone.pack()
                resolution_choose_zone.adapt()
            self.resolution_btn.command = resolution_choose_zone.show
        self.resolution_btn.command = create_resolution_choose_zone

        # PROGRESS TRACKER
        self.progress_tracker = ProgressTracker(self, layer=self.progress_layer)
        self.progress_tracker.hide()

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
        self.next_sail = bp.Zone(map, pos=(-map.rect.h, 0), size=(map.rect.h, "100%"), layer_level=2)
        def nextsail_animate():
            self.next_sail.move(dx=max(abs(self.next_sail.rect.centerx - map.auto_rect.centerx) / 5, 20))
            if self.next_sail.rect.left >= self.map.rect.width:
                self.nextsail_animator.cancel()
        self.nextsail_animator = bp.RepeatingTimer(.04, nextsail_animate)
        bp.Circle(self.next_sail, (0, 0, 0, 63), radius=map.auto_rect.centery, center=("50%", "50%"))
        nextsail_text = bp.Text(self.next_sail, "HELLO !!", font_height=50, font_color="orange", font_bold=True,
                                sticky="center", ref=map)

        # INFORMATION ON TOP & RIGHT
        self.info_right_zone = bp.Zone(self, sticky="midright", size=("10%", 0), spacing=-3, layer=self.gameinfo_layer)
        self.info_top_zone = bp.Zone(self, sticky="midtop", size=("80%", "5%"), visible=False, layer=self.gameinfo_layer)
        self.au_tour_de = PartiallyTranslatableText(self.info_top_zone, sticky="center", text_id=5,
                                                  get_args=(lambda : self.current_player.name_id,))

        # INFORMATION AT LEFT
        self.info_left_zone = bp.Zone(self, sticky="midleft", size=("10%", "60%"), visible=False, layer=self.gameinfo_layer)
        def next_todo_command():
            if self.todo.id == 22:
                self.next_player()
                self.set_todo(20)
            else:
                self.set_todo(self.todo.id + 1)
        self.next_todo = PE_Button(self.info_left_zone, "Étape suivante", width="100%", sticky="midbottom",
                                   command=next_todo_command)
        def handle_timeout():
            if self.todo.text == "build":
                self.todo.end()
            if self.todo.text == "attack":
                self.todo.end()
            self.next_player()
            self.set_todo(20)
        self.time_left = bp.Timer(90, handle_timeout)
        order_zone = bp.Zone(self.info_left_zone, size=("100%", self.next_todo.rect.top))
        def handle_ilz_resize():
            order_zone.resize(self.info_left_zone.rect.width, self.next_todo.rect.top)
            order_zone.pack()
        self.info_left_zone.signal.RESIZE.connect(handle_ilz_resize, owner=order_zone)
        timer_zone = bp.Zone(order_zone, size=("100%", "10%"), background_color="black")
        bp.DynamicText(timer_zone, lambda: bp.format_time(self.time_left.get_time_left(), formatter="%M:%S"),
                            sticky="center", align_mode="center", font_color="white")
        z1 = BackgroundedZone(order_zone, size=("100%", "30%"), padding=5)
        construction_text = TranslatableText(z1, text_id=16, sticky="center", align_mode="center")
        z2 = BackgroundedZone(order_zone, size=("100%", "30%"), padding=5)
        attack_text = TranslatableText(z2, text_id=17, sticky="center", align_mode="center")
        z3 = BackgroundedZone(order_zone, size=("100%", "30%"), padding=5)
        reorganize_text = TranslatableText(z3, text_id=18, sticky="center", align_mode="center")
        order_zone.pack()

        # INFO COUNTRY
        self.info_country_on_hover = False
        self.region_info_zone = BackgroundedZone(self, size=(150, 150), visible=False, layer=self.game_layer)
        r2 = bp.Rectangle(self.region_info_zone, size=(self.region_info_zone.rect.w, 40),
                          color=(0, 0, 0, 0), border_width=2, border_color="black")
        self.invade_btn = RegionInfoButton(self, text_id=4)
        self.back_btn = RegionInfoButton(self, text_id=19)
        self.import_btn = RegionInfoButton(self, text_id=20)
        class InfoCountryTitle(TranslatableText):
            def __init__(txt, *args, **kwargs):
                TranslatableText.__init__(txt, *args, text_id=0, **kwargs)
            def set_region(self, region):
                if region.upper_name == self.text:
                    return
                self.set_ref_text(region.upper_name_id)
        info_country_title = InfoCountryTitle(self.region_info_zone, align_mode="center", sticky="center", ref=r2,
                                              max_width=self.region_info_zone.rect.w - 10)
        self.info_csa = bp.Text(self.region_info_zone, "", pos=(5, r2.rect.bottom + 5))
        self.info_csi = bp.Image(self.region_info_zone, Player.SOLDIERS["asia"],
                                 ref=self.info_csa, pos=(4, -2), refloc="topright")
        def handle_infocountry_change(region=None):
            region = self.map.selected_region if region is None else region

            self.region_info_zone.set_pos(midleft=(region.abs_rect.right + 5, region.abs_rect.centery))
            # info_country_title.set_text(region.name.upper().replace("_", " "))
            info_country_title.set_region(region)
            if region.owner is None:
                self.info_csi.hide()
                self.info_csa.hide()
            else:
                self.info_csi.show()
                self.info_csa.show()
                self.info_csi.set_surface(region.owner.soldier_icon)
                self.info_csa.set_text(str(region.soldiers_amount))
            self.region_info_zone.show()

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
        self.map.signal.REGION_SELECT.connect(handle_infocountry_change, owner=None)

        # REGION CHOOSE
        self.picked_regions = []
        def rc_next():
            if len(self.players) < self.nb_players:
                self.rc_yes.hide()
                self.rc_no.hide()
                set_cursor("default")
                self.set_todo("choose color")
            else:
                self.next_player()
                count = 0
                while self.current_player.flag_region is not None:
                    self.next_player()
                    count += 1
                    if count == self.nb_players:
                        self.current_player_id = -1
                        self.next_player()  # set to player n°1
                        self.time_left.start()
                        self.rc_yes.hide()
                        self.rc_no.hide()
                        return self.set_todo("build")
                self.pick_region()
        def yes():
            self.current_player.flag_region = self.last_selected_region
            flag = self.flags[self.current_player_id]
            flag.swap_layer(map.behind_regions_layer)
            flag.set_pos(midbottom=self.last_selected_region.flag_midbottom)
            flag.show()
            self.current_player.conquer(self.last_selected_region)
            self.current_player.move_flag(self.last_selected_region)
            self.last_selected_region.add_soldiers(3)
            rc_next()
        self.rc_yes = RegionInfoButton(self, text_id=21)
        self.rc_no = RegionInfoButton(self, text_id=22)
        self.rc_yes.set_pos(midbottom=(75, 103))
        self.rc_yes.command = yes
        self.rc_no.command = rc_next

        # WINNER INFO
        self.info_winner_zone = bp.Zone(self, size=map.rect.size, background_color=(0, 0, 0, 63), sticky="center",
                                        visible=False, layer=self.gameinfo_layer)
        self.info_winner_panel = rw1 = bp.Rectangle(self.info_winner_zone, size=("40%", "40%"), sticky="center",
                                                    border_width=2, border_color="black")
        self.info_winner_title = PartiallyTranslatableText(self.info_winner_zone,
                            text_id=23, get_args=(lambda : self.current_player.name_id,),
                            font_height=self.info_winner_zone.get_style_for(bp.Text)["font_height"] + 15,
                            max_width=rw1.rect.w - 10, align_mode="center", pos=(rw1.rect.left + 5, rw1.rect.top + 5))
        rw2 = bp.Rectangle(self.info_winner_zone, size=(rw1.rect.w, self.info_winner_title.rect.h + 10),
                           pos=rw1.rect.topleft, color=(0, 0, 0, 0), border_width=2, border_color="black")  # border
        self.info_winner_subtitle = TranslatableText(self.info_winner_zone, text_id=6, max_width=rw1.rect.w - 10,
                                                     pos=(5, 5), ref=rw2, refloc="bottomleft")
        def ok():
            self.info_winner_zone.hide()
        PE_Button(self.info_winner_zone, "OK", midbottom=(rw1.rect.centerx, rw1.rect.bottom - 5), command=ok)

        # NB PLAYERS CHOOSE
        self.nb_players = None
        self.choose_nb_players_zone = BackgroundedZone(self, size=(992, 400), sticky="center", visible=False,
                                                       layer=self.gameinfo_layer)
        r2 = bp.Rectangle(self.choose_nb_players_zone, size=("100%", 50), color="black")
        centerx = int(self.choose_nb_players_zone.rect.w / 2)
        centery = int((self.choose_nb_players_zone.rect.h + r2.rect.h + 3) / 2)
        TranslatableText(self.choose_nb_players_zone, text_id=25, center=r2.rect.center, font_height=30,
                font_color=self.theme.colors.font_opposite)
        btn_w = 36*3
        btn_marg = 20
        btn_mid = int(btn_w / 2 + btn_marg / 2)
        class ClickableNb(bp.Button):
            STYLE = bp.Button.STYLE.substyle()
            STYLE.modify(text_style={"font_height":30}, background_color=(0, 0, 0, 24), width=btn_w, height=60*3)
            def __init__(btn, number, pos):
                bp.Button.__init__(btn, self.choose_nb_players_zone, text=str(number), center=pos)
                btn.original_font_height = btn.text_widget.font.height
            def handle_hover(btn):
                btn.text_widget.font.config(height=int(btn.original_font_height * 1.5))
            def handle_unhover(btn):
                btn.text_widget.font.config(height=btn.original_font_height)
            def validate(btn, *args, **kwargs):
                self.set_todo("choose color")
                self.nb_players = int(btn.text)

        b1 = ClickableNb(1, pos=(centerx - btn_w * 2 - btn_marg * 2 - btn_mid, centery))
        b1.set_background_color((0, 0, 0, 0))
        b1.disable()
        TranslatableText(b1, text_id=36, sticky="midbottom", pos=(0, -5), align_mode="center")
        ClickableNb(2, pos=(centerx - btn_w * 1 - btn_marg * 1 - btn_mid, centery))
        ClickableNb(3, pos=(centerx - btn_mid, centery))
        ClickableNb(4, pos=(centerx + btn_mid, centery))
        ClickableNb(5, pos=(centerx + btn_w * 1 + btn_marg * 1 + btn_mid, centery))
        ClickableNb(6, pos=(centerx + btn_w * 2 + btn_marg * 2 + btn_mid, centery))

        # FLAG CHOOSE
        self.choose_color_zone = BackgroundedZone(self, size=(992, 400), sticky="center", visible=False,
                                                  layer=self.gameinfo_layer)
        r2 = bp.Rectangle(self.choose_color_zone, size=("100%", 50), color="black")
        centerx = int(self.choose_color_zone.rect.w / 2)
        centery = int((self.choose_color_zone.rect.h + r2.rect.h + 3) / 2)
        TranslatableText(self.choose_color_zone, text_id=26, center=r2.rect.center, font_height=30,
                font_color=self.theme.colors.font_opposite)
        class ClickableFlag(bp.Button):
            STYLE = bp.Button.STYLE.substyle()
            STYLE.modify(background_color=(0, 0, 0, 24), width=btn_w, height=60*3, hover_class=None)
            def __init__(btn, continent, pos):
                bp.Button.__init__(btn, self.choose_color_zone, center=pos)
                btn.continent = continent
                btn.flag = bp.Image(btn, Player.FLAGS[continent], sticky="center")
                btn.flag2 = bp.Image(btn, Player.FLAGS_BIG[continent], sticky="center", visible=False)
                btn.flag2.resize(int(btn.flag.rect.width * 1.5), int(btn.flag.rect.height * 1.5))
            def disable(btn):
                btn.set_background_color((0, 0, 0, 0))
                super().disable()
            def enable(btn):
                btn.set_background_color((0, 0, 0, 24))
                super().enable()
            def handle_hover(btn):
                with bp.paint_lock:
                    btn.flag.hide()
                    btn.flag2.show()
            def handle_unhover(btn):
                with bp.paint_lock:
                    btn.flag.show()
                    btn.flag2.hide()
            def validate(btn, *args, **kwargs):
                Player(self, btn.continent)
                self.next_player()
                self.flags.append(self.current_player.flag)
                self.set_todo("choose region")
                btn.disable()
        ClickableFlag("north_america", pos=(centerx - btn_w * 2 - btn_marg * 2 - btn_mid, centery))
        ClickableFlag("europa", pos=(centerx - btn_w * 1 - btn_marg * 1 - btn_mid, centery))
        ClickableFlag("asia", pos=(centerx - btn_mid, centery))
        ClickableFlag("south_america", pos=(centerx + btn_mid, centery))
        ClickableFlag("africa", pos=(centerx + btn_w * 1 + btn_marg * 1 + btn_mid, centery))
        ClickableFlag("oceania", pos=(centerx + btn_w * 2 + btn_marg * 2 + btn_mid, centery))

        # CLICK TO START
        play_zone = bp.Zone(self, size=(logo.get_width(), logo.get_height()), sticky="center", layer=self.game_layer)
        logo_play_zone = pygame.Surface(logo.get_size())
        logo_play_zone.fill((255, 255, 255))
        logo_play_zone.blit(logo, (0, 0))
        bp.Image(play_zone, image=logo_play_zone)
        play_box = PE_Button(play_zone, text_id=3,
                             center=(0, -37), refloc="midbottom", command=bp.PrefilledFunction(self.set_todo, 1))
        play_box_originalsize = play_box.rect.size
        play_box.growing = True
        def anim_play_zone():
            if play_box.growing:
                if play_box.rect.height >= 48:
                    play_box.growing = False
                else:
                    play_box.resize(play_box.rect.w+2, play_box.rect.h+2)
            else:
                if play_box.rect.height <= 40:
                    play_box.growing = True
                else:
                    play_box.resize(play_box.rect.w-2, play_box.rect.h-2)
        play_btn_animator = bp.RepeatingTimer(.1, anim_play_zone)
        def open_play_zone():
            play_box.resize(*play_box_originalsize)
            play_zone.show()
            play_btn_animator.start()

        # CONFIRMATION
        self.confirm_zone = BackgroundedZone(self, visible=False, padding=6, spacing=4, layer=self.game_layer)
        bp.Button(self.confirm_zone, size=(30, 30), background_color="green4", focus=-1,
                  background_image=Region.BUILDS.subsurface(0, 60, 30, 30),
                  command=bp.PackedFunctions(lambda: self.todo.confirm(), self.map.region_unselect))
        bp.Button(self.confirm_zone, size=(30, 30), background_color="red4", focus=-1,
                  background_image=Region.BUILDS.subsurface(30, 60, 30, 30), command=self.map.region_unselect)
        self.confirm_zone.pack(adapt=True)

        # CHOOSE BUILD
        self.choose_build_zone = BackgroundedZone(self, visible=False, padding=6, spacing=4, layer=self.game_layer)

        def build(build_name):
            self.last_selected_region.start_construction(build_name)
            self.current_player.change_gold(-3)
            self.current_player.check_build()
            self.map.region_unselect()

        bp.Button(self.choose_build_zone, "", size=(30, 30), background_image=Region.MINE,
                  command=bp.PrefilledFunction(build, "mine"), background_color=(0, 0, 0, 0))
        bp.Button(self.choose_build_zone, "", size=(30, 30), background_image=Region.CAMP,
                  command=bp.PrefilledFunction(build, "camp"), background_color=(0, 0, 0, 0))
        self.choose_build_zone.pack(adapt=True)

        # SOLDIERS TRANSFERT
        self.transfert_from = None
        self.transfert_zone = BackgroundedZone(self, size=(35, 24), visible=False,
                                               padding=4, spacing=4, layer=self.game_layer)
        self.transfert_amount = 0
        self.transfert_title = bp.Text(self.transfert_zone, "")
        self.transfert_icon = bp.Image(self.transfert_zone, Player.SOLDIERS["asia"])
        def handle_mouse_motion():
            self.transfert_zone.set_pos(topleft=(bp.mouse.x + 12, bp.mouse.y))
        bp.mouse.signal.MOUSEMOTION.connect(handle_mouse_motion, owner=None)

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
                if len(self.players) == self.nb_players:
                    self.next_turn()
                else:
                    self.set_todo("choose color")

            def __init__(todo, id, text="", confirm=None, f_start=(), f_end=()):
                todo.id = id
                todo.text = text
                todo.confirm = confirm
                todo.need_confirmation = confirm is not None
                todo.f_start = f_start
                todo.f_end = f_end
                self.todo_from_id[id] = todo
                self.todo_from_text[text] = todo

            def start(todo):
                for f in todo.f_start:
                    f()

            def end(todo):
                for f in todo.f_end:
                    f()

        self.todo_from_id = {}
        self.todo_from_text = {}
        def start_presentation():
            self.set_tuto_ref_text_id(38)
            open_play_zone()
        Todo(0, "owl presentation", f_start=(start_presentation,), f_end=(play_zone.hide, play_btn_animator.cancel))
        def start_choosenbplayer():
            self.choose_nb_players_zone.show()
            self.newgame_setup()
            self.set_tuto_ref_text_id(27)
            self.info_top_zone.hide()
            self.info_right_zone.hide()
        Todo(1, "choose nb players", f_start=(start_choosenbplayer,),
             f_end=(self.choose_nb_players_zone.hide,))
        Todo(10, "choose color",
             f_start=(self.choose_color_zone.show, bp.PrefilledFunction(self.set_tuto_ref_text_id, 28)),
             f_end=(self.choose_color_zone.hide, self.info_top_zone.show, self.info_right_zone.show))
        Todo(11, "choose region", f_start=(bp.PrefilledFunction(self.set_tuto_ref_text_id, 29), self.pick_region))
        Todo(17, "place flag", confirm=Todo.confirm_place_flag,
             f_start=(bp.PrefilledFunction(self.set_tuto_ref_text_id, 30),))
        def start_build():
            self.next_todo.show()
            self.info_left_zone.show()
            self.set_tuto_ref_text_id(31)
            z1.set_background_color("orange")
            nextsail_text.set_text(construction_text.text)
            self.current_player.build_stuff()
        Todo(20, "build", f_start=(start_build,),
             f_end=(lambda: tuple(r.build_circle.hide() for r in self.current_player.regions),
             bp.PrefilledFunction(z1.set_background_color, BackgroundedZone.STYLE["background_color"])))
        def start_attack():
            self.set_tuto_ref_text_id(32)
            z2.set_background_color("orange")
            nextsail_text.set_text(attack_text.text)
            self.current_player.check_attack()
        Todo(21, "attack", f_start=(start_attack,),
             f_end=(bp.PrefilledFunction(z2.set_background_color, BackgroundedZone.STYLE["background_color"]),))
        def start_reorganization():
            self.set_tuto_ref_text_id(33)
            z3.set_background_color("orange")
            nextsail_text.set_text(reorganize_text.text)
            self.current_player.check_movement()
        Todo(22, "troops movement", f_start=(start_reorganization,),
             f_end=(bp.PrefilledFunction(z3.set_background_color, BackgroundedZone.STYLE["background_color"]),))

        self.todo = self.todo_from_id[0]
        self.set_todo(0)

        # SETUP
        self.map.signal.REGION_SELECT.connect(self.handle_region_select, owner=self)
        self.map.signal.REGION_UNSELECT.connect(self.handle_region_unselect, owner=self)

    def _set_connected_to_network(self, boolean):
        if boolean:
            raise PermissionError("Can only set game.connected_to_network to False")
        if self._connected_to_network is False:
            return
        self._connected_to_network = False
        # self.connection_title.set_ref_text(text="État du réseau :\nDéconnecté")
        self.connection_btn.text_widget.set_ref_text(11)
        # if lang_manager.language == "fr":
        #     self.connection_title.set_text("État du réseau :\nDéconnecté")
        self.connection_btn.enable()
        # tz = BackgroundedZone(self, size=(250, 150), pos=game.settings_btn.rect.bottomleft, layer_level=2)
        # tz._flip()
        # bp.Text(tz, "Network is not connected")
        Game.TmpMessage(self, text_id=34)
    connected_to_network = property(lambda self: self._connected_to_network, _set_connected_to_network)
    current_player = property(lambda self: self.players[self.current_player_id])
    transferring = property(lambda self: self.transfert_from is not None)

    def end_transfert(self, region=None):

        assert self.transferring
        if region is None:
            region = self.map.selected_region
        if region is None:
            region = self.temp_import_region
        assert region is not None

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

    def handle_event(self, event):

        # Region sail
        if self.todo.id >= 20:
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
                                self.region_info_zone.show()

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
                        if ctrl_hovered is None and self.region_info_zone.is_visible:
                            self.region_info_zone.hide()
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
                            self.region_info_zone.hide()

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

    def handle_region_select(self, region):

        if self.mapsail_close_animator.is_running:
            self.mapsail_close_animator.cancel()
        if self.mapsail_open_animator.is_running:
            self.mapsail_open_animator.cancel()
        self.map_sail.set_pos(center=region.rect.center)
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
            flag.set_pos(midbottom=region.flag_midbottom)
            flag.show()
            self.confirm_zone.set_pos(midright=(region.abs_rect.left - 5, region.abs_rect.centery))
            self.confirm_zone.show()

        if self.todo.text == "build":
            if region in self.current_player.regions and region.build_state == "empty":
                self.choose_build_zone.set_pos(midright=(region.abs_rect.left - 5, region.abs_rect.centery))
                self.choose_build_zone.show()
            else:
                self.choose_build_zone.hide()

    def handle_region_unselect(self):

        if self.mapsail_open_animator.is_running:
            self.mapsail_open_animator.cancel()
        self.mapsail_close_animator.start()

        self.region_info_zone.hide()
        self.confirm_zone.hide()
        self.choose_build_zone.hide()

        if self.todo.text == "place flag":
            flag = self.flags[self.current_player_id]
            flag.hide()

    def handle_resize(self):

        super().handle_resize()
        # if self.resolution_btn.text_widget.has_locked("text"):
        #     return
        text = f"{self.rect.width} × {self.rect.height}"
        self.resolution_btn.text_widget.set_text(text)
        self.resolution_btn.text_widget2.set_text(text)

    def next_player(self):

        if self.todo.id >= 20:
            if self.turn_index > 0 and self.current_player_id == len(self.players) - 1:
                self.turn_index += 1

        self.current_player_id = (self.current_player_id + 1) % len(self.players)
        if not self.current_player.is_alive:
            self.next_player()
            return
        self.au_tour_de.complete_text()
        self.info_top_zone.set_background_color(self.current_player.color)

        if self.time_left.is_running:
            self.time_left.cancel()
        if self.todo.id >= 20:
            self.time_left.start()

        set_cursor(self.current_player.name)

    def next_turn(self):

        self.turn_index += 1
        self.current_player_id = -1
        self.next_player()
        if self.todo.id >= 20:
            self.time_left.start()
        self.set_todo("build")
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

        self.picked_regions.clear()

        set_cursor("default")

    def pick_region(self):

        while True:
            picked = random.choice(self.regions_list)
            if picked not in self.picked_regions:
                self.picked_regions.append(picked)
                break
        self.map.region_select(picked)

        player = self.current_player
        player.choose_region_attemps += 1
        if player.choose_region_attemps < 3:
            self.rc_yes.show()
            self.rc_no.show()
        else:
            self.rc_yes.command()

    def set_todo(self, index):

        if self.transferring:
            self.end_transfert(self.transfert_from)

        self.todo.end()

        if isinstance(index, str):
            self.todo = self.todo_from_text[index]
        else:
            self.todo = self.todo_from_id[index]

        if self.map.selected_region is not None:
            self.map.region_unselect()
        self.todo.start()

        if self.todo.id >= 20:
            self.next_sail.set_pos(right=0)
            if self.nextsail_animator.is_running:
                self.nextsail_animator.cancel()
            self.nextsail_animator.start()

    def set_tuto_ref_text_id(self, text_id):
        self.tuto_ref_text_id = text_id
        if isinstance(self.tuto_text, TranslatableText):
            self.tuto_text.set_ref_text(text_id)
        else:
            self.tuto_text = text_id

    def transfert(self, region):

        if self.transferring:
            if self.transfert_from is region:
                if region.soldiers_amount < 2:
                    self.back_btn.command(region)
                else:
                    self.map.region_unselect()
                    amount = region.soldiers_amount - 1 if bp.keyboard.mod.maj else 1
                    self.transfert_amount += amount
                    region.rem_soldiers(amount)
                    self.transfert_title.set_text(str(self.transfert_amount))
                    self.transfert_zone.pack(axis="horizontal", adapt=True)
            else:
                if self.todo.text == "troops movement":
                    self.temp_import_region = region
                    self.import_btn.validate()
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
            self.transfert_zone.pack(axis="horizontal", adapt=True)
            self.transfert_zone.show()


if loading_screen:
    set_progression(.3)


class ProgressTracker(bp.Zone):

    def __init__(self, scene, **kwargs):

        bp.Zone.__init__(self, parent=scene, size=("100%", "100%"), **kwargs)

        self.logo = bp.Image(self, image=logo, sticky="center")
        self.progress_rect = bp.Rectangle(self, color="white", ref=self.logo, size=(0, self.logo.rect.height))
        self.logo.move_in_front_of(self.progress_rect)

        self.progress = 0

    def set_progress(self, progress):

        assert 0 <= progress <= 1
        self.progress = progress
        self.progress_rect.resize_width(int(self.logo.rect.width * progress))

class Map(bp.Zone, bp.LinkableByMouse):

    IMAGE = load("images/map.png")

    def __init__(self, parent):

        bp.Zone.__init__(self, parent, size=Map.IMAGE.get_size(), background_image=Map.IMAGE, sticky="center")
        bp.LinkableByMouse.__init__(self, parent)

        self.selected_region = None
        self.hovered_region = None

        self.behind_regions_layer = bp.Layer(self, weight=0, name="0",
                                             default_sortkey=lambda w: (w.rect.bottom, w.rect.centerx))
        self.regions_layer = bp.Layer(self, weight=1, name="1")
        self.frontof_regions_layer = bp.Layer(self, weight=2, name="2",
                                              default_sortkey=lambda w: (w.rect.bottom, w.rect.centerx))

        self.create_signal("REGION_SELECT")
        self.create_signal("REGION_UNSELECT")

        self.sail = bp.Circle(self, (0, 0, 0, 63), radius=0, center=(0, 0), visible=False,
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

        if self.parent.todo.id < 20:
            return

        for region in self.parent.regions.values():
            if region.get_hovered():
                if region is self.selected_region:
                    self.region_unselect()
                else:
                    self.region_select(region)
                return
        self.region_unselect()

if loading_screen:
    set_progression(.3)


class Region(bp.Image):

    BUILDS = load("images/builds.png")
    DOTTED = BUILDS.subsurface(0, 0, 30, 30)
    CIRCLE = BUILDS.subsurface(30, 0, 30, 30)
    MINE = BUILDS.subsurface(0, 30, 30, 30)
    CAMP = BUILDS.subsurface(30, 30, 30, 30)

    def __init__(self, name, parent, center, flag_midbottom=None, build_center=None, neighbors=()):

        bp.Image.__init__(self, parent, load(f"images/{name}.png"), center=center, name=name,
                          visible=False, layer=parent.regions_layer)

        self.mask = bp.mask.from_surface(self.surface)
        self.build_circle = bp.Image(parent, image=Region.DOTTED, visible=False,
                                     center=build_center if build_center is not None else center)
        if flag_midbottom is None:
            flag_midbottom = self.build_circle.rect.midtop
        self.flag_midbottom = flag_midbottom
        self.build = None
        self.build_state = "empty"
        self.owner = None
        self.neighbors = neighbors
        self.all_allied_neighbors = []
        self.flag = None
        self.upper_name = self.name.upper().replace("_", " ")
        self.upper_name_id = dicts.get_id(self.upper_name)

        parent.parent.regions[self.name] = self

        # self.build_rect = bp.Rectangle(parent, color="red", pos=self.build_circle.topleft, size=self.build_circle.size)
        # self.flag_rect = bp.Rectangle(parent, color="blue", midbottom=flag_midbottom, size=(36, 60))

    game = property(lambda self: self.scene)
    soldiers_amount = property(lambda self: len(self.owner.regions[self]) if self.owner is not None else 0)

    def add_soldiers(self, amount):

        if self.owner is None:
            raise PermissionError("This country is unoccupied")

        padding = 5
        for i in range(amount):
            ok = 0
            while ok == 0:
                x, y = random.randint(padding, self.rect.w - padding), random.randint(padding, self.rect.h - padding)
                ok = self.mask.get_at((x, y))
                if ok == 1:
                    pixel = self.surface.get_at((x, y))
                    if pixel != (207, 157, 89, 255):
                        ok = 0
            layer = self.parent.frontof_regions_layer if self is self.parent.hovered_region else \
                self.parent.behind_regions_layer
            self.owner.regions[self].append(bp.Image(self.parent, self.owner.soldier_icon,
                                            center=(x + self.rect.left, y + self.rect.top), layer=layer))

        self.owner.soldiers_title.set_text(str(sum(len(s_list) for s_list in self.owner.regions.values())))

    def destroy_construction(self):

        if self.build is not None:
            self.build.kill()
        self.build = None
        self.build_circle.set_lock(visibility=False)
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
        self.build_circle.set_lock(visibility=True)
        self.build = bp.Image(self.parent, getattr(Region, build_name.upper()), name=build_name,
                              center=self.build_circle.rect.center)

    def produce(self):

        if self.build_state != "producing":
            return
        if self.build.name == "mine":
            self.owner.change_gold(+4)
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

if loading_screen:
    set_progression(.4)


btn_background = load("images/btn_back.png")
btn_window = load("images/btn_window.png")
btn_window_topleft = (int((btn_background.get_width() - btn_window.get_width()) / 2),) * 2
default_btn_color = (68, 76, 70)
btn_background.fill(default_btn_color, special_flags=pygame.BLEND_RGBA_MIN)
class PE_Button_Text(bp.Button_Text, Translatable):

    def __init__(self, *args, **kwargs):
        bp.Button_Text.__init__(self, *args, **kwargs)
        if self.parent.is_translatable:
            if self.parent.text_id is None:
                # Translatable.__init__(self, text=self.text)
                Translatable.__init__(self, text_id=dicts.get_id(self.text))
            else:
                Translatable.__init__(self, text_id=self.parent.text_id)

    def fit(self):
        if not hasattr(self.parent, "text_widget2"):
            return  # called from construction
        max_font_height = self.parent.style["text_style"]["font_height"]
        # if self.font.height < max_font_height:
        content_rect = self.parent.content_rect
        self.font.config(height=min(max_font_height, content_rect.height))
        while self.rect.width > content_rect.width or self.rect.height > content_rect.height:
            if self.font.height == 2:
                break
                # raise ValueError(f"This text is too long for the text area : {text} (area={content_rect})")
            self.font.config(height=self.font.height - 1)  # changing the font will automatically update the text
        self.parent.original_font_height = self.font.height

        if self.parent.is_hovered:
            self.font.config(height=self.font.height + 4)
        self.parent.text_widget2.set_text(self.text)
        self.parent.text_widget2.font.config(height=self.font.height)
class PE_Button(bp.Button):

    class Button_HoverImage(bp.Image):

        surf = btn_background.copy()
        win = btn_window.copy()
        win.fill((255, 255, 255, 50), special_flags=pygame.BLEND_RGBA_MIN)
        surf.blit(win, btn_window_topleft)

        def __init__(self, textbutton):

            if textbutton.style["background_color"] != default_btn_color:
                self.surf = load("images/btn_back.png")
                self.surf.fill(textbutton.style["background_color"], special_flags=pygame.BLEND_RGBA_MIN)
                win = btn_window.copy()
                win.fill((255, 255, 255, 50), special_flags=pygame.BLEND_RGBA_MIN)
                self.surf.blit(win, btn_window_topleft)

            surf = self.surf
            if surf.get_size() != textbutton.rect.size:
                surf = pygame.transform.smoothscale(self.surf, textbutton.rect.size)
            bp.Image.__init__(self, textbutton, image=surf, visible=False, layer=textbutton.behind_content)

    class Button_LinkImage(bp.Image):

        surf = btn_background.copy()
        surf.fill((0, 0, 0, 63), special_flags=pygame.BLEND_RGBA_MIN)

        def __init__(self, textbutton):

            surf = self.surf
            if surf.get_size() != textbutton.rect.size:
                surf = pygame.transform.smoothscale(self.surf, textbutton.rect.size)

            bp.Image.__init__(self, textbutton, image=surf, visible=False, layer=textbutton.above_content)

    surf = btn_background.copy()
    win = btn_window.copy()
    win.fill((255, 255, 255, 15), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(win, btn_window_topleft)

    STYLE = bp.Button.STYLE.substyle()
    STYLE.modify(
        focus_class=None,
        hover_class=Button_HoverImage,
        link_class=Button_LinkImage,
        text_class=PE_Button_Text,

        width=140,
        height=40,
        background_color=default_btn_color,
        background_image=surf,
        padding=(10, 7, 10, 7),
        text_style={"font_height": 25},
    )

    def __init__(self, parent, *args, translatable=True, text_id=None, **kwargs):

        if text_id is not None:
            kwargs["text"] = dicts.get(text_id, lang_manager.language)

        self.text_id = text_id
        self.is_translatable = translatable
        bp.Button.__init__(self, parent, *args, **kwargs)
        self.__delattr__("text_id")

        if self.background_color != default_btn_color:
            self.surf = load("images/btn_back.png")
            self.surf.fill(self.background_color, special_flags=pygame.BLEND_RGBA_MIN)
            win = btn_window.copy()
            win.fill((255, 255, 255, 15), special_flags=pygame.BLEND_RGBA_MIN)
            self.surf.blit(win, btn_window_topleft)
            if self.surf.get_size() != self.rect.size:
                self.surf = pygame.transform.smoothscale(self.surf, self.rect.size)
        self.set_background_image(self.surf)
        self.set_background_color((0, 0, 0, 0))

        disable_surf = btn_background.copy()
        disable_surf.fill((255, 255, 255, 128), special_flags=pygame.BLEND_RGBA_MIN)
        if disable_surf.get_size() != self.rect.size:
            disable_surf = pygame.transform.smoothscale(disable_surf, self.rect.size)
        self.disable_sail.kill()
        self._disable_sail_ref =bp.Image(self, disable_surf, visible=False,
                                         layer=self.above_content, name=self.name + ".disable_sail").get_weakref()

        self.text_widget2 = bp.Button_Text(self, text=self.text, layer=self.content, font_color="white",
                                           **self.style["text_style"])
        self.text_widget.move(1, 1)
        self.text_widget2.move(-1, -1)
        self.original_font_height = self.text_widget.font.height

        # def handle_new_surf():
        #     self.text_widget2.set_text(self.text)
        #     if self.is_hovered:
        #         print(4)
        # self.text_widget.signal.NEW_SURFACE.connect(handle_new_surf, owner=self.text_widget2)

    def handle_hover(self):

        with bp.paint_lock:
            self.hover_sail.show()
            self.text_widget.font.config(height=self.original_font_height + 4)
            self.text_widget2.font.config(height=self.original_font_height + 4)

    def handle_unhover(self):

        with bp.paint_lock:
            self.hover_sail.hide()
            self.text_widget.font.config(height=self.original_font_height)
            self.text_widget2.font.config(height=self.original_font_height)


class RegionInfoButton(PE_Button):

    def __init__(self, game, **kwargs):

        PE_Button.__init__(self, game.region_info_zone, midbottom=(75, 145), command=game.end_transfert, **kwargs)


if loading_screen:
    set_progression(.5)


from baopig.prefabs.themes import DarkTheme
class MyTheme(DarkTheme):

    def __init__(self):

        DarkTheme.__init__(self)

        self.colors.content = (176, 167, 139)
        self.colors.font_opposite = self.colors.font
        self.colors.font = "black"

        self.set_style_for(bp.Text, font_file="kirsty-bold", font_height=18)

if loading_screen:
    set_progression(.6)


# bp.pygame.init()
app = bp.Application(name="PremierEmpire", theme=MyTheme(), size=fullscreen_size)
app._debug_launchtime = True

if loading_screen:
    set_progression(.7)

def set_cursor(cursor_name):
    pygame.mouse.set_cursor((5, 0), mouses[cursor_name])
mouses_full = bp.image.load("images/hands.png")
mouses = {
    "default": mouses_full.subsurface(0, 0, 32, 32),
    "Jaune": mouses_full.subsurface(0, 32, 32, 32),
    "Bleu": mouses_full.subsurface(0, 64, 32, 32),
    "Vert": mouses_full.subsurface(0, 96, 32, 32),
    "Rouge": mouses_full.subsurface(0, 128, 32, 32),
    "Gris": mouses_full.subsurface(0, 160, 32, 32),
    "Violet": mouses_full.subsurface(0, 192, 32, 32),
}
set_cursor("default")

if loading_screen:
    set_progression(.8)

game = Game(app)
lang_manager.game = game

if loading_screen:
    set_progression(.9)

if __name__ == "__main__":
    app.launch()
