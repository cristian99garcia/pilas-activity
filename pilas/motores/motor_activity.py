# -*- encoding: utf-8 -*-
# pilas engine - a video game framework.
#
# copyright 2015 - Cristian García
# license: lgplv3 (see http://www.gnu.org/licenses/lgpl.html)
#
# website - http://www.pilas-engine.com.ar

import os
import sys
import copy

from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GLib
from gi.repository import GdkPixbuf

import motor
from pilas import imagenes
from pilas import actores
from pilas import eventos
from pilas import utils
from pilas import depurador

from pilas import fps
from pilas import simbolos
from pilas import colores

from sugar3.activity import activity
from sugar3.graphics.toolbarbox import ToolbarBox
from sugar3.activity.widgets import ActivityButton
from sugar3.activity.widgets import TitleEntry
from sugar3.activity.widgets import StopButton
from sugar3.activity.widgets import ShareButton


class BaseActor(object):

    def __init__(self):
        self._rotacion = 0
        self._transparencia = 0
        self.centro_x = 0
        self.centro_y = 0
        self._escala_x = 1
        self._escala_y = 1
        self._espejado = False
        self.fijo = 0

    def definir_centro(self, x, y):
        self.centro_x = x
        self.centro_y = y

    def obtener_posicion(self):
        return self.x, self.y

    def definir_posicion(self, x, y):
        self.x, self.y = x, y
        eventos.actualizar.send("update")

    def obtener_escala(self):
        return self._escala_x

    def definir_escala(self, s):
        self._escala_x = s
        self._escala_y = s
        eventos.actualizar.send("update")

    def definir_escala_x(self, s):
        self._escala_x = s

    def definir_escala_y(self, s):
        self._escala_y = s
        eventos.actualizar.send("update")

    def definir_transparencia(self, nuevo_valor):
        self._transparencia = nuevo_valor
        eventos.actualizar.send("update")

    def obtener_transparencia(self):
        return self._transparencia

    def obtener_rotacion(self):
        return self._rotacion

    def definir_rotacion(self, r):
        self._rotacion = r
        eventos.actualizar.send("update")

    def set_espejado(self, espejado):
        self._espejado = espejado
        eventos.actualizar.send("update")


class GtkImagen(object):

    def __init__(self, ruta):
        self.ruta_original = ruta
        self._imagen = GdkPixbuf.Pixbuf.new_from_file(ruta)

    def ancho(self):
        return self._imagen.get_width()

    def alto(self):
        return self._imagen.get_height()

    def centro(self):
        "Retorna una tupla con la coordenada del punto medio del la imagen."
        return (self.ancho() / 2, self.alto() / 2)

    def avanzar(self):
        pass

    def dibujar(self, motor, x, y, dx=0, dy=0, escala_x=1, escala_y=1, rotacion=0, transparencia=0):
        """Dibuja la imagen sobre la ventana que muestra el motor.

           x, y: indican la posicion dentro del mundo.
           dx, dy: es el punto centro de la imagen (importante para rotaciones).
           escala_x, escala_yindican cambio de tamano (1 significa normal).
           rotacion: angulo de inclinacion en sentido de las agujas del reloj.
        """

        motor.context.save()
        centro_x, centro_y = motor.centro_fisico()

        motor.context.translate(x + centro_x, centro_y - y)
        motor.context.rotate(rotacion)
        motor.context.scale(escala_x, escala_y)

        #if transparencia:
        #    motor.context.setOpacity(1 - transparencia/100.0)

        self._dibujar_pixbuf(motor.context, -dx, -dy)
        motor.context.restore()

    def _dibujar_pixbuf(self, context, x, y):
        Gdk.cairo_set_source_pixbuf(context, self._imagen, 0, 0)
        context.paint()

    def __str__(self):
        nombre_imagen = os.path.basename(self.ruta_original)
        return "<Imagen del archivo '%s'>" %(nombre_imagen)


