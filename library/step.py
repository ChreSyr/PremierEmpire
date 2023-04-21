

class Step:

    def __init__(self, game, id, start=None, end=None):

        self.game = game
        self.id = id

        if start:
            self.start = start
        if end:
            self.end = end

        game.step_from_id[id] = self

    def start(self):
        """"""

    def end(self):
        """"""


class Step_Presentation(Step):

    def __init__(self, game):

        Step.__init__(self, game, 0)

    def start(self):
        self.game.set_tuto_ref_text_id(38)
        self.game.play_zone.btn.resize(*self.game.play_zone.btn.original_size)
        self.game.play_zone.show()
        self.game.play_zone.btn_animator.start()

    def end(self):
        self.game.play_zone.hide()
        self.game.play_zone.btn_animator.cancel()


class Step_ChooseNbPLayers(Step):

    def __init__(self, game):

        Step.__init__(self, game, 1)

    def start(self):
        self.game.choose_nb_players_zone.show()
        self.game.newgame_setup()
        self.game.set_tuto_ref_text_id(27)
        self.game.info_top_zone.hide()
        self.game.info_right_zone.hide()

    def end(self):
        self.game.choose_nb_players_zone.hide()


class Step_ChooseColor(Step):

    def __init__(self, game):

        Step.__init__(self, game, 10)

    def start(self):
        self.game.choose_color_zone.show()
        self.game.set_tuto_ref_text_id(28)

    def end(self):
        self.game.choose_color_zone.hide()
        self.game.info_top_zone.show()
        self.game.info_right_zone.show()
