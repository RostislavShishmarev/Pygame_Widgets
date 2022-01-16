import pygame as pg
from additional_classes import Align, NotAlignmentError


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


def get_max_font_size(text, w, h, start_font=200):
    while True:
        text_font = pg.font.Font(None, start_font)
        text_sc = text_font.render(text, True, pg.Color(0, 0, 0))
        if text_sc.get_width() < w and text_sc.get_height() < h:
            return start_font
        start_font -= 1


def get_coords_from_align(alignment, parent_w, parent_h, item_w, item_h,
                          start_x=0, start_y=0):
    #print(alignment, alignment.aligns)
    if alignment == Align.LEFT:
        x = 0
    elif alignment == Align.RIGHT:
        x = parent_w - item_w
    elif alignment == Align.CENTER:
        x = parent_w // 2 - item_w // 2
    else:
        raise NotAlignmentError('Argument is not an Align object')
    if alignment == Align.TOP:
        y = 0
    elif alignment == Align.BOTTOM:
        y = parent_h - item_h
    elif alignment == Align.CENTER:
        y = parent_h // 2 - item_h // 2
    else:
        raise NotAlignmentError('Argument is not an Align object')
    return (start_x + x, start_y + y)


def get_max_text_string(strings):
    return max(strings, key=lambda x:\
        pg.font.Font(None, 50).render(x, True, pg.Color(0, 0, 0)).get_width())
