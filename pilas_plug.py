#!/usr/bin/env python

import os
import sys

from gi.repository import Gtk

import pilas
from pilas import aplicacion

app = QApplication(sys.argv)

parent_window_id = int(sys.argv[1])
screen_width = int(sys.argv[2])
screen_height = int(sys.argv[3])

window = QX11EmbedWidget()
window.embedInto(parent_window_id)
window.show()

hbox = QHBoxLayout(window)
pilas_height = 2.0 / 3 * screen_height
pilas_width = 2.0 / 3 * screen_width
pilas_widget = aplicacion.Window(parent=window, pilas_width=pilas_width, pilas_height=pilas_height)
hbox.addWidget(pilas_widget)

sys.exit(app.exec_())
