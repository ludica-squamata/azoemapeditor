from pygame import mouse, K_RIGHT, K_LEFT, K_UP, K_DOWN, K_DELETE, Surface
from globales import Sistema, LAYER_FONDO, LAYER_COLISIONES
from .simboloBase import SimboloBase
from azoe.widgets import ContextMenu


class SimboloCNVS(SimboloBase):
    selected = False
    isMoving = False
    dx, dy = 0, 0

    def __init__(self, parent, data):
        super().__init__(parent, data)

        self.grupo = self.data['grupo']
        self.tipo = self.data['tipo']
        self.index = self.data['index']
        self.ruta = self.data['ruta']
        self.rot = self.data.get('rot', 0)

        self.img_pos = self._imagen.copy()
        self.img_neg = self._crear_transparencia(self._imagen.copy())
        self.img_cls = self.crear_img_cls(self.data['colisiones'])
        self.img_sel = self.crear_img_sel(self._imagen.copy())
        self.image = self.img_pos

        comandos = [
            {'nom': 'Subir', 'cmd': lambda: self.change_layer(+1)},
            {'nom': 'Bajar', 'cmd': lambda: self.change_layer(-1)},
            {'nom': 'barra'},
            {'nom': 'Cortar', 'cmd': Sistema.cortar, 'icon': Sistema.iconos['cortar']},
            {'nom': 'Copiar', 'cmd': Sistema.copiar, 'icon': Sistema.iconos['copiar']},
        ]
        self.context = ContextMenu(self, comandos)

    def copiar(self):
        datos = self.data.copy()
        datos['rect'] = self.rect.copy()
        return datos

    def estado(self):
        at = ' @ (' + str(self.rect.x) + ',' + str(self.rect.y) + ',' + str(self.z) + ')'
        return self.tipo + ' ' + self.get_real_name() + ' #' + str(self.index) + at

    @staticmethod
    def crear_img_sel(imagebase):
        over = imagebase.copy()
        over.fill((0, 0, 100), special_flags=1)
        return over

    def crear_img_cls(self, imagebase):
        if imagebase is not None:
            return imagebase
        else:
            img = Surface(self.img_pos.get_size())
            img.set_alpha(0)
            return img

    def on_mouse_down(self, button):
        if button == 1:
            self.on_focus_in()
            self.img_sel = self.crear_img_sel(self._imagen.copy())
            if not self.selected:
                self.ser_elegido()
            self.pressed = True
            x, y = mouse.get_pos()
            self.px = x - self.x
            self.py = y - self.y

        elif button == 3:
            if not self.selected:
                self.ser_elegido()
            self.context.show()

    def on_key_down(self, tecla, shift=False):
        if self.selected:
            x, y = 0, 0

            if tecla == K_DELETE:
                self.delete()
            elif tecla == K_RIGHT:
                x = +1
            elif tecla == K_LEFT:
                x = -1
            elif tecla == K_DOWN:
                y = +1
            elif tecla == K_UP:
                y = -1

            if shift:
                x *= 10
                y *= 10
            self.mover(x, y)

    def on_key_up(self, tecla):
        if tecla == K_RIGHT or tecla == K_LEFT:
            self.dx = 0
        elif tecla == K_DOWN or tecla == K_UP:
            self.dy = 0

    def mover(self, dx=0, dy=0):
        self.isMoving = True
        super().mover(dx, dy)

    def delete(self):
        self.parent.del_tile(self)
        if self in Sistema.selected:
            Sistema.selected.remove(self)

    def change_layer(self, mod):
        self.parent.cambiar_layer(self, mod)
        self.z += mod
        Sistema.estado = self.estado()

    def ser_elegido(self):
        self.selected = True
        Sistema.selected.append(self)
        self.image = self.img_sel
        # Sistema.estado = self.estado()

    def ser_deselegido(self):
        self.selected = False
        if self in Sistema.selected:
            Sistema.selected.remove(self)

    def update(self):
        self.isMoving = False
        if Sistema.capa_actual == LAYER_COLISIONES:
            self.image = self.img_cls

        elif Sistema.capa_actual == LAYER_FONDO:
            if self.selected:
                self.image = self.img_sel
                if self.pressed:
                    dx, dy = self._arrastrar()
                    if (dx, dy) != (0, 0):
                        self.mover(dx, dy)
                    self.dx, self.dy = dx, dy
            else:
                self.image = self.img_pos
        self.dirty = 1
