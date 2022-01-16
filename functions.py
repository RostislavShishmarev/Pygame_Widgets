import pygame as pg
from additional_classes import Align


def load_image(name, color_key=None):
    try:
        image = pg.image.load(name)
    except pg.error as message:
        raise SystemExit(message)

    if color_key is not None:
        image = image.convert()
        color_key = image.get_at((0, 0)) if color_key == -1 else color_key
        image.set_colorkey(color_key)
    else:
        image = image.convert_alpha()
    return image


def do_nothing(*args, **kwargs):
    pass


def get_width(surface, height):
    return round(surface.get_size()[0] * (height / surface.get_size()[1]))


def get_height(surface, width):
    return round(surface.get_size()[1] * (width / surface.get_size()[0]))


def get_max_font_size(text, w, start_font=200):
    while True:
        text_font = pg.font.Font(None, start_font)
        text_sc = text_font.render(text, True, pg.Color(0, 0, 0))
        if text_sc.get_width() < w:
            return start_font
        start_font -= 1


def get_coords_from_align(alignment, parent_w, parent_h, item_w, item_h,
                          x_indent=5, y_indent=5, start_x=0, start_y=0):
    #print(alignment, alignment.aligns)
    if alignment == Align.LEFT:
        x = x_indent
    elif alignment == Align.RIGHT:
        x = parent_w - x_indent - item_w
    else:
        x = parent_w // 2 - item_w // 2
    if alignment == Align.TOP:
        y = y_indent
    elif alignment == Align.BOTTOM:
        y = parent_h - y_indent - item_h
    else:
        y = parent_h // 2 - item_h // 2
    return (start_x + x, start_y + y)


