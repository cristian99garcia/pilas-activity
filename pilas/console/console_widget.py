# -*- coding: utf-8 -*-
from __future__ import absolute_import

import re

from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GtkSource

from pilas.console import console


INDENT = 4

EDITOR_STYLE = """
GtkTextView {
    font-family: monospace;
    font-size: 10px;
    color: black;
    background-color: white;
}

GtkTextView:selected {
    color: white;
    background-color: #437DCD;
}"""

style_provider = Gtk.CssProvider()
style_provider.load_from_data(EDITOR_STYLE)

Gtk.StyleContext.add_provider_for_screen(
    Gdk.Screen.get_default(),
    style_provider,
    Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
)


class ConsoleWidget(Gtk.ScrolledWindow):

    def __init__(self, locals):
        Gtk.ScrolledWindow.__init__(self)

        self.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)

        self.view = GtkSource.View()
        self.view.set_tooltip_text("Show/Hide (F4)")
        self.view.connect("key-press-event", self.keyPressEvent)
        self.add(self.view)

        lang_manager = GtkSource.LanguageManager()

        self.buffer = self.view.get_buffer()
        self.buffer.set_max_undo_levels(0)
        self.buffer.set_language(lang_manager.get_language('python'))

        self.prompt = '>>> '
        self._console = console.Console(locals)
        self._history = []

        self.buffer.insert_at_cursor(self.prompt)
        self.setCursorPosition(0)

    def setCursorPosition(self, position):
        pos = len(self.prompt) + position

        for line in self.get_all_text().splitlines()[:-1]:
            pos += len(line) + 1

        iter = self.buffer.get_iter_at_offset(pos)
        self.buffer.place_cursor(iter)

    def keyPressEvent(self, widget, event):
        key = event.keyval

        if key == Gdk.KEY_Return:
            self._write_command()
            return True

        if self._get_cursor_position() <= 0 and (key == Gdk.KEY_BackSpace or key == Gdk.KEY_Left):
            self.setCursorPosition(0)
            return True

        if key == Gdk.KEY_Tab:
            self.buffer.insert_at_cursor(' ' * INDENT)
            return True

        elif key == Gdk.KEY_Up:
            self._set_command(self._get_prev_history_entry())
            return True

        elif key == Gdk.KEY_Down:
            self._set_command(self._get_next_history_entry())
            return True

        if key == Gdk.KEY_Tab:  # How this can be?
            if self.buffer.hasSelection():
                self.indent_more()
                return True

            else:
                self.buffer.insert_at_cursor(' ' * INDENT)
                return True

    def _text_under_cursor(self):
        tc = self.textCursor()
        tc.select(QTextCursor.WordUnderCursor)
        return tc.selectedText()

    def get_selection(self, posStart, posEnd):
        cursor = self.textCursor()
        cursor.setPosition(posStart)
        cursor2 = self.textCursor()

        if posEnd == QTextCursor.End:
            cursor2.movePosition(posEnd)
            cursor.setPosition(cursor2.position(), QTextCursor.KeepAnchor)

        else:
            cursor.setPosition(posEnd, QTextCursor.KeepAnchor)

        text = cursor.selectedText()
        return unicode(text)

    def _add_prompt(self, incomplete):
        if incomplete:
            prompt = '.' * 3 + ' '

        else:
            prompt = self.prompt

        self.buffer.insert_at_cursor("\n" + prompt)

        position = len(self.get_all_text())
        iter = self.buffer.get_iter_at_offset(position)
        self.buffer.backspace(iter, False, False)

    def _get_cursor_position(self):
        prvious_characters = 0
        for line in self.get_all_text().splitlines()[:-1]:
            prvious_characters += len(line) + 1

        cursor = self.buffer.get_property("cursor-position") - prvious_characters - len(self.prompt)
        return cursor

    def _write_command(self):
        command = self.get_all_text().splitlines()[-1]
        command = command[len(self.prompt):]

        self._add_history(command)
        incomplete = self._write(command)

        if not incomplete:
            output = self._read()

            if output is not None:
                if output.__class__.__name__ == 'unicode':
                    output = output.encode('utf8')

                self.buffer.insert_at_cursor("\n" + output.decode('utf8'))

        self._add_prompt(incomplete)

    def _set_command(self, command):
        text = self.get_all_text()
        line = text.splitlines()[-1]
        #self.buffer.place_cursor(self.buffer.get_end_iter())

        pos = len(self.prompt)

        for line in self.get_all_text().splitlines()[:-1]:
            pos += len(line) + 1

        start = self.buffer.get_iter_at_offset(pos)
        self.buffer.delete(start, self.buffer.get_end_iter())

        self.buffer.place_cursor(self.buffer.get_end_iter())
        self.buffer.insert_at_cursor(command)
        self.buffer.place_cursor(self.buffer.get_end_iter())

    def mousePressEvent(self, event):
        event.ignore()

    def _write(self, line):
        return self._console.push(line)

    def _read(self):
        return self._console.output

    def _add_history(self, command):
        if command and (not self._history or self._history[-1] != command):
            self._history.append(command)

        self.history_index = len(self._history)

    def _get_prev_history_entry(self):
        if self._history:
            self.history_index = max(0, self.history_index - 1)
            return self._history[self.history_index]

        return ''

    def _get_next_history_entry(self):
        if self._history:
            hist_len = len(self._history)
            self.history_index = min(hist_len, self.history_index + 1)
            if self.history_index < hist_len:
                return self._history[self.history_index]

        return ''

    def get_all_text(self):
        bounds = self.buffer.get_bounds()
        if bounds:
            start, end = bounds
            text = self.buffer.get_text(start, end, False)

        else:
            text = ""

        return text
