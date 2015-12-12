# Copyright 2009 Simon Schampijer
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

"""Pilas Activity.  Live interpreter to learn programming with games."""

import os
import sys
import copy
import logging
import subprocess

from gettext import gettext as _

from gi.repository import Gtk
from gi.repository import Gdk

from sugar3.activity import activity
from sugar3.graphics.toolbarbox import ToolbarBox
from sugar3.activity.widgets import ActivityButton
from sugar3.activity.widgets import TitleEntry
from sugar3.activity.widgets import StopButton
from sugar3.activity.widgets import ShareButton

import pilas
from pilas.motores.motor_gtk import GtkBase
from pilas.console import console_widget


class ActivityMotor(activity.Activity, GtkBase):

    def __init__(self, handle):
        activity.Activity.__init__(self, handle)
        GtkBase.__init__(self)


class PilasActivity(ActivityMotor):
    """Pilas class as specified in activity.info"""

    def __init__(self, handle):
        """Set up the Pilas activity."""
        ActivityMotor.__init__(self, handle)

        # we do not have collaboration features,
        # make the share option insensitive
        self.max_participants = 1

        self.make_toolbar()

        # Pilas
        vbox = Gtk.VBox()
        self.set_canvas(vbox)

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

    def make_toolbar(self):
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

    def sonreir(self, evento):
        #self.mono.sonreir()
        pass
