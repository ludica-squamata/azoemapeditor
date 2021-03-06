from azoe.widgets import BaseWidget
from pygame import Surface, mouse


class BaseLinea(BaseWidget):
    pressed = False
    locked = False
    w, h = 0, 0

    def __init__(self, parent, idx):
        super().__init__(parent)
        self.nombre = self.parent.nombre + '.LineaGuia'
        self.idx = idx
        self.x, self.y = self.parent.x, self.parent.y
        self.base_x, self.base_y = self.x, self.y
        self.image = self._crear(self.w, self.h)
        self.rect = self.image.get_rect(topleft=(self.x, self.y))

    @staticmethod
    def _crear(w, h):
        img = Surface((w, h))
        img.fill((120, 255, 255))
        return img

    def on_mouse_down(self, button):
        self.pressed = True

    def on_mouse_up(self, button):
        self.pressed = False

    def on_mouse_out(self):
        if not self.pressed:
            super().on_mouse_out()

    def desplazar(self):
        pass

    def update(self):
        if self.pressed and not self.locked:
            self.desplazar()


class LineaGuiaX(BaseLinea):
    lin = 'x'

    def __init__(self, parent, idx):
        self.w, self.h = parent.w, 1
        super().__init__(parent, idx)
        self.nombre += '.W:' + str(self.idx)
        self.parent.guias.append(self)

    def desplazar(self):
        x, y = mouse.get_pos()
        if y > self.base_y:
            self.rect.y = y

    def scroll(self, dy):
        self.rect.move_ip(0, dy)
        self.dirty = 1


class LineaGuiaY(BaseLinea):
    lin = 'y'

    def __init__(self, parent, idx):
        self.w, self.h = 1, parent.h
        super().__init__(parent, idx)
        self.nombre += '.H:' + str(self.idx)
        self.parent.guias.append(self)

    def desplazar(self):
        x, y = mouse.get_pos()
        if x > self.base_x:
            self.rect.x = x

    def scroll(self, dx):
        self.rect.move_ip(dx, 0)
        self.dirty = 1
