"""Gtk.Application för MoodTracker."""

import sys
import gettext
import locale
from pathlib import Path

import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, Gio

from . import __app_id__
from .window import MoodTrackerWindow

# Konfigurera i18n
APP_NAME = "moodtracker"
LOCALE_DIR = Path(__file__).parent.parent / "po"

try:
    locale.setlocale(locale.LC_ALL, "")
except locale.Error:
    pass

gettext.bindtextdomain(APP_NAME, str(LOCALE_DIR))
gettext.textdomain(APP_NAME)
_ = gettext.gettext


class MoodTrackerApp(Adw.Application):
    """Huvudapplikation för MoodTracker."""

    def __init__(self):
        super().__init__(
            application_id=__app_id__,
            flags=Gio.ApplicationFlags.DEFAULT_FLAGS,
        )

    def do_activate(self):
        """Aktivera applikationen."""
        win = self.props.active_window
        if not win:
            win = MoodTrackerWindow(self)
        win.present()


def main():
    """Starta MoodTracker."""
    app = MoodTrackerApp()
    return app.run(sys.argv)


if __name__ == "__main__":
    sys.exit(main())
