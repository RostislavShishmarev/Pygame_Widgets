import pygame as pg
import pygame.draw as dr
import pygame.sprite as spr
import pygame.transform as tr

from functions import do_nothing, get_width, load_image, get_max_font_size,\
    get_coords_from_align
from additional_classes import Align


class BaseWidget(spr.Sprite):
    EVENT_PROCESSING = 'event'
    RENDER = 'render'

    def __init__(self, parent, rect):
        super().__init__()
        self.parent = parent
        x, y, w, h = rect
        self.rect = pg.Rect(*rect)
        self.x, self.y, self.x1, self.y1 = x, y, x + w, y + h
        self.w, self.h = w, h

    def render(self, screen=None):
        pass

    def __contains__(self, coords):
        return self.rect.collidepoint(coords)

    def process_event(self, event, *args, **kwargs):
        # В args и kwargs передаются аргументы, которые нужно передать слоту
        pass

    def update(self, key, event=None):
        if key == BaseWidget.EVENT_PROCESSING:
            self.process_event(event)
        if key == BaseWidget.RENDER:
            self.render()

    def set_rect(self, x=None, y=None, w=None, h=None):
        if x is not None:
            self.set_x(x)
        if y is not None:
            self.set_y(y)
        if w is not None:
            self.set_w(w)
        if h is not None:
            self.set_h(h)

    def set_x(self, x):
        self.x = x
        self.rect.x = x
        self.x1 = self.x + self.w

    def set_y(self, y):
        self.y = y
        self.rect.y = y
        self.y1 = self.y + self.h

    def set_w(self, w):
        self.w = w
        self.rect.w = w
        self.x1 = self.x + w

    def set_h(self, h):
        self.h = h
        self.rect.h = h
        self.y1 = self.y + h


class Window(BaseWidget):
    def __init__(self, width, height, caption='Window', logo_name=None,
                 background_color=pg.Color(0, 0, 0), fps=60):
        super().__init__(None, (0, 0, width, height))
        self.size = (self.w, self.h)
        self.fps = fps
        self.caption = caption
        self.logo_name = logo_name
        self.background_color = background_color

        self.cursor_group = spr.Group()
        self.widgets_group = spr.Group()
        self.cursor_name = None
        self.new_window_after_self = None

        self.runned = False
        self.running = True

    def run(self):
        self.runned = True
        pg.init()
        clock = pg.time.Clock()
        pg.display.set_caption(self.caption)
        self.screen = pg.display.set_mode(self.size)
        if self.logo_name is not None:
            pg.display.set_icon(load_image(self.logo_name))
        self.code_before_game_cycle()  # USER CODE
        if self.cursor_name is not None:
            pg.mouse.set_visible(False)
            self.cursor = spr.Sprite(self.cursor_group)
            self.cursor.image = load_image(self.cursor_name)
            self.cursor.rect = self.cursor.image.get_rect()
        while self.running:
            for event in pg.event.get():
                self.widgets_group.update(BaseWidget.EVENT_PROCESSING,
                                          event=event)
                if event.type == pg.QUIT:
                    self.running = False
                    self.exit()
                self.code_in_event_cycle(event)  # USER CODE
                if event.type == pg.MOUSEMOTION and\
                                self.cursor_name is not None:
                    self.cursor.rect.topleft = event.pos
            self.code_before_render()  # USER CODE
            self.screen.fill(self.background_color)
            self.widgets_group.update(BaseWidget.RENDER)
            self.code_in_render()
            if pg.mouse.get_focused() and self.cursor_name is not None:
                self.cursor_group.draw(self.screen)
            self.code_after_render()  # USER CODE
            clock.tick(self.fps)
            pg.display.flip()
        self.code_after_game_cycle()  # USER CODE
        pg.quit()
        if self.new_window_after_self is not None:
            self.new_window_after_self.run()

    def exit(self):
        pass

    def set_caption(self, caption):
        self.caption = caption
        if self.runned:
            pg.display.set_caption(caption)

    def set_window_after_self(self, window):
        self.new_window_after_self = window

    def set_cursor(self, image_name):
        self.cursor_name = image_name
        if self.runned and self.cursor_name is not None:
            pos = pg.mouse.get_pos()
            self.cursor.kill()
            self.cursor = spr.Sprite(self.cursor_group)
            self.cursor.image = load_image(self.cursor_name)
            self.cursor.rect = self.cursor.image.get_rect()
            self.cursor.rect.topleft = pos

    def set_logo(self, image_name):
        self.logo_name = image_name
        if self.runned and self.logo_name is not None:
            pg.display.set_icon(load_image(self.logo_name))

    def set_fps(self, fps):
        self.fps = fps

    def add_widgets(self, *widgets):
        self.widgets_group.add(*widgets)

    def remove_widgets(self, *widgets):
        self.widgets_group.remove(*widgets)

    def code_before_game_cycle(self):
        pass

    def code_in_event_cycle(self, event):
        pass

    def code_before_render(self):
        pass

    def code_in_render(self):
        pass

    def code_after_render(self):
        pass

    def code_after_game_cycle(self):
        pass


