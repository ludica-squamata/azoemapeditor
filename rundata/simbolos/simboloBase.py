from azoe.widgets import BaseWidget
from pygame import mouse, PixelArray


class SimboloBase(BaseWidget):
    img_pos = None  # imagen normal
    img_neg = None  # imagen semitransparente
    img_sel = None  # imagen seleccionada
    img_cls = None  # imagen de colisiones
    cls_code = None  # codigo de imagen de colisiones comprimida
    pressed = False
    context = None

    def __init__(self, parent, data):
        super().__init__(parent)

        self.data = data
        if len(data['pos']) == 3:
            self.x, self.y, self.z = self.data['pos']
        else:
            self.x, self.y, self.z, self.curr_rot = self.data['pos']
        self._nombre = self.data['nombre']
        self.nombre = self.parent.nombre + '.Simbolo.' + self._nombre
        self._imagen = self.data['image']
        self.w, self.h = self._imagen.get_size()
        self.rect = self._imagen.get_rect(topleft=(self.x, self.y))
        self.px, self.py = self.rect.topleft

    def on_mouse_up(self, button):
        if button == 1:
            self.pressed = False

    def _arrastrar(self):
        abs_x, abs_y = mouse.get_pos()
        new_x, new_y = abs_x - self.x, abs_y - self.y

        dx = new_x - self.px
        dy = new_y - self.py

        return dx, dy

    def get_real_name(self):
        return self._nombre

    def mover(self, dx=0, dy=0):
        self.rect.move_ip(dx, dy)
        self.x += dx
        self.y += dy
        self.dirty = 1

    def on_mouse_down(self, button):
        if button == 1:
            self.pressed = True
            x, y = mouse.get_pos()
            self.px = x - self.x
            self.py = y - self.y
        elif button == 3:
            self.context.show()

    def on_mouse_out(self):
        super().on_mouse_out()
        self.pressed = False

    @staticmethod
    def hide_menu():
        print('dummy')

    @staticmethod
    def _crear_transparencia(imagen):
        px_array = PixelArray(imagen.copy())
        for y in range(imagen.get_height()):
            for x in range(imagen.get_width()):
                _color = imagen.unmap_rgb(px_array[x, y])
                if _color.a == 255:
                    _color.a = 200
                px_array[x, y] = _color
        return px_array.make_surface()