class GtkGrilla(GtkImagen):

    """Representa una grilla regular, que se utiliza en animaciones.

       La grilla regular se tiene que crear indicando la cantidad
       de filas y columnas. Una vez definida se puede usar como
       una imagen normal, solo que tiene dos metodos adicionales
       para ``definir_cuadro`` y ``avanzar`` el cuadro actual.
    """

    def __init__(self, ruta, columnas=1, filas=1):
        GtkImagen.__init__(self, ruta)

        self.cantidad_de_cuadros = columnas * filas
        self.columnas = columnas
        self.filas = filas
        self.cuadro_ancho = GtkImagen.ancho(self) / columnas
        self.cuadro_alto = GtkImagen.alto(self) / filas
        self.definir_cuadro(0)

    def ancho(self):
        return self.cuadro_ancho

    def alto(self):
        return self.cuadro_alto

    def _dibujar_pixmap(self, motor, x, y):
        Gdk.cairo_set_source_pixbuf(context, self._imagen, self._image.width(), self._image.height())
        #motor.context.drawPixmap(x, y, self._imagen, self.dx, self.dy,
        #        self.cuadro_ancho, self.cuadro_alto)

    def definir_cuadro(self, cuadro):
        self._cuadro = cuadro

        frame_col = cuadro % self.columnas
        frame_row = cuadro / self.columnas

        self.dx = frame_col * self.cuadro_ancho
        self.dy = frame_row * self.cuadro_alto
        eventos.actualizar.send("update")

    def avanzar(self):
        ha_reiniciado = False
        cuadro_actual = self._cuadro + 1

        if cuadro_actual >= self.cantidad_de_cuadros:
            cuadro_actual = 0
            ha_reiniciado = True

        self.definir_cuadro(cuadro_actual)
        return ha_reiniciado

    def obtener_cuadro(self):
        return self._cuadro

    def dibujarse_sobre_una_pizarra(self, pizarra, x, y):
        pizarra.pintar_parte_de_imagen(self, self.dx, self.dy, self.cuadro_ancho, self.cuadro_alto, x, y)


class GtkTexto(GtkImagen):

    def __init__(self, texto, magnitud, motor):
        self._ancho, self._alto = motor.obtener_area_de_texto(texto, magnitud)

    def _dibujar_pixmap(self, motor, dx, dy):
        nombre_de_fuente = motor.context.get_font_face()
        tamano = 12
        r, g, b, a = self.color.obtener_componentes()

        motor.context.set_font_face(nombre_de_fuente)
        motor.context.set_font_size(tamano)
        motor.context.set_source_rgb(r, g, b)

        lines = self.texto.split('\n')

        for line in lines:
            extents = motor.context.text_extents(line)
            motor.context.show_text(dx, dy + self._alto, line)
            dy += extents.height()

    def ancho(self):
        return self._ancho

    def alto(self):
        return self._alto


class GtkLienzo(GtkImagen):

    def __init__(self):
        pass

    def texto(self, motor, cadena, x=0, y=0, magnitud=10, fuente=None, color=colores.negro):
        "Imprime un texto respespetando el desplazamiento de la camara."
        self.texto_absoluto(motor, cadena, x, y, magnitud, fuente, color)

    def texto_absoluto(self, motor, cadena, x=0, y=0, magnitud=10, fuente=None, color=colores.negro):
        "Imprime un texto sin respetar al camara."
        x, y = utils.hacer_coordenada_pantalla_absoluta(x, y)

        r, g, b, a = color.obtener_componentes()
        motor.context.set_source_rgb(r, g, b)

        if not fuente:
            fuente = motor.context.get_font_face()

        motor.context.set_font_face(fuente)
        motor.context.set_font_size(magnitud)
        motor.context.show_text(x, y, cadena)

    def pintar(self, motor, color):
        r, g, b, a = color.obtener_componentes()
        ancho, alto = motor.obtener_area()
        motor.context.set_source_rgb(r, g, b)
        motor.context.rectangle(0, 0, ancho, alto)

    def linea(self, motor, x0, y0, x1, y1, color=colores.negro, grosor=1):
        x0, y0 = utils.hacer_coordenada_pantalla_absoluta(x0, y0)
        x1, y1 = utils.hacer_coordenada_pantalla_absoluta(x1, y1)

        r, g, b, a = color.obtener_componentes()

        motor.context.set_source_rgb(r, g, b)
        motor.context.set_line_width(grosor)
        motor.context.move_to(x0, y0)
        motor.context.line_to(x1, y1)
        motor.context.stroke()

    def poligono(self, motor, puntos, color=colores.negro, grosor=1, cerrado=False):
        x, y = puntos[0]
        if cerrado:
            puntos.append((x, y))

        for p in puntos[1:]:
            nuevo_x, nuevo_y = p
            self.linea(motor, x, y, nuevo_x, nuevo_y, color, grosor)
            x, y = nuevo_x, nuevo_y

    def cruz(self, motor, x, y, color=colores.negro, grosor=1):
        t = 3
        self.linea(motor, x - t, y - t, x + t, y + t, color, grosor)
        self.linea(motor, x + t, y - t, x - t, y + t, color, grosor)

    def circulo(self, motor, x, y, radio, color=colores.negro, grosor=1):
        x, y = utils.hacer_coordenada_pantalla_absoluta(x, y)
        r, g, b, a = color.obtener_componentes()

        motor.context.set_source_rgb(r, g, b)
        motor.context.set_line_width(grosor)

        motor.context.arc(x -radio, y - radio, radio * 2, radio * 2)
        motor.stroke()

    def rectangulo(self, motor, x, y, ancho, alto, color=colores.negro, grosor=1):
        x, y = utils.hacer_coordenada_pantalla_absoluta(x, y)
        r, g, b, a = color.obtener_componentes()

        motor.context.set_source_rgb(r, g, b)
        motor.context.set_line_width(grosor)
        motor.context.rectangle(x, y, ancho, alto)
        motor.context.stroke()


