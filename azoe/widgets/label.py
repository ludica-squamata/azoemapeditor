from azoe.libs.textrect import render_textrect
from pygame import font, Rect, Surface
from azoe.engine import color
from . import BaseWidget


class Label(BaseWidget):
    texto = ''

    def __init__(self, parent, nombre, x, y, texto='', **opciones):
        if 'colorTexto' not in opciones:
            opciones['colorTexto'] = 'sysElmText'
        if 'colorFondo' not in opciones:
            opciones['colorFondo'] = 'sysElmFace'
        # algo más custom.. esta bien así?
        if 'fontType' not in opciones:
            opciones['fontType'] = 'Verdana'
        if 'fontSize' not in opciones:
            opciones['fontSize'] = 14

        super().__init__(parent, **opciones)
        self.fuente = font.SysFont(opciones['fontType'], opciones['fontSize'])
        self.x, self.y = x, y
        self.nombre = self.parent.nombre + '.Label.' + nombre
        if texto == '':
            self.w, self.h = self.fuente.size(self.texto)
            self.image = Surface((self.w, self.h))
            self.rect = self.image.get_rect(topleft=(self.x, self.y))
        else:
            self.set_text(texto)

    def set_text(self, texto, fgcolor=None, bgcolor=None):
        if fgcolor is None:
            fgcolor = color(self.opciones.get('colorTexto', 'sysElmText'))
        if bgcolor is None:
            bgcolor = color(self.opciones.get('colorFondo', 'sysElmFace'))
        w, h = self.fuente.size(texto)
        rect = Rect(self.x, self.y, w, h + 1)
        self.image = render_textrect(texto, self.fuente, rect, fgcolor, bgcolor)
        self.rect = self.image.get_rect(topleft=(self.x, self.y))
        self.w, self.h = self.image.get_size()