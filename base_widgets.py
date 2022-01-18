import pygame as pg
import pygame.draw as dr
import pygame.sprite as spr
import pygame.transform as tr
import pygame.font as fnt

from functions import do_nothing, get_width, load_image, get_max_font_size,\
    get_coords_from_align, get_max_text_string, get_light_color
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
        pass

    def update(self, key, event=None, screen=None):
        if key == BaseWidget.EVENT_PROCESSING:
            self.process_event(event)
        if key == BaseWidget.RENDER:
            self.render(screen)

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


class PushButton(BaseWidget):
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
        self.light_main_color = get_light_color(self.main_color,
                                                self.light_delta)
        self.current_color = self.main_color
        self.back_color = back_color

        self.text = text
        self.font_size = font_size if font_size < self.h - 2 * self.indent\
            else get_max_font_size(self.text, self.w - 2 * self.indent,
                                   self.h - 2 * self.indent,
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
        font = fnt.Font(None, self.font_size)
        text = font.render(self.text, True, self.current_color)
        x, y = get_coords_from_align(self.alignment, self.w - 2 * self.indent,
                                     self.h - 2 * self.indent,
                                     text.get_width(), text.get_height(),
                                     start_x=self.x + self.indent,
                                     start_y=self.y + self.indent)
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
        self.light_main_color = get_light_color(self.main_color,
                                                self.light_delta)

    def set_slot(self, slot):
        self.slot = slot

    def set_text(self, text):
        self.text = text

    def set_light_delta(self, delta):
        self.light_delta = delta
        self.set_color(self.main_color)

    def set_indent(self, indent):
        self.indent = indent
        self.font_size = self.font_size\
            if self.font_size < self.h - 2 * self.indent\
            else get_max_font_size(self.text, self.w - 2 * self.indent,
                                   self.font_size)

    def set_border(self, border_w):
        self.border_w = border_w


class Image(BaseWidget):
    def __init__(self, parent, rect, image,
                 border_color=None, light_image=None,
                 key=None, modifier=None, slot=do_nothing):
        super().__init__(parent, rect)
        self.border_w = 2
        self.light_delta = 90

        self.image = self.current_image = tr.scale(image, (self.w, self.h))
        self.light_image = light_image if light_image is None\
            else tr.scale(light_image, (self.w, self.h))

        self.key = key
        self.modifier = modifier
        self.slot = slot

        self.main_color = self.current_color = border_color
        self.light_main_color = get_light_color(self.main_color,
                                                self.light_delta)\
            if self.main_color is not None else None

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
        self.image = self.current_image = tr.scale(image, (self.w, self.h))

    def set_light_image(self, image):
        self.light_image = image if image is None\
            else tr.scale(image, (self.w, self.h))

    def set_color(self, color=None):
        self.main_color = self.current_color = color
        self.light_main_color = get_light_color(self.main_color,
                                                self.light_delta)\
            if self.main_color is not None else None

    def set_slot(self, slot):
        self.slot = slot


class Label(BaseWidget):
    def __init__(self, parent, rect, text, main_color=pg.Color(247, 180, 10),
                 back_color=pg.Color(0, 0, 0), font_size=20, font_obj=None,
                 border=False, alignment=Align.LEFT & Align.TOP):
        super().__init__(parent, rect)
        self.indent = 5
        self.text_indent = 4
        self.border_w = 2
        self.text_strings = text.split('\n')
        self.alignment = alignment
        self.main_color = main_color
        self.back_color = back_color
        self.border = border

        max_string = get_max_text_string(self.text_strings)
        string_h = (self.h - 2 * self.indent - (len(self.text_strings) - 1) *
                    self.text_indent) // len(self.text_strings)
        self.font_size = get_max_font_size(max_string, self.w - 2 * self.indent,
                                           string_h, font_size)
        self.start_font_size = self.font_size
        self.font_obj = font_obj
        self.font = fnt.Font(self.font_obj, self.start_font_size)

        self.text_h = (len(self.text_strings) - 1) * self.text_indent +\
                      len(self.text_strings) * self.font.size(max_string)[1]
        self.text_w = self.font.size(max_string)[0]

    def render(self, screen=None):
        screen = screen if screen is not None else self.parent.screen
        if self.border:
            dr.rect(screen, self.back_color, self.rect)
            dr.rect(screen, self.main_color, self.rect, width=self.border_w)
        self.surface = pg.Surface((self.text_w, self.text_h), pg.SRCALPHA, 32)
        self.surface.fill(pg.Color(0, 0, 0, 1))
        x, y = 0, 0
        for text in self.text_strings:
            text = self.font.render(text, True, self.main_color)
            x1, y1 = get_coords_from_align(self.alignment, self.text_w,
                                           text.get_height(),
                                           text.get_width(), text.get_height(),
                                           start_x=x, start_y=y)
            self.surface.blit(text, (x1, y1))
            y += self.text_indent + text.get_height()
        x, y = self.get_text_coords()
        pg.Surface.blit(screen, self.surface, (self.x + x, self.y + y))

    def set_text(self, text):
        self.text_strings = text.split('\n')
        max_string = get_max_text_string(self.text_strings)
        string_h = (self.h - 2 * self.indent - (len(self.text_strings) - 1) *
                    self.text_indent) // len(self.text_strings)
        self.font_size = get_max_font_size(max_string, self.w - 2 * self.indent,
                                           string_h, self.start_font_size)
        self.font = fnt.Font(self.font_obj, self.font_size)
        self.text_h = (len(self.text_strings) - 1) * self.text_indent +\
                      len(self.text_strings) * self.font.size(max_string)[1]
        self.text_w = self.font.size(max_string)[0]

    def set_color(self, color):
        self.main_color = color

    def set_font(self, f_size=None, f_obj=None):
        self.start_font_size = f_size if f_size is not None\
            else self.start_font_size
        self.font_obj = f_obj if f_obj is not None else self.font_obj
        self.set_text('\n'.join(self.text_strings))

    def get_text_size(self):
        return self.text_w, self.text_h

    def get_text_coords(self):
        return get_coords_from_align(self.alignment, self.w - 2 * self.indent,
                                     self.h - 2 * self.indent,
                                     self.text_w, self.text_h,
                                     start_x=self.indent,
                                     start_y=self.indent)


class LineEdit(BaseWidget):
    def __init__(self, parent, rect, text='', font_size=40,
                 color=pg.Color(222, 18, 178), back_color=pg.Color(0, 0, 0),
                 alignment=Align.LEFT, cursor_period=30):
        super().__init__(parent, rect)
        self.indent = 5
        self.border_w = 2
        self.light_delta = 90
        # Cursor:
        self.delta = -1
        self.start_cursor_period = self.cursor_period = cursor_period

        self.text = text
        self.start_font_size = font_size
        self.alignment = alignment

        self.current_color = self.main_color = color
        self.light_main_color = get_light_color(self.main_color,
                                                self.light_delta)
        self.back_color = back_color

        self.label = Label(self.parent, self.rect, self.text,
                           self.current_color, font_size=self.start_font_size,
                           alignment=self.alignment)

        self.active = False
        self.draw_cursor = False


    def process_event(self, event, *args, **kwargs):
        if event.type == pg.MOUSEBUTTONDOWN:
            if event.pos in self and event.button == 1:
                self.active = True
            elif event.pos not in self and event.button == 1:
                self.active = False
            self.current_color = self.light_main_color if self.active\
                else self.main_color
            self.label.set_color(self.current_color)
        if event.type == pg.KEYDOWN and self.active:
            if event.key == pg.K_BACKSPACE:
                self.set_text(self.text[:-1])
            else:
                symbol = event.unicode
                if symbol.isprintable():
                    self.set_text(self.text + symbol)

    def render(self, screen=None):
        screen = screen if screen is not None else self.parent.screen
        pg.draw.rect(screen, self.back_color, self.rect)
        pg.draw.rect(screen, self.current_color, self.rect, self.border_w)
        self.label.render()
        text_width, text_height = self.label.get_text_size()
        x, y = self.label.get_text_coords()
        x += self.x
        y += self.y
        if self.active and self.draw_cursor:
            dr.line(screen, self.current_color,
                    (x + text_width, y), (x + text_width, y + text_height),
                    self.border_w)
        self.cursor_period += self.delta
        if self.cursor_period <= 0 or\
                        self.cursor_period >= self.start_cursor_period:
            self.draw_cursor = not self.draw_cursor
            self.delta *= -1

    def get_text(self):
        return self.text

    def set_text(self, text):
        self.text = text
        self.label.set_text(self.text)
        self.label.set_font(self.start_font_size)