class GtkSuperficie(GtkImagen):

    def __init__(self, ancho, alto):
        self.ancho = ancho
        self.alto = alto

    def pintar(self, color):
        r, g, b, a = color.obtener_componentes()
        self._imagen.fill(QtGui.QColor(r, g, b, a))

    def pintar_parte_de_imagen(self, imagen, origen_x, origen_y, ancho, alto, x, y):
        #self.canvas.begin(self._imagen)
        #self.canvas.drawPixmap(x, y, imagen._imagen, origen_x, origen_y, ancho, alto)
        #self.canvas.end()
        pass

    def pintar_imagen(self, imagen, x=0, y=0):
        self.pintar_parte_de_imagen(imagen, 0, 0, imagen.ancho(), imagen.alto(), x, y)

    def texto(self, cadena, x=0, y=0, magnitud=10, fuente=None, color=colores.negro):
        self.canvas.begin(self._imagen)
        r, g, b, a = color.obtener_componentes()
        self.canvas.setPen(QtGui.QColor(r, g, b))
        dx = x
        dy = y

        if not fuente:
            fuente = self.canvas.font().family()

        font = QtGui.QFont(fuente, magnitud)
        self.canvas.setFont(font)
        metrica = QtGui.QFontMetrics(font)

        for line in cadena.split('\n'):
            self.canvas.drawText(dx, dy, line)
            dy += metrica.height()

        self.canvas.end()

    def circulo(self, x, y, radio, color=colores.negro, relleno=False, grosor=1):
        self.canvas.begin(self._imagen)

        r, g, b, a = color.obtener_componentes()
        color = QtGui.QColor(r, g, b)
        pen = QtGui.QPen(color, grosor)
        self.canvas.setPen(pen)

        if relleno:
            self.canvas.setBrush(color)

        self.canvas.drawEllipse(x -radio, y-radio, radio*2, radio*2)
        self.canvas.end()

    def rectangulo(self, x, y, ancho, alto, color=colores.negro, relleno=False, grosor=1):
        self.canvas.begin(self._imagen)

        r, g, b, a = color.obtener_componentes()
        color = QtGui.QColor(r, g, b)
        pen = QtGui.QPen(color, grosor)
        self.canvas.setPen(pen)

        if relleno:
            self.canvas.setBrush(color)

        self.canvas.drawRect(x, y, ancho, alto)
        self.canvas.end()

    def linea(self, x, y, x2, y2, color=colores.negro, grosor=1):
        self.canvas.begin(self._imagen)

        r, g, b, a = color.obtener_componentes()
        color = QtGui.QColor(r, g, b)
        pen = QtGui.QPen(color, grosor)
        self.canvas.setPen(pen)

        self.canvas.drawLine(x, y, x2, y2)
        self.canvas.end()

    def poligono(self, puntos, color, grosor, cerrado=False):
        x, y = puntos[0]

        if cerrado:
            puntos.append((x, y))

        for p in puntos[1:]:
            nuevo_x, nuevo_y = p
            self.linea(x, y, nuevo_x, nuevo_y, color, grosor)
            x, y = nuevo_x, nuevo_y

    def dibujar_punto(self, x, y, color=colores.negro):
        self.circulo(x, y, 3, color=color, relleno=True)

    def limpiar(self):
        self._imagen.fill(QtGui.QColor(0, 0, 0, 0))


