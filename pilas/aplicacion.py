import sys

import gi
gi.require_version('Gtk', '3.0')

from gi.repository import Gtk

import pilas
from pilas.motores.motor_gtk import GtkMotor

from pilas.console import console_widget


class Window(GtkMotor):

    def __init__(self, parent=None, pilas_width=320, pilas_height=240):
        GtkMotor.__init__(self)

        if (parent != None):
            self.set_transient_for(parent)

        self.set_title("Hola")

        vbox = Gtk.VBox()
        self.add(vbox)

        pilas.iniciar(motor=self)

        horizontalLayout = Gtk.HBox()
        vbox.pack_start(horizontalLayout, True, True, 0)

        #Crear actor
        self.mono = pilas.actores.Mono()
        pilas.eventos.click_de_mouse.conectar(self.sonreir)

        # Agrega la Consola
        locals = {'pilas': pilas, 'mono': self.mono}
        self.consoleWidget = console_widget.ConsoleWidget(locals)
        vbox.pack_start(self.consoleWidget, True, True, 0)

        self.connect("destroy", Gtk.main_quit)

        self.show_all()

    def sonreir(self, evento):
        #self.mono.sonreir()
        pass


def main():
    ventana = Window()
    Gtk.main()


if __name__ == '__main__':
    import signal
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    main()
