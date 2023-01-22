import baopig


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


class Todo:
    @staticmethod
    def confirm_place_flag():
        flag = self.flags[self.current_player_id]
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