class GtkActor(BaseActor):

    def __init__(self, imagen="sin_imagen.png", x=0, y=0):

        if isinstance(imagen, str):
            self.imagen = imagenes.cargar(imagen)

        else:
            self.imagen = imagen

        self.x = x
        self.y = y
        BaseActor.__init__(self)

    def definir_imagen(self, imagen):
        # permite que varios actores usen la misma grilla.
        if isinstance(imagen, GtkGrilla):
            self.imagen = copy.copy(imagen)

        else:
            self.imagen = imagen

        eventos.actualizar.send("update")

    def obtener_imagen(self):
        return self.imagen

    def dibujar(self, motor):
        escala_x, escala_y = self._escala_x, self._escala_y

        if self._espejado:
            escala_x *= -1

        #if not self.fijo:
        #    x = self.x - motor.camara_x
        #    y = self.y - motor.camara_y
        #else:
        #    x = self.x
        #    y = self.y

        x = self.x
        y = self.y
        self.imagen.dibujar(motor, x, y,
                self.centro_x, self.centro_y,
                escala_x, escala_y, self._rotacion, self._transparencia)

    def actualizar(self):
        eventos.actualizar.send("update")


class GtkSonido:

    def __init__(self, ruta):
        try:
            import pygame
            pygame.mixer.init()
            self.sonido = pygame.mixer.Sound(ruta)

        except (ImportError, pygame.error):
            self.sonido = None

    def reproducir(self):
        if self.sonido != None:
            self.sonido.play()