class Button(BaseWidget):
    def __init__(self, parent, rect, text, font_size=40,
                 main_color=pg.Color(70, 202, 232),
                 back_color=pg.Color(0, 0, 0), slot=do_nothing,
                 key=None, modifier=None, alignment=Align.CENTER):
        super().__init__(parent, rect)
        self.slot = slot
        self.border_w = 2
        self.light_delta = 90
        self.indent = 5

        self.main_color = main_color
        self.light_main_color = pg.Color(min(self.main_color.r +\
                                             self.light_delta, 255),
                                         min(self.main_color.g +\
                                             self.light_delta, 255),
                                         min(self.main_color.b +\
                                             self.light_delta, 255))
        self.current_color = self.main_color
        self.back_color = back_color

        self.text = text
        self.font_size = font_size if font_size < self.h - 2 * self.indent\
            else get_max_font_size(self.text, self.w - 2 * self.indent,
                                   font_size)
        self.alignment = alignment

        self.key = key
        self.modifier = modifier

    def render(self, screen=None):
        screen = screen if screen is not None else self.parent.screen
        dr.rect(screen, self.back_color,
                (self.x, self.y, self.w, self.h))
        dr.rect(screen, self.current_color,
                (self.x, self.y, self.w, self.h), width=self.border_w)
        font = pg.font.Font(None, self.font_size)
        text = font.render(self.text, True, self.current_color)
        x, y = get_coords_from_align(self.alignment, self.w, self.h,
                                     text.get_width(), text.get_height(),
                                     x_indent=self.indent,
                                     y_indent=self.indent, start_x=self.x,
                                     start_y=self.y)
        screen.blit(text, (x, y))

    def process_event(self, event, *args, **kwargs):
        if event.type == pg.MOUSEBUTTONDOWN:
            if event.pos in self and event.button == 1:
                self.slot(*args, **kwargs)
        if event.type == pg.KEYDOWN and self.key is not None:
            if event.key == self.key:
                if self.modifier is not None:
                    if event.mod & self.modifier:
                        self.slot(*args, **kwargs)
                else:
                    self.slot(*args, **kwargs)
        if event.type == pg.MOUSEMOTION:
            if event.pos in self:
                self.current_color = self.light_main_color
            else:
                self.current_color = self.main_color

    def set_color(self, color):
        self.main_color = self.current_color = color
        func = min if self.light_delta >= 0 else max
        value = 255 if self.light_delta >= 0 else 0
        self.light_main_color = pg.Color(func(self.main_color.r +\
                                              self.light_delta, value),
                                         func(self.main_color.g +\
                                              self.light_delta, value),
                                         func(self.main_color.b +\
                                              self.light_delta, value))

    def set_slot(self, slot):
        self.slot = slot

    def set_text(self, text):
        self.text = text

    def set_light_delta(self, delta):
        self.light_delta = delta
        self.set_color(self.main_color)


