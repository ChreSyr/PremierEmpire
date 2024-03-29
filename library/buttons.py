
import baopig as bp
from baopig import pygame
from baopig.googletrans import Translatable, lang_manager
from library.images import image


class BtnImg:

    def __init__(self):

        # self.window_topleft = (int((btn_background.get_width() - btn_window.get_width()) / 2),) * 2
        self.window_topleft = (5, 5)
        self.default_color = (68, 76, 70)
        self.win_color = (255, 255, 255, 15)
        self.hover_color = (0, 20, 0, 128)

        self.hover_dict = {}  # from size to colored hover
        self.rawback_dict = {image.raw_back.get_size(): image.raw_back}  # from size to raw background
        self.rawwin_dict = {image.raw_window.get_size(): image.raw_window}  # from size to raw window

        self.colored_back = image.raw_back.copy()
        self.colored_win = image.raw_window.copy()
        self.colored_back.fill(self.default_color, special_flags=pygame.BLEND_RGBA_MIN)  # flag for transparency
        self.colored_win.fill(self.win_color, special_flags=pygame.BLEND_RGBA_MIN)  # flag for transparency

        w, h = image.raw_back.get_size()
        self.raw_back_corners = (
            image.raw_back.subsurface(0, 0, 6, 6),
            image.raw_back.subsurface(w - 6, 0, 6, 6),
            image.raw_back.subsurface(w - 6, h - 6, 6, 6),
            image.raw_back.subsurface(0, h - 6, 6, 6),
        )

        w, h = image.raw_window.get_size()
        self.raw_win_corners = (
            image.raw_window.subsurface(0, 0, 6, 6),
            image.raw_window.subsurface(w - 6, 0, 6, 6),
            image.raw_window.subsurface(w - 6, h - 6, 6, 6),
            image.raw_window.subsurface(0, h - 6, 6, 6),
        )

        self.default_background = self.colored_back.copy()
        self.default_background.blit(self.colored_win, self.window_topleft)

        self.default_link = self.colored_back.copy()
        self.default_link.fill((0, 0, 0, 63), special_flags=pygame.BLEND_RGBA_MIN)

        self.default_hover = image.raw_back.copy()
        self.default_hover.fill(self.hover_color, special_flags=pygame.BLEND_RGBA_MIN)
        self.win_hover = image.raw_window.copy()
        self.win_hover.fill((255, 255, 255, 50), special_flags=pygame.BLEND_RGBA_MIN)
        self.default_hover.blit(self.win_hover, self.window_topleft)
        self.hover_dict[image.raw_back.get_size()] = self.default_hover

    def get_resized_background(self, size, color=None):

        if color is None:
            color = self.default_color
        else:
            color = bp.Color(color)

        w, h = size

        try:
            surf = self.rawback_dict[size].copy()

        except KeyError:
            surf = pygame.Surface(size, pygame.SRCALPHA)

            surf.blit(self.raw_back_corners[0], (0, 0))
            surf.blit(self.raw_back_corners[1], (w - 6, 0))
            surf.blit(self.raw_back_corners[2], (w - 6, h - 6))
            surf.blit(self.raw_back_corners[3], (0, h - 6))

            self.rawback_dict[size] = surf.copy()

        surf.fill(color, special_flags=pygame.BLEND_RGBA_MIN)

        if w > 12:
            pygame.draw.rect(surf, color, (6, 0, w - 12, h))
        if h > 12:
            pygame.draw.rect(surf, color, (0, 6, w, h - 12))

        win_width = int(w * 13 / 14)
        if win_width % 2 == 1:
            win_width -= 1
        win_height = int(h / 2)
        win = pygame.Surface((win_width, win_height), pygame.SRCALPHA)

        win.blit(self.raw_win_corners[0], (0, 0))
        win.blit(self.raw_win_corners[1], (win_width - 6, 0))
        win.blit(self.raw_win_corners[2], (win_width - 6, win_height - 6))
        win.blit(self.raw_win_corners[3], (0, win_height - 6))

        win.fill(self.win_color, special_flags=pygame.BLEND_RGBA_MIN)

        if win_width > 12:
            pygame.draw.rect(win, self.win_color, (6, 0, win_width - 12, win_height))
        if win_height > 12:
            pygame.draw.rect(win, self.win_color, (0, 6, win_width, win_height - 12))

        win_topleft = (int((w - win_width) / 2),) * 2
        surf.blit(win, win_topleft)

        return surf

    def get_resized_hover(self, size):

        if size in self.hover_dict:
            return self.hover_dict[size]

        color = self.hover_color
        surf = pygame.Surface(size, pygame.SRCALPHA)

        w, h = size
        surf.blit(self.raw_back_corners[0], (0, 0))
        surf.blit(self.raw_back_corners[1], (w - 6, 0))
        surf.blit(self.raw_back_corners[2], (w - 6, h - 6))
        surf.blit(self.raw_back_corners[3], (0, h - 6))

        if w > 12:
            pygame.draw.rect(surf, color, (6, 0, w - 12, h))
        if h > 12:
            pygame.draw.rect(surf, color, (0, 6, w, h - 12))

        surf.fill(color, special_flags=pygame.BLEND_RGBA_MIN)

        win_width = int(w * 13 / 14)
        if win_width % 2 == 1:
            win_width -= 1
        win_height = int(h / 2)
        win = pygame.Surface((win_width, win_height), pygame.SRCALPHA)

        win.blit(self.raw_win_corners[0], (0, 0))
        win.blit(self.raw_win_corners[1], (win_width - 6, 0))
        win.blit(self.raw_win_corners[2], (win_width - 6, win_height - 6))
        win.blit(self.raw_win_corners[3], (0, win_height - 6))

        win.fill((255, 255, 255, 50), special_flags=pygame.BLEND_RGBA_MIN)

        if win_width > 12:
            pygame.draw.rect(win, (255, 255, 255, 50), (6, 0, win_width - 12, win_height))
        if win_height > 12:
            pygame.draw.rect(win, (255, 255, 255, 50), (0, 6, win_width, win_height - 12))

        win_topleft = (int((w - win_width) / 2),) * 2
        surf.blit(win, win_topleft)

        self.hover_dict[size] = surf

        return surf

    def get_resized_window(self, size, color=None):

        if color is None:
            color = self.win_color
        else:
            color = bp.Color(color)

        w, h = size

        try:
            win = self.rawwin_dict[size].copy()

        except KeyError:
            win = pygame.Surface((w, h), pygame.SRCALPHA)

            win.blit(self.raw_win_corners[0], (0, 0))
            win.blit(self.raw_win_corners[1], (w - 6, 0))
            win.blit(self.raw_win_corners[2], (w - 6, h - 6))
            win.blit(self.raw_win_corners[3], (0, h - 6))

            self.rawwin_dict[size] = win.copy()

        win.fill(color, special_flags=pygame.BLEND_RGBA_MIN)

        if w > 12:
            pygame.draw.rect(win, color, (6, 0, w - 12, h))
        if h > 12:
            pygame.draw.rect(win, color, (0, 6, w, h - 12))

        win.fill(color, special_flags=pygame.BLEND_RGBA_MIN)

        return win