class ActivityBase(activity.Activity, motor.Motor):

    def __init__(self, handle):
        activity.Activity.__init__(self, handle)
        motor.Motor.__init__(self)

        self.layout = Gtk.VBox()
        self.set_canvas(self.layout)

        self.canvas = Gtk.DrawingArea()
        self.layout.pack_start(self.canvas, False, False, 0)

        self.canvas.add_events(Gdk.EventMask.POINTER_MOTION_MASK |
                               Gdk.EventMask.BUTTON_PRESS_MASK |
                               Gdk.EventMask.BUTTON_RELEASE_MASK |
                               Gdk.EventMask.KEY_PRESS_MASK |
                               Gdk.EventMask.KEY_RELEASE_MASK)

        self.canvas.connect("draw", self.paintEvent)
        self.canvas.connect("button-press-event", self.mousePressEvent)
        self.canvas.connect("button-release-event", self.mouseReleaseEvent)
        self.canvas.connect("motion-notify-event", self.mouseMoveEvent)
        self.canvas.connect("key-press-event", self.keyPressEvent)
        self.canvas.connect("key-release-event", self.keyReleaseEvent)

        self.fps = fps.FPS(60, True)
        self.pausa_habilitada = False

        self.depurador = depurador.Depurador(self.obtener_lienzo(), self.fps)
        self.mouse_x = 0
        self.mouse_y = 0
        self.camara_x = 0
        self.camara_y = 0

        self.__fullscreen = False

        eventos.actualizar.connect(self.actualizar_pantalla)

    def __make_toolbar(self):
        # toolbar with the new toolbar redesign
        toolbar_box = ToolbarBox()

        activity_button = ActivityButton(self)
        toolbar_box.toolbar.insert(activity_button, 0)
        activity_button.show()

        title_entry = TitleEntry(self)
        toolbar_box.toolbar.insert(title_entry, -1)
        title_entry.show()

        share_button = ShareButton(self)
        toolbar_box.toolbar.insert(share_button, -1)
        share_button.show()

        separator = Gtk.SeparatorToolItem()
        separator.props.draw = False
        separator.set_expand(True)
        toolbar_box.toolbar.insert(separator, -1)
        separator.show()

        stop_button = StopButton(self)
        toolbar_box.toolbar.insert(stop_button, -1)
        stop_button.show()

        self.set_toolbar_box(toolbar_box)
        toolbar_box.show()

    def iniciar_ventana(self, ancho, alto, titulo, pantalla_completa):
        self.ancho = ancho
        self.alto = alto
        self.ancho_original = ancho
        self.alto_original = alto
        self.titulo = titulo
        self.__fullscreen = pantalla_completa
        self.centrar_ventana()

        if pantalla_completa:
            self.fullscreen()

        else:
            self.show()

        self.canvas.set_size_request(ancho, alto)

        self.__make_toolbar()
        # Activa la invocacion al evento timerEvent.
        #self.startTimer(1000 / 60.0)

    def pantalla_completa(self):
        self.__fullscreen = True
        self.fullscreen()

    def pantalla_modo_ventana(self):
        self.__fullscreen = False
        self.unfullscreen()

    def esta_en_pantalla_completa(self):
        return self.__fullscreen

    def alternar_pantalla_completa(self):
        """Permite cambiar el modo de video.

        Si está en modo ventana, pasa a pantalla completa y viceversa.
        """
        if self.esta_en_pantalla_completa():
            self.pantalla_modo_ventana()

        else:
            self.pantalla_completa()

    def centro_fisico(self):
        "Centro de la ventana para situar el punto (0, 0)"
        return self.ancho_original / 2, self.alto_original / 2

    def obtener_area(self):
        return (self.ancho_original, self.alto_original)

    def centrar_ventana(self):
        ancho_escritorio = Gdk.Screen.width()
        alto_escritorio = Gdk.Screen.height()
        #self.setGeometry((escritorio.width() - self.ancho) / 2, (escritorio.height() - self.alto) / 2, self.ancho, self.alto)

    def obtener_actor(self, imagen, x, y):
        return GtkActor(imagen, x, y)

    def obtener_texto(self, texto, magnitud):
        return GtkTexto(texto, magnitud, self)

    def obtener_grilla(self, ruta, columnas, filas):
        return GtkGrilla(ruta, columnas, filas)

    def actualizar_pantalla(self, *args):
        GLib.idle_add(self.canvas.queue_draw)

    def definir_centro_de_la_camara(self, x, y):
        self.camara_x = x
        self.camara_y = y

    def obtener_centro_de_la_camara(self):
        return (self.camara_x, self.camara_y)

    def cargar_sonido(self, ruta):
        return GtkSonido(ruta)

    def cargar_imagen(self, ruta):
        return GtkImagen(ruta)

    def obtener_lienzo(self):
        return GtkLienzo()

    def obtener_superficie(self, ancho, alto):
        return GtkSuperficie(ancho, alto)

    def ejecutar_bucle_principal(self, mundo, ignorar_errores):
        #sys.exit(self.app.exec_())
        pass

    def paintEvent(self, area, context):
        self.context = context

        alloc = self.canvas.get_allocation()
        ancho = self.alto * self.ancho_original / self.alto_original
        alto = self.alto

        self.context.set_source_rgb(1, 1, 1)
        self.context.rectangle(alloc.width / 2 - ancho / 2, 0, ancho, self.alto)
        self.context.fill()

        alto = self.alto / float(self.alto_original)
        self.context.scale(alto, alto)

        self.depurador.comienza_dibujado(self)

        for actor in actores.todos:
            try:
                actor.dibujar(self)

            except Exception as e:
                actor.eliminar()

            self.depurador.dibuja_al_actor(self, actor)

        self.depurador.termina_dibujado(self)

        return False

    def timerEvent(self, event):
        if not self.pausa_habilitada:
            try:
                self.realizar_actualizacion_logica()

            except Exception as e:
                pass

        # Invoca el dibujado de la pantalla.
        self.update()

    def realizar_actualizacion_logica(self):
        for x in range(self.fps.actualizar()):
            if not self.pausa_habilitada:
                eventos.actualizar.send("update")

                for actor in actores.todos:
                    actor.pre_actualizar()
                    actor.actualizar()

    def resizeEvent(self, area, event):
        self.ancho = event.size().width()
        self.alto = event.size().height()

    def mousePressEvent(self, area, e):
        escala = self.escala()
        x, y = utils.convertir_de_posicion_fisica_relativa(e.x / escala, e.y / escala)
        eventos.click_de_mouse.send("button-press-event", x=x, y=y, dx=0, dy=0)

    def mouseReleaseEvent(self, area, e):
        escala = self.escala()
        x, y = utils.convertir_de_posicion_fisica_relativa(e.x / escala, e.y / escala)
        eventos.termina_click.send("button-release-event", x=x, y=y, dx=0, dy=0)

    def wheelEvent(self, area, e):
        #eventos.mueve_rueda.send("scroll-event", delta=e.delta() / 120)
        # FIXME: Need connect "scroll-event"
        pass

    def mouseMoveEvent(self, area, e):
        escala = self.escala()
        x, y = utils.convertir_de_posicion_fisica_relativa(e.x / escala, e.y / escala)
        dx, dy = x - self.mouse_x, y - self.mouse_y

        eventos.mueve_mouse.send("motion-notify-event", x=x, y=y, dx=dx, dy=dy)

        self.mouse_x = x
        self.mouse_y = y

        self.actualizar_pantalla()

    def keyPressEvent(self, area, event):
        codigo_de_tecla = self.obtener_codigo_de_tecla_normalizado(event.key())

        if event.keyval == Gdk.KEY_Escape:
            eventos.pulsa_tecla_escape.send("key-press-event")

        if event.keyval == Gdk.KEY_P:
            self.alternar_pausa()

        if event.keyval == Gdk.KEY_F:
            self.alternar_pantalla_completa()

        eventos.pulsa_tecla.send("key-press-event", codigo=codigo_de_tecla, texto=event.text())

    def keyReleaseEvent(self, area, event):
        codigo_de_tecla = self.obtener_codigo_de_tecla_normalizado(event.key())
        eventos.suelta_tecla.send("key-release-event", codigo=codigo_de_tecla, texto=event.text())

    def obtener_codigo_de_tecla_normalizado(self, tecla):
        teclas = {
            Gdk.KEY_Left: simbolos.IZQUIERDA,
            Gdk.KEY_Right: simbolos.DERECHA,
            Gdk.KEY_Up: simbolos.ARRIBA,
            Gdk.KEY_Down: simbolos.ABAJO,
            Gdk.KEY_Space: simbolos.SELECCION,
            Gdk.KEY_Return: simbolos.SELECCION,
            Gdk.KEY_F1: simbolos.F1,
            Gdk.KEY_F2: simbolos.F2,
            Gdk.KEY_F3: simbolos.F3,
            Gdk.KEY_F4: simbolos.F4,
            Gdk.KEY_F5: simbolos.F5,
            Gdk.KEY_F6: simbolos.F6,
            Gdk.KEY_F7: simbolos.F7,
            Gdk.KEY_F8: simbolos.F8,
            Gdk.KEY_F9: simbolos.F9,
            Gdk.KEY_F10: simbolos.F10,
            Gdk.KEY_F11: simbolos.F11,
            Gdk.KEY_F12: simbolos.F12,
        }

        if teclas.has_key(tecla):
            return teclas[tecla]

        else:
            return tecla

    def escala(self):
        "Obtiene la proporcion de cambio de escala de la pantalla"
        return self.alto / float(self.alto_original)

    def obtener_area_de_texto(self, texto, magnitud=10):
        ancho = 0
        alto = 0

        self.context.set_font_size(magnitud)

        lineas = texto.split('\n')

        for linea in lineas:
            extents = self.context.get_text_extents(texto)
            ancho = max(ancho, extents.width)
            alto += extents.height

        return ancho, alto

    def alternar_pausa(self):
        if self.pausa_habilitada:
            self.pausa_habilitada = False
            self.actor_pausa.eliminar()

        else:
            self.pausa_habilitada = True
            self.actor_pausa = actores.Pausa()

    def ocultar_puntero_del_mouse(self):
        self.establecer_puntero_del_mouse(Gdk.CursorType.BLANK_CURSOR)

    def mostrar_puntero_del_mouse(self, cursor=Gdk.CursorType.ARROW):
        self.establecer_puntero_del_mouse(cursor)

    def establecer_puntero_del_mouse(self, cursor):
        if not self.canvas.get_realized():
            print("El area de dibujado tiene que ser visible para establecer un puntero")
            return

        cursor = Gdk.Cursor.new_from_name(Gdk.Display.get_default(), cursor)
        win = self.canvas.get_window()
        win.set_curosr(cursor)