class Image(BaseWidget):
    def __init__(self, parent, rect, image, proportional=False,
                 bord_color=None, light_image=None,
                 key=None, modifier=None, slot=do_nothing):
        super().__init__(parent, rect)
        if proportional:
            self.w = get_width(image, self.h)

        self.image = self.current_image = tr.scale(image, (self.w, self.h))
        self.light_image = light_image if light_image is None\
            else tr.scale(light_image, (self.w, self.h))

        self.key = key
        self.modifier = modifier
        self.slot = slot

        self.main_color = bord_color
        self.light_main_color = pg.Color(min(self.main_color.r + 90, 255),
                                         min(self.main_color.g + 90, 255),
                                         min(self.main_color.b + 90, 255))\
            if self.main_color is not None else None
        self.current_color = self.main_color
        self.border_w = 2

    def render(self, screen=None):
        screen = screen if screen is not None else self.parent.screen
        pg.Surface.blit(screen, self.current_image, (self.x, self.y))
        if self.current_color is not None:
            dr.rect(screen, self.current_color,
                    (self.x, self.y, self.w, self.h), width=self.border_w)

    def process_event(self, event, *args, **kwargs):
        if event.type == pg.MOUSEBUTTONDOWN:
            if event.pos in self and event.button == 1:
                self.slot(*args, **kwargs)
        if event.type == pg.KEYDOWN and self.key is not None:
            if event.key == self.key:
                if self.modifier is not None:
                    if event.mod & self.modifier:
                        self.slot(*args, **kwargs)
                else:
                    self.slot(*args, **kwargs)
        if event.type == pg.MOUSEMOTION and self.light_image is not None:
            if event.pos in self:
                self.current_image = self.light_image
                self.current_color = self.light_main_color
            else:
                self.current_image = self.image
                self.current_color = self.main_color

    def set_image(self, image):
        self.image = self.current_image = image

    def set_color(self, color=None):
        self.main_color = self.current_color = color
        self.light_main_color = pg.Color(min(self.main_color.r + 90, 255),
                                         min(self.main_color.g + 90, 255),
                                         min(self.main_color.b + 90, 255))\
            if self.main_color is not None else None

    def set_slot(self, slot):
        self.slot = slot


class Label(BaseWidget):
    def __init__(self, parent, rect, text, main_color=pg.Color(247, 180, 10),
                 back_color=pg.Color(0, 0, 0), font_size=20, border=False,
                 alignment=Align.LEFT, indent=5):
        super().__init__(parent, rect)
        self.text = text
        self.font_size = font_size
        self.alignment = alignment
        self.indent = indent
        self.main_color = main_color
        self.back_color = back_color
        self.border = border
        self.border_w = 2

    def render(self, screen=None):
        screen = screen if screen is not None else self.parent.screen
        if self.border:
            dr.rect(screen, self.back_color, (self.x, self.y, self.w, self.h))
            dr.rect(screen, self.main_color, (self.x, self.y, self.w, self.h),
                    width=self.border_w)
        font = pg.font.Font(None, self.font_size)
        text = font.render(self.text, True, self.main_color)
        if self.alignment == Align.LEFT:
            x = self.x + self.indent
        elif self.alignment == Align.CENTER:
            x = self.x + self.w // 2 - text.get_width() // 2
        elif self.alignment == Align.RIGHT:
            x = self.x + self.w - self.indent
        else:
            return
        screen.blit(text, (x, self.y + self.h // 2 - text.get_height() // 2))

    def set_text(self, text):
        self.text = text

    def set_color(self, color):
        self.main_color = color

    def set_font_size(self, font_size):
        self.font_size = font_size
