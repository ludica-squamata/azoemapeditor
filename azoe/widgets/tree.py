from . import Marco, BaseWidget, BaseOpcion, ToolTip, ScrollV
from azoe.libs.textrect import render_textrect
from azoe.engine import EventHandler, color
from pygame import font, Rect, Surface, draw
from pygame.sprite import LayeredDirty

class Tree (Marco):
    ItemActual = ''
    items = None
    def __init__(self,parent,x,y,w,h,walk,actual,**opciones):
        if 'colorFondo' not in opciones:
            opciones['colorFondo'] = 'sysMenBack'
        self.nombre = parent.nombre+'.Tree'
        super().__init__(x,y,w,h,False,**opciones)
        self.parent = parent
        self.layer = self.parent.layer +1
        self.items = LayeredDirty()
        self.crearLista(walk)
        self.ItemActual = actual #ruta
        self.ScrollY = ScrollV(self,self.x+self.w,self.y)
        self.agregar(self.ScrollY)
        self.doc_h = h
    
    def scroll(self,dy):
        pass
    
    def crearLista(self,opciones):
        h = 0
        for y in range(len(opciones)):
            x = opciones[y]['x']
            dx = self.x+(x*16)
            dy = self.y+(y*h)
            item = Item(self,dx,dy,opciones[y])
            h = item.h
            self.items.add(item)
            self.agregar(item)
        
        for i in range(len(self.items)):
            padre = self.items.get_sprite(i)
            for nomhijo in opciones[i]['hijos']:
                for j in range(len(self.items)):
                    hijo = self.items.get_sprite(j)
                    if hijo.nom_obj == nomhijo:
                        padre.hijos.add(hijo)
    
    def mover(self,item,dy):
        sprites = self.items.sprites()
        for idx in range(len(sprites)):
            if sprites[idx].nombre == item.nombre:
                idx += 1
                break
        dh = 0
        for hijo in item.hijos:
            dh += hijo.h
            idx += 1
        
        for i in range(idx,len(self.items)):
            widget = self.items.get_sprite(i)
            widget.mover(dh*dy)
    
    def on_mouse_down(self, button):
        if self.ScrollY.enabled:
            if button == 5:
                self.ScrollY.moverCursor(dy=+10)
            if button == 4:
                self.ScrollY.moverCursor(dy=-10)
    
    def update(self):
        for item in self.items:
            if item.opcion.path == self.ItemActual:
                item.opcion.selected = True
            else:
                item.opcion.selected = False

class Item (BaseWidget):
    hijos = None
    def __init__(self,parent,x,y,keyargs,**opciones):
        super().__init__(parent,**opciones)
        self.x,self.y = x,y
        self.nombre = self.parent.nombre+'.Item:'+keyargs['obj']
        self.nom_obj = keyargs['obj']
        self.hijos = LayeredDirty()
        self.visible = 0 # no es que sea invisible, es que no tiene imagen
        self.opcion = _Opcion(self,self.nom_obj,keyargs['path'],x+16+3,y)
        h = self.opcion.image.get_height()
        self.cursor = _Cursor(self,self.nom_obj,x,y,16,h-2,keyargs['empty'])
        w = self.cursor.rect.w+3+self.opcion.rect.w
        self.rect = Rect(x,y,w,h)
        self.w,self.h = self.rect.size
        EventHandler.add_widget(self.opcion)
        EventHandler.add_widget(self.cursor)
                
    def on_destruction(self):
        EventHandler.del_widget(self.opcion.tooltip)
        EventHandler.del_widget(self.opcion)
        EventHandler.del_widget(self.cursor)
    
    def reubicar_en_ventana(self,dx=0,dy=0):
        super().reubicar_en_ventana(dx,dy)
        self.opcion.reubicar_en_ventana(dx,dy)
        self.cursor.reubicar_en_ventana(dx,dy)
        
    def colapsarHijos(self):
        for hijo in self.hijos:
            hijo.AutoColapsar()
            hijo.colapsarHijos()

    def mostrarHijos(self):
        for hijo in self.hijos:
            hijo.AutoMostrar()
            if hijo.cursor.open:
                hijo.mostrarHijos()
            
    def AutoColapsar(self):
        for obj in [self.opcion,self.cursor]:
            obj.visible = False
            obj.enabled = False
        self.enabled = False

    def AutoMostrar(self):
        for obj in [self.opcion,self.cursor]:
            obj.visible = True
            obj.enabled = True
        self.enabled = True
    
    def mover(self,dy):
        for obj in [self,self.opcion,self.cursor]:
            obj.y += dy
            obj.rect.y += dy
    
class _Opcion(BaseOpcion):
    path = ''
    selected = False
    
    def __init__(self,parent,nombre,path,x,y,w=0):
        super().__init__(parent,nombre,x,y,w)
        self.layer = self.parent.layer
        self.texto = nombre
        self.path = path
        self.tooltip = ToolTip(self.parent,path,x,y)
        self.nombre = self.parent.nombre+'.Opcion'
    
    def serElegido(self):
        self.selected = True
        self.image = self.img_sel
        self.dirty = 1
    
    def serDeselegido(self):
        self.selected = False
        self.image = self.img_des
        self.dirty = 1
        
    def on_mouse_down(self, button):
        if button == 1:
            self.serElegido()
            self.parent.parent.ItemActual = self.path
    
    def on_focus_out(self):
        super().on_focus_out()
        self.serDeselegido()
    
    def update(self):        
        if self.hasMouseOver:
            self.tooltip.show()
        else:
            self.tooltip.hide()

class _Cursor(BaseWidget):
    def __init__(self,parent,nombre,x,y,w,h,vacio,**opciones):
        super().__init__(parent,**opciones)
        self.nombre = self.parent.nombre+'.Cursor'
        self.layer = self.parent.layer #overwrite
        self.x,self.y = x,y
        self.w,self.h = w,h
        self.open = True
        self.vacio = vacio
        self.img_cld = self._crear(self.w,self.h,False)
        self.img_opn = self._crear(self.w,self.h,True)
        self.setStatus()
        self.rect = self.image.get_rect(topleft = (self.x,self.y))
    
    @staticmethod
    def _crear(w,h,closed):
        imagen = Surface((w,h))
        imagen.fill(color('sysMenBack'))
        rect = imagen.get_rect()
        if closed:
            draw.line(imagen,(0,0,0),(5,rect.h//2),(rect.w-4,rect.h//2),2)
        else:
            draw.line(imagen,(0,0,0),(5,rect.h//2),(rect.w-4,rect.h//2),2)
            draw.line(imagen,(0,0,0),(8,4),(8,rect.h-4),2)
        draw.rect(imagen,(0,0,0),(2,2,rect.w-2,rect.h-2),1)
        return imagen
    
    def on_mouse_down(self, button):
        if button == 1:
            if not self.vacio:
                self.open = not self.open
            
            dy = self.setStatus()
                
            
            self.parent.parent.mover(self.parent,dy)
    
    def setStatus(self):
        if self.open:
            self.image = self.img_opn
            self.parent.mostrarHijos()
            self.dirty = 1
            dy = +1
        else:
            self.image = self.img_cld
            self.parent.colapsarHijos()
            self.dirty = 1
            dy = -1
        return dy