btnimg_manager = BtnImg()


class ButtonWithSound(bp.Button):

    def handle_link(self):

        self.scene.sounds.click.play()
        super().handle_link()


class PE_Button_Text(bp.Button_Text, Translatable):

    def __init__(self, *args, **kwargs):
        bp.Button_Text.__init__(self, *args, **kwargs)
        if self.parent.is_translatable:
            assert self.parent.text_id is not None, "A translatable widget needs a text_id instead of a text"
            Translatable.__init__(self, self.parent, text_id=self.parent.text_id)

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


class PE_Button(ButtonWithSound):

    class Button_DisableImage(bp.Image):

        def __init__(self, textbutton):

            surf = btnimg_manager.colored_back.copy()
            surf.fill((255, 255, 255, 128), special_flags=pygame.BLEND_RGBA_MIN)
            if surf.get_size() != textbutton.rect.size:
                surf = pygame.transform.smoothscale(surf, textbutton.rect.size)

            bp.Image.__init__(self, textbutton, image=surf, visible=False, layer=textbutton.above_content)

    class Button_HoverImage(bp.Image):

        def __init__(self, textbutton):

            surf = btnimg_manager.default_hover
            if surf.get_size() != textbutton.rect.size:
                surf = btnimg_manager.get_resized_hover(textbutton.rect.size)

            bp.Image.__init__(self, textbutton, image=surf, visible=False, layer=textbutton.behind_content)

        def _update_surface_from_resize(self, asked_size):

            self.set_surface(btnimg_manager.get_resized_hover(asked_size))
            self.send_paint_request()

    class Button_LinkImage(bp.Image):

        def __init__(self, textbutton):

            surf = btnimg_manager.default_link
            if surf.get_size() != textbutton.rect.size:
                surf = btnimg_manager.get_resized_window(textbutton.rect.size, color=(0, 0, 0, 63))

            bp.Image.__init__(self, textbutton, image=surf, visible=False, layer=textbutton.above_content)

    STYLE = ButtonWithSound.STYLE.substyle()
    STYLE.modify(
        disable_class=Button_DisableImage,
        focus_class=None,
        hover_class=Button_HoverImage,
        link_class=Button_LinkImage,
        text_class=PE_Button_Text,

        width=140,
        height=40,
        background_color=btnimg_manager.default_color,
        background_image=btnimg_manager.default_background,
        padding=(10, 7, 10, 7),
        text_style={"font_height": 25},
    )

    def __init__(self, parent, *args, translatable=True, text_id=None, **kwargs):

        if text_id is not None:
            kwargs["text"] = lang_manager.get_text_from_id(text_id)

        self.text_id = text_id
        self.is_translatable = translatable
        ButtonWithSound.__init__(self, parent, *args, **kwargs)
        self.__delattr__("text_id")

        surf = btnimg_manager.default_background
        if surf.get_size() != self.rect.size or self.background_color != btnimg_manager.default_color:
            surf = btnimg_manager.get_resized_background(self.rect.size, color=self.background_color)
        self.set_background_image(surf)

        self.original_font_height = self.text_widget.font.height

        self.middle_color = 128 * 3
        self.text_widget2 = None
        if sum(self.background_color[:3]) < self.middle_color:
            self.text_widget2 = bp.Button_Text(self, text=self.text, layer=self.content, font_color="white",
                                               **self.style["text_style"])
            self.text_widget.move(1, 1)
            self.text_widget2.move(0, -1)

        self.true_background_color = self.background_color
        bp.Button.set_background_color(self, (0, 0, 0, 0))

        self.signal.RESIZE.connect(self.handle_resize, owner=self)

    def handle_hover(self):

        with bp.paint_lock:
            self.hover_sail.show()
            self.text_widget.font.config(height=self.original_font_height + 4)
            if self.text_widget2 is not None:
                self.text_widget2.font.config(height=self.original_font_height + 4)

    def handle_resize(self):

        self.set_background_image(btnimg_manager.get_resized_background(self.rect.size,
                                                                        color=self.true_background_color))

    def handle_unhover(self):

        with bp.paint_lock:
            self.hover_sail.hide()
            self.text_widget.font.config(height=self.original_font_height)
            if self.text_widget2 is not None:
                self.text_widget2.font.config(height=self.original_font_height)

    def set_background_color(self, background_color):

        if (sum(background_color) < self.middle_color) != (sum(self.background_color) < self.middle_color):
            bp.LOGGER.warning("A button changes its background_color too much ?")

        self.true_background_color = background_color
        self.set_background_image(btnimg_manager.get_resized_background(self.rect.size, color=background_color))

    def set_text(self, text):

        self.text_widget.set_text(text)
        self.text_widget.fit()


class RegionInfoButton(PE_Button):

    def __init__(self, game, zone=None, **kwargs):

        PE_Button.__init__(self, game.region_info_zone if zone is None else zone, midbottom=(76, 146), **kwargs)


class TransferButton(RegionInfoButton):

    def __init__(self, game, text_id, zone=None):

        RegionInfoButton.__init__(self, game, text_id=text_id, zone=zone, command=game.end_transfer, visible=False)


    def handle_validate(self):

        super().handle_validate()  # end_transfer

        self.scene.region_info_zone.close()
        self.scene.info_boat_zone.close()