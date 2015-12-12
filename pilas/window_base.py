# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'data/window.ui'
#
# Created: Sun Sep 25 16:42:42 2011
#      by: PyQt4 UI code generator 4.8.3
#
# WARNING! All changes made in this file will be lost!

from gi.repository import Gtk


class Ui_Window(object):

    def setupUi(self, Window):

        Window.set_name("Window")

        Window.resize(503, 477)
        self.verticalLayout = Gtk.VBox()
        Window.add(self.verticalLayout)

        self.graphicsView = Gtk.DrawingArea()
        #self.graphicsView.setBackgroundBrush(brush)
        #self.graphicsView.setObjectName(_fromUtf8("graphicsView"))
        self.verticalLayout.pack_start(self.graphicsView, True, True, 0)

        #self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        #self.graphicsView = QtGui.QGraphicsView(Window)
        #brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        #brush.setStyle(QtCore.Qt.NoBrush)

        self.plainTextEdit = Gtk.TextView()
        #self.plainTextEdit.setObjectName(_fromUtf8("plainTextEdit"))
        self.verticalLayout.pack_start(self.plainTextEdit, True, True, 0)

        s#elf.retranslateUi(Window)
        #QtCore.QMetaObject.connectSlotsByName(Window)

    def retranslateUi(self, Window):
        Window.setWindowTitle(QtGui.QApplication.translate("Window", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.plainTextEdit.setPlainText(QtGui.QApplication.translate("Window", "import blabla\n"
"", None, QtGui.QApplication.UnicodeUTF8))

