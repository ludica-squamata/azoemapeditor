from azoe.engine import abrir_json, cargar_iconos, guardar_imagen, cargar_imagen, split_spritesheet, guardar_json
from azoe.engine.RLE import decode, descomprimir, deserialize
from azoe.engine import EventHandler, Portapapeles
from .constantes import LAYER_FONDO, C
from pygame.sprite import DirtySprite
from pygame import quit as py_quit
from sys import exit as sys_exit
from .mapa import Proyecto
from os import getcwd

__all__ = ['Sistema']


class Sistema:
    PROYECTO = None
    estado = ''
    referencias = {'fondo': None, 'colisiones': None,
                   'props': None, 'mobs': None, 'ambiente': None}
    KeyCombinations = []
    key_bindings = None
    binded_methods = None
    capa_actual = None
    selected = None
    preferencias = {}
    Guardado = None
    iconos = []
    fdProyectos = getcwd() + '\\proyectos'
    fdAssets = getcwd() + '\\assets'
    fdExport = getcwd() + '\\export'
    fdLibs = getcwd() + '\\libs'
    DiagBox = None
    DiagMODE = False
    DiagBoxes_repeat = {}

    @classmethod
    def init(cls):
        cls.iconos = cls.cargar_iconos()
        cls.capa_actual = LAYER_FONDO
        cls.key_bindings = {}
        cls.binded_methods = {}
        cls.selected = []
        keybindings = abrir_json('config/config.json')['keybindings']
        for command in keybindings:
            if hasattr(Sistema, command):
                if command == 'save_project':
                    cls.key_bindings[keybindings[command]] = lambda: cls.save_project(cls.Guardado)
                    cls.binded_methods[command] = keybindings[command]
                else:
                    cls.key_bindings[keybindings[command]] = getattr(Sistema, command)
                    cls.binded_methods[command] = keybindings[command]

    @staticmethod
    def cargar_iconos():
        nombres = 'nuevo,abrir,guardar,cortar,copiar,pegar,grilla,grilla_tog,guardar_dis,cortar_dis,copiar_dis,'
        nombres += 'pegar_dis,grilla_dis,mob,prop,borrar,ver_cls,ver_fondo,ver_dis,mob_dis,prop_dis,borrar_dis,'
        nombres += 'fondo,fondo_dis'
        nombres = nombres.split(',')
        ruta = getcwd() + '/config/iconos.png'
        return cargar_iconos(nombres, ruta, 19, 17)

    @classmethod
    def set_ruta_fondo(cls, ruta=None):
        from azoe.widgets import FileOpenDialog
        if ruta is None:
            FileOpenDialog(cls.set_ruta_fondo, cls.fdAssets, ft=['.png'])
        else:
            try:
                canvas = EventHandler.get_widget('Grilla.Canvas')
                canvas.set_bg_image(BackgroundImage(ruta))
                # cls.PROYECTO.script["fondo"] = ruta
                cls.capa_actual = LAYER_FONDO
                cls.estado = ''
            except IOError:
                cls.estado = 'No se ha selecionado una imagen válida'

    @classmethod
    def save_collition_map(cls, ruta=None):
        from azoe.widgets import FileSaveDialog
        if ruta is None:
            FileSaveDialog(cls.save_collition_map, cls.fdExport, ft=['*.png'])

        else:
            imagen = EventHandler.get_widget('Grilla.Canvas').render()
            guardar_imagen(imagen, ruta)
            cls.estado = 'Imagen ' + ruta + ' guardada exitosamente'
            cls.PROYECTO.script['colisiones'] = ruta

    @classmethod
    def new_project(cls, data=None):
        from rundata.menus.cuadros import CuadroMapa
        if data is None:
            CuadroMapa('Nuevo Mapa')

        elif cls.PROYECTO is not None:
            cls.referencias.update(data)

        else:
            cls.close_project()
            cls.referencias.update(data)
            cls.habilitar_todo(True)
            # cls.PROYECTO = Proyecto(data)

    @classmethod
    def open_project(cls, ruta=None):
        from azoe.widgets import FileOpenDialog
        if ruta is None:
            FileOpenDialog(cls.open_project, cls.fdProyectos, ft=['.json'])

        else:
            data = abrir_json(ruta)
            cls.PROYECTO = Proyecto(data)
            cls.PROYECTO.cargar(data)

            for key in data:
                if key == 'fondo':
                    if data[key] != "":
                        cls.set_ruta_fondo(data[key])
                elif key == 'props' or key == 'mobs':
                    widget = EventHandler.get_widget('Grilla.Canvas')
                    for item in data[key]:
                        nombre = item
                        _ruta = data['refs'][item]['ruta']
                        _cols = data['refs'][item]['code']

                        tipo = ''
                        if key == 'props':
                            sprite = cargar_imagen(_ruta)
                            tipo = 'Prop'
                        elif key == 'mobs':
                            sprite = split_spritesheet(_ruta)
                            tipo = 'Mob'

                        colision = None
                        if _cols is not None:
                            # w, h = 0, 0
                            # if key == 'props':
                            #     w, h = sprite.get_size()
                            # elif key == 'mobs':
                            #     w, h = sprite[0].get_size()
                            colision = deserialize(decode(descomprimir(_cols)))

                        idx = -1
                        for pos in data[key][item]:
                            rot = pos[3]
                            if type(sprite) == list:
                                image = sprite[rot]
                            else:
                                image = sprite
                            if len(pos) != 0:
                                idx += 1
                                datos = {"nombre": nombre, "image": image, "tipo": tipo,
                                         "grupo": key, "ruta": _ruta, "pos": pos,
                                         "index": idx, "colisiones": colision, 'rot': rot}
                                widget.add_tile(datos)

                elif key == 'referencias':
                    cls.referencias = data[key]
            cls.Guardado = ruta
            cls.habilitar_todo(True)

    @classmethod
    def save_project(cls, ruta=None, nombre=None):
        from azoe.widgets import FileSaveDialog
        if ruta is None:
            FileSaveDialog(cls.save_project, cls.fdProyectos, ft=['*.json'], name=nombre)

        else:
            data = cls.PROYECTO.guardar()
            guardar_json(ruta, data, False)
            cls.Guardado = ruta
            cls.estado = "Proyecto '" + ruta + "' guardado exitosamente."

    @classmethod
    def save_project_as(cls):
        cls.save_project(nombre='Guardar como...')

    @classmethod
    def close_project(cls):
        cls.PROYECTO = None
        cls.IMG_FONDO = None
        cls.habilitar_todo(False)
        for key in cls.referencias:
            cls.referencias[key] = None
        EventHandler.contents.update()

    @classmethod
    def exportar_mapa(cls, ruta=None):
        from azoe.widgets import FileSaveDialog
        if ruta is None:
            FileSaveDialog(cls.exportar_mapa, cls.fdExport, ft=['*.json'])

        else:
            try:
                mapa = cls.PROYECTO.exportar_mapa()
                guardar_json(ruta, mapa)
                cls.estado = "Mapa '" + ruta + "' exportado correctamente."

            except IOError as Description:
                print(Description)
                cls.estado = 'Error: No se pudo exportar el mapa.'

    @classmethod
    def set_preferences(cls):
        from rundata.menus.cuadros import CuadroPreferencias
        CuadroPreferencias()

    @staticmethod
    def habilitar_todo(control):
        for widget in EventHandler.contents.sprites():
            nombre = widget.nombre
            if nombre == 'PanelSimbolos.AreaPrev':
                simbolos = EventHandler.widgets[nombre]
                simbolos.habilitar(control)
            else:
                if hasattr(widget, 'habilitar'):
                    widget.habilitar(control)

    @staticmethod
    def exit():
        py_quit()
        sys_exit()

    @classmethod
    def cortar(cls):
        for elemento in cls.selected:
            elemento.parent.tiles.remove(elemento)
        Portapapeles.put('cut', *cls.selected)

    @classmethod
    def copiar(cls):
        copied = [item.copiar() for item in cls.selected]
        Portapapeles.put('copy', *copied)

    @classmethod
    def pegar(cls):
        widget = EventHandler.get_widget('Grilla.Canvas')
        Portapapeles.take(widget)

    @classmethod
    def update(cls):
        key = EventHandler.key
        cls.KeyCombinations.clear()

        if key is not None:
            if EventHandler.control:
                cls.KeyCombinations.append('Ctrl')
            if EventHandler.alt:
                cls.KeyCombinations.append('Alt')
            cls.KeyCombinations.append(key.upper())

        if cls.KeyCombinations:
            combination = '+'.join(cls.KeyCombinations)
            if combination in cls.key_bindings:
                cls.key_bindings[combination]()
            for widget in EventHandler.contents:
                if combination == widget.KeyCombination:
                    print(combination, widget)
                    widget.key_combination(combination)

        if cls.DiagBox is not None:
            if not cls.DiagMODE:
                for widget in EventHandler.contents:
                    if hasattr(widget, 'parent'):
                        if widget != cls.DiagBox and widget.parent != cls.DiagBox:
                            widget.enabled = False
                cls.DiagMODE = True
            else:
                if cls.DiagBox.update():
                    cls.DiagBoxes_repeat[cls.DiagBox.identifier] = cls.DiagBox.status
                    cls.DiagBox = None
                    for widget in EventHandler.contents:
                        if hasattr(widget, 'parent'):
                            if widget != cls.DiagBox and widget.parent != cls.DiagBox:
                                widget.enabled = True
                    cls.DiagMODE = False

        if len(cls.selected):
            cls.estado = ', '.join([tile.estado() for tile in sorted(cls.selected, key=lambda t: t.index)])


class BackgroundImage(DirtySprite):
    def __init__(self, ruta):
        super().__init__()
        self.image = cargar_imagen(ruta)
        self.rect = self.image.get_rect()
        self._layer = LAYER_FONDO
        if self.rect.w <= C * 15 or self.rect.h < C * 15:
            raise IOError()

    def update(self, dx=0, dy=0):
        self.rect.move_ip(dx, dy)
        self.dirty = 1
