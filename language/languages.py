
import googletrans
import baopig as bp


class Dictionnaries(dict):
    highest_id = -1
    def add(self, lang1, text1):  # , lang2=None, text2=None
        self.highest_id += 1
        self[lang1][self.highest_id] = text1
        # if lang2:
        #     self[lang2][self.highest_id] = text2
        # print("ADDED", self.highest_id, lang1, text1, lang2, text2)
        return self.highest_id
    def add_translation(self, text_id, lang, translation):
        self[lang][text_id] = translation
    def create(self, lang_id):
        assert isinstance(lang_id, str) and len(lang_id) == 2
        assert lang_id not in self
        self[lang_id] = Dictionnary(lang_id)
        import importlib
        try:
            module = importlib.import_module("language.dict_" + lang_id)
        except ModuleNotFoundError:
            pass
        else:
            for text_id, text in enumerate(module.texts):
                dicts.add_translation(text_id, lang_id, text)
    def get(self, text_id, lang):
        try:
            return self[lang][text_id]
        except KeyError:
            return self[lang_manager.ref_language][text_id]
    def get_id(self, text):
        text_id = None
        for stored_id, stored_text in dicts["fr"].items():
            if stored_text == text:
                text_id = stored_id
                break
        if text_id is None:
            text_id = self.add("fr", text)
        return text_id


class Dictionnary(dict):
    def __init__(self, lang_id):
        dict.__init__(self)
        self.lang_id = lang_id


class SmartTranslator(googletrans.Translator):
    game = None
    def translate(self, text, src, dest):
        if self.game.connected_to_network is False:
            return text

        text_id = dicts.get_id(text)
        try:
            return dicts[dest][text_id]
        except KeyError:
            try:
                translation = super().translate(text, src=src, dest=dest).text
                dicts[dest][text_id] = translation
                return translation
            except Exception:
                bp.LOGGER.warning(f"Couldn't translate {text} from {src} to {dest}")
                # self.game.connected_to_network = False
                return text


class LangManager:
    def __init__(self):
        self.game = None
        self._ref_texts = {}
        self._requests = []
        self._textid_by_widget = {}
        self._ref_language = self._language = "fr"
    language = property(lambda self: self._language)
    ref_language = property(lambda self: self._ref_language)
    def get_text_from_id(self, text_id):
        try:
            return dicts[self._language][text_id]
        except KeyError:
            return dicts[self._ref_language][text_id]
    def remove_widget(self, widget):
        self._ref_texts.pop(widget)
        self._textid_by_widget.pop(widget)
    def request(self, obj, text, src, dest):
        self._requests.append((obj, text, src, dest))
    def set_language(self, lang_id):
        if lang_id == self._language:
            return
        self._language = lang_id
        self.update_language()
    def set_ref_text(self, widget, text=None, text_id=None):
        assert (text is None) != (text_id is None)
        if text_id is None:
            for stored_id, stored_text in dicts["fr"].items():
                if stored_text == text:
                    text_id = stored_id
                    break
            if text_id is None:
                text_id = dicts.add(self._ref_language, text)
        else:
            text = dicts["fr"][text_id]
        self._ref_texts[widget] = text
        self._textid_by_widget[widget] = text_id
        widget.text_id = text_id
        widget.set_text(dicts.get(widget.text_id, self._language))
        widget.fit()
    def update_language(self):

        old_cursor = bp.pygame.mouse.get_cursor()
        bp.pygame.mouse.set_cursor(bp.SYSTEM_CURSOR_WAIT)

        if self.game is None or self.game.connected_to_network is False:

            if self._language == self._ref_language:
                if self.game is not None:
                    for player in self.game.players.values():
                        player.translated_name = player.name
                for widget, text in self._ref_texts.items():
                    widget.set_text(text)
                    widget.fit()
            else:
                if self.game is not None:
                    for player in self.game.players.values():
                        player.translated_name = dicts.get(player.name_id, self._language)
                for widget in self._ref_texts:
                    widget.set_text(dicts.get(widget.text_id, self._language))
                    widget.fit()

        else:

            if self._language != self._ref_language:

                for request in self._requests:
                    request[0].set_text(translator.translate(*request[1:]))

                new_dict = dicts[self._language]
                to_translate = {}

                for ref_text_id, ref_text in dicts[self._ref_language].items():
                    if ref_text_id not in new_dict:
                        to_translate[ref_text_id] = ref_text

                if to_translate:
                    translations = googletrans.Translator.translate(translator, list(to_translate.values()),
                                                                     src=self._ref_language, dest=self._language)

                    for text_id, translation in zip(to_translate.keys(), translations):
                        dicts.add_translation(text_id, lang=self.language, translation=translation)

                for player in self.game.players.values():
                    player.translated_name = dicts.get(player.name_id, self.language)

                for widget in self._ref_texts:
                    widget.set_text(dicts.get(widget.text_id, self._language))
                    widget.fit()

            else:
                for player in self.game.players.values():
                    player.translated_name = player.name
                for widget, text in self._ref_texts.items():
                    widget.set_text(text)
                    widget.fit()

        bp.pygame.mouse.set_cursor(old_cursor)

        if self.game is not None and not "×" in self.game.settings_zone.resolution_btn.text:
            self.game.settings_zone.resolution_btn.set_text(dicts.get(text_id=47, lang=self.language))


class Translatable:

    def __init__(self, text_id=None):

        self.text_id = text_id
        lang_manager.set_ref_text(self, text_id=text_id)

    def fit(self):
        """ Called each time the text has been translated, and need to be ajusted """

    def set_ref_text(self, text_id):
        lang_manager.set_ref_text(self, text_id=text_id)


class TranslatableText(bp.Text, Translatable):

    def __init__(self, parent, text_id=None, **kwargs):

        bp.Text.__init__(self, parent=parent, text=dicts.get(text_id, lang_manager.ref_language), **kwargs)
        Translatable.__init__(self, text_id=text_id)

        def handle_kill():
            lang_manager.remove_widget(self)
        self.signal.KILL.connect(handle_kill, owner=self)


class PartiallyTranslatableText(TranslatableText):

    def __init__(self, parent, get_args:tuple, **kwargs):
        TranslatableText.__init__(self, parent, **kwargs)

        assert self.text.count("{}") == len(get_args)

        self.partial_text = self.translated_partial_text = self.text
        self.get_args = get_args

    def complete_text(self):

        inserts = tuple(dicts.get(text_id=get_arg(), lang=lang_manager.language) for get_arg in self.get_args)
        complete_text = self.translated_partial_text.format(*inserts)
        self.set_text(complete_text)

    def set_text(self, text):
        if "{}" in text:
            self.translated_partial_text = text
            try:
                self.complete_text()
            except:  # still in construction, self.get_args is not defined
                     # or a function in get_args raised an exception
                super().set_text(text)
        else:
            super().set_text(text)


# TODO : remove SmartTranslator ?
translator = SmartTranslator()
lang_manager = LangManager()
dicts = Dictionnaries()
dicts.create("fr")
