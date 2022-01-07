import pygame as pg
import pygame.draw as dr

from functions import do_nothing
from base_widgets import BaseWidget, Button, Label
from additional_classes import HorAlign, ElementFunctionAtCycle


class TabWidget(BaseWidget):
    def __init__(self, parent, rect, titles, titles_h=40,
                 title_font_size=30,
                 main_color=pg.Color(20, 224, 54),
                 back_color=pg.Color(0, 0, 0)):
        super().__init__(parent, rect)
        self.main_color = main_color
        self.light_main_color = pg.Color(min(self.main_color.r + 90, 255),
                                         min(self.main_color.g + 90, 255),
                                         min(self.main_color.b + 90, 255))
        self.current_color = self.main_color
        self.back_color = back_color

        self.rects_w = 2
        self.bord_rad = 6
        self.text_indent = 10

        self.titles_names = titles
        self.selected_index = 0
        self.titles_h = titles_h
        self.title_font_size = title_font_size
        self.widgets = []
        x, y = self.x + self.bord_rad, self.y
        for i, ttl in enumerate(self.titles_names):
            title_font = pg.font.Font(None, self.title_font_size)
            title = title_font.render(ttl, True, self.main_color)
            w, h = title.get_width() + self.text_indent * 2, self.titles_h
            color = self.light_main_color if i == self.selected_index\
                else self.main_color
            self.widgets.append([[], Button(self.parent, (x, y, w, h), ttl,
                                            font_size=self.title_font_size,
                                            main_color=color,
                                            slot=self.change_selected)])
            x += w + self.rects_w * 2

    def render(self, screen=None):
        screen = screen if screen is not None else self.parent.screen
        dr.rect(screen, self.back_color,
                (self.x, self.y + self.titles_h - self.rects_w // 2,
                 self.w, self.h - self.titles_h + self.rects_w // 2),
                border_radius=self.bord_rad)
        dr.rect(screen, self.main_color,
                (self.x, self.y + self.titles_h - self.rects_w // 2,
                 self.w, self.h - self.titles_h + self.rects_w // 2),
                width=self.rects_w, border_radius=self.bord_rad)
        for i, title in enumerate(self.titles_names):
            self.widgets[i][1].render()
            if i == self.selected_index:
                self.surface = pg.Surface(self.get_surface_size(),
                                          pg.SRCALPHA, 32)
                self.surface.fill(pg.Color(0, 0, 0, 1))
                for widget in self.widgets[i][0]:
                    widget.render(screen=self.surface)
                pg.Surface.blit(screen, self.surface, (self.x,
                                                       self.y + self.titles_h\
                                                       - self.rects_w // 2))

    def process_event(self, event, *args, **kwargs):
        for i, title in enumerate(self.titles_names):
            self.widgets[i][1].process_event(event, i)
            for widget in self.widgets[i][0]:
                widget.process_event(event)

    def change_selected(self, index):
        self.selected_index = index
        self.widgets[self.selected_index][1].set_color(self.light_main_color)
        for i in range(len(self.titles_names)):
            if i != self.selected_index:
                self.widgets[i][1].set_color(self.main_color)

    def get_widgets(self, index):
        return self.widgets[index][0]

    def set_widgets(self, widgets, index):
        tab_widgets = []
        for wid in widgets:
            wid.parent = self
            tab_widgets.append(wid)
        self.widgets[index][0] = tab_widgets

    def add_widget(self, widget, index):
        widget.parent = self
        self.widgets[index][0].append(widget)

    def trans_pos(self, pos):
        return (pos[0] - self.x,
                pos[1] - self.y - self.titles_h + self.rects_w // 2)

    def get_surface_size(self):
        return (self.w, self.h - self.titles_h + self.rects_w // 2)


class ScrollList(BaseWidget):
    def __init__(self, parent, rect, title,
                 title_font_size=50, n_vizible=5,
                 main_color=pg.Color(245, 127, 17),
                 back_color=pg.Color(0, 0, 0),
                 select_func=do_nothing):
        super().__init__(parent, rect)
        self.main_color = main_color
        self.back_color = back_color

        self.select_func = select_func

        self.rects_w = 2
        self.bord_rad = 6
        self.indent = 10
        self.n_vizible = n_vizible

        self.title = title
        self.title_font_size = title_font_size
        self.title_label = Label(self, (self.indent, self.indent,
                                        self.w - 2 * self.indent,
                                        self.title_font_size), self.title,
                                 font_size=self.title_font_size,
                                 main_color=self.main_color,
                                 alignment=HorAlign.CENTER)

        self.elements = []
        self.up_index = None
        self.selected_index = None

    def render(self, screen=None):
        screen = screen if screen is not None else self.parent.screen
        dr.rect(screen, self.back_color, (self.x, self.y, self.w, self.h),
                border_radius=self.bord_rad)
        dr.rect(screen, self.main_color, (self.x, self.y, self.w, self.h),
                width=self.rects_w, border_radius=self.bord_rad)

        surface = pg.Surface((self.w, self.h), pg.SRCALPHA, 32)
        surface.fill(pg.Color(0, 0, 0, 1))
        self.title_label.render(surface)
        if self.up_index is None:
            pg.Surface.blit(screen, surface, (self.x, self.y))
            return

        x, y = self.indent, 2 * self.indent + self.title_label.h
        els = self.elements[self.up_index:self.up_index + self.n_vizible]
        for i, el in enumerate(els):
            if self.up_index + i == self.selected_index:
                el.set_selected(True)
            else:
                el.set_selected(False)
            el.set_coords(x, y)
            el.set_number(self.up_index + i + 1)
            el.render(surface)
            y += self.indent + el.h
        pg.Surface.blit(screen, surface, (self.x, self.y))

    def process_event(self, event, *args, **kwargs):
        if self.up_index is None:
            return
        if event.type == pg.MOUSEWHEEL:
            if pg.mouse.get_pos() in self:
                self.change_up(1 if event.y < 0 else -1)
        if event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1 and\
                            self.trans_pos(event.pos) in self.title_label:
                self.selected_index = None
                self.select_func()
        els = self.elements[self.up_index:self.up_index + self.n_vizible]
        for i, el in enumerate(els):
            try:
                self.elements[self.up_index + i].process_event(event, *args,
                                                               **kwargs)
            except ElementFunctionAtCycle as ex:
                break

    def change_up(self, delta):
        new_index = self.up_index + delta
        if 0 <= new_index < len(self.elements) - self.n_vizible + 1:
            self.up_index = new_index

    def set_elements(self, elements, but_image=None, but_light_image=None,
                     but_slot=do_nothing):
        self.elements = []
        h = (self.h - 3 * self.indent - self.title_label.h) //\
            self.n_vizible - self.indent
        for i, el in enumerate(elements):
            item, info = el
            self.elements.append(ScrollElement(self,
                                               (0, 0, self.w - self.indent * 2,
                                                h), item, but_image=but_image,
                                               but_light_image=but_light_image,
                                               but_slot=but_slot,
                                               information=info,
                                               select_func=self.select_func))
        self.up_index = None if elements == [] else 0
        self.selected_index = None if elements == [] else self.selected_index

    def get_selected_item_info(self):
        if self.get_selected_item_index() is None:
            return
        return self.elements[self.get_selected_item_index()].get_info()

    def get_selected_item_index(self):
        # Защита от удаления элементов:
        if self.selected_index is not None and\
                        self.selected_index >= len(self.elements):
            self.selected_index = None
        return self.selected_index


class ScrollElement(BaseWidget):
    def __init__(self, parent, rect, text_item, font_size=35,
                 but_image=None, but_light_image=None, but_slot=do_nothing,
                 main_color=pg.Color(245, 127, 17),
                 back_color=pg.Color(20, 20, 20), information=None,
                 select_func=do_nothing):
        super().__init__(parent, rect)
        self.text = text_item
        self.font_size = font_size
        self.information = information

        self.but_image = but_image
        self.but_light_image = but_light_image
        self.but_slot = but_slot
        self.select_function = select_func

        self.main_color = self.current_color = main_color
        self.light_main_color = pg.Color(min(self.main_color.r + 90, 255),
                                         min(self.main_color.g + 90, 255),
                                         min(self.main_color.b + 90, 255))
        self.back_color = back_color

        self.indent = 5
        self.rects_w = 3
        self.bord_rad = 0
        self.number = 1
        self.selected = False
        self.button = None

        item_w = self.w - self.h - self.indent * 2
        if self.but_image is not None:
            item_w -= self.h + self.indent * 2
            self.button = Image(self, (self.h + self.indent * 3 + item_w,
                                       self.indent, self.h - self.indent * 2,
                                       self.h - self.indent * 2),
                                self.but_image,
                                light_image=self.but_light_image,
                                slot=self.but_slot)
        self.item_label = Label(self, (self.h + 2 * self.indent, self.indent,
                                       item_w, self.h - self.indent * 2),
                                self.text, main_color=self.current_color,
                                 back_color=self.back_color,
                                font_size=self.font_size)
        self.num_label = Label(self, (self.indent, self.indent,
                                      self.h - self.indent * 2,
                                      self.h - self.indent * 2),
                                str(self.number),
                                main_color=self.current_color,
                                back_color=self.back_color,
                                alignment=HorAlign.CENTER,
                                font_size=self.font_size)

    def render(self, screen=None, index=0):
        screen = screen if screen is not None else self.parent.screen
        dr.rect(screen, self.back_color, (self.x, self.y, self.w, self.h),
                border_radius=self.bord_rad)
        dr.rect(screen, self.current_color, (self.x, self.y, self.w, self.h),
                width=self.rects_w, border_radius=self.bord_rad)

        surface = pg.Surface((self.w, self.h), pg.SRCALPHA, 32)
        surface.fill(pg.Color(0, 0, 0, 1))
        dr.ellipse(surface, self.current_color, (self.indent, self.indent,
                                                 self.h - self.indent * 2,
                                                 self.h - self.indent * 2),
                   width=self.rects_w)
        self.num_label.render(surface)
        self.item_label.render(surface)
        if self.button is not None:
            self.button.render(surface)
        pg.Surface.blit(screen, surface, (self.x, self.y))

    def set_selected(self, bool_obj):
        self.selected = bool_obj
        color = self.light_main_color if self.selected\
            else self.main_color
        self.current_color = color
        self.num_label.set_color(self.current_color)
        self.item_label.set_color(self.current_color)

    def get_info(self):
        return self.information

    def set_number(self, num):
        self.number = num
        self.num_label.set_text(str(self.number))

    def process_event(self, event, *args, **kwargs):
        if event.type == pg.MOUSEBUTTONDOWN:
            if self.parent.trans_pos(event.pos) in self and event.button == 1:
                self.parent.selected_index = self.number - 1
                self.select_function()
        if self.button is None:
            return
        if event.type == pg.MOUSEMOTION:
            if self.trans_pos(self.parent.trans_pos(event.pos)) in self.button:
                self.button.current_image = self.button.light_image
            else:
                self.button.current_image = self.button.image
        if event.type == pg.MOUSEBUTTONDOWN:
            if self.trans_pos(self.parent.trans_pos(event.pos)) in\
                    self.button and event.button == 1:
                self.button.slot()
                raise ElementFunctionAtCycle
