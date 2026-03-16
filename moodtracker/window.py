"""Huvudfönster för MoodTracker med GTK4/Adwaita."""

import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, GLib, Gio, GdkPixbuf, Gdk

import gettext
from datetime import datetime

from .database import MoodDatabase
from .charts import create_mood_chart, create_mood_distribution

# i18n
_ = gettext.gettext


class MoodButton(Gtk.Button):
    """En stor emoji-knapp för stämningsregistrering."""

    def __init__(self, mood_key, mood_info):
        super().__init__()
        self.mood_key = mood_key
        self.mood_info = mood_info

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)

        emoji_label = Gtk.Label(label=mood_info["emoji"])
        emoji_label.add_css_class("mood-emoji")

        text_label = Gtk.Label(label=mood_info["label_sv"])
        text_label.add_css_class("mood-label")

        box.append(emoji_label)
        box.append(text_label)
        self.set_child(box)

        self.add_css_class("mood-button")
        self.set_size_request(90, 90)


class CheckInView(Gtk.Box):
    """Vy för daglig stämnings-check-in."""

    def __init__(self, db, on_mood_logged):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        self.db = db
        self.on_mood_logged = on_mood_logged

        self.set_margin_top(24)
        self.set_margin_bottom(24)
        self.set_margin_start(24)
        self.set_margin_end(24)

        # Rubrik
        header = Gtk.Label(label=_("Hur mår du just nu?"))
        header.add_css_class("title-1")
        self.append(header)

        subtitle = Gtk.Label(label=_("Select den känsla som bäst beskriver dig"))
        subtitle.add_css_class("dim-label")
        self.append(subtitle)

        # Emoji FlowBox
        self.flowbox = Gtk.FlowBox()
        self.flowbox.set_max_children_per_line(4)
        self.flowbox.set_min_children_per_line(2)
        self.flowbox.set_selection_mode(Gtk.SelectionMode.NONE)
        self.flowbox.set_homogeneous(True)
        self.flowbox.set_row_spacing(12)
        self.flowbox.set_column_spacing(12)
        self.flowbox.set_halign(Gtk.Align.CENTER)
        self.flowbox.set_valign(Gtk.Align.CENTER)

        for mood_key, mood_info in MoodDatabase.MOODS.items():
            btn = MoodButton(mood_key, mood_info)
            btn.connect("clicked", self._on_mood_clicked)
            self.flowbox.append(btn)

        self.append(self.flowbox)

        # Anteckningsfält
        note_label = Gtk.Label(label=_("Anteckning (valfritt):"))
        note_label.set_halign(Gtk.Align.START)
        note_label.add_css_class("heading")
        self.append(note_label)

        self.note_entry = Gtk.TextView()
        self.note_entry.set_wrap_mode(Gtk.WrapMode.WORD)
        self.note_entry.set_size_request(-1, 80)
        self.note_entry.add_css_class("card")

        note_scroll = Gtk.ScrolledWindow()
        note_scroll.set_child(self.note_entry)
        note_scroll.set_min_content_height(80)
        self.append(note_scroll)

        # Dagens registreringar
        self._build_today_section()

    def _build_today_section(self):
        """Visa dagens registreringar."""
        # Ta bort gammal sektion om den finns
        if hasattr(self, "today_box"):
            self.remove(self.today_box)

        self.today_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)

        today_label = Gtk.Label(label=_("Dagens registreringar"))
        today_label.add_css_class("title-3")
        today_label.set_halign(Gtk.Align.START)
        self.today_box.append(today_label)

        entries = self.db.get_today_entries()
        if entries:
            for entry in entries:
                ts = datetime.fromisoformat(entry["timestamp"])
                row = Gtk.Box(spacing=8)
                row.add_css_class("card")
                row.set_margin_top(2)
                row.set_margin_bottom(2)

                time_label = Gtk.Label(label=ts.strftime("%H:%M"))
                time_label.add_css_class("dim-label")
                row.append(time_label)

                emoji_label = Gtk.Label(label=entry["emoji"])
                row.append(emoji_label)

                mood_info = MoodDatabase.MOODS.get(entry["mood_key"], {})
                name_label = Gtk.Label(label=mood_info.get("label_sv", entry["mood_key"]))
                row.append(name_label)

                if entry["note"]:
                    note_label = Gtk.Label(label=f"— {entry['note']}")
                    note_label.add_css_class("dim-label")
                    note_label.set_ellipsize(3)  # PANGO_ELLIPSIZE_END
                    note_label.set_hexpand(True)
                    note_label.set_halign(Gtk.Align.START)
                    row.append(note_label)

                self.today_box.append(row)
        else:
            empty = Gtk.Label(label=_("Inga registreringar idag ännu"))
            empty.add_css_class("dim-label")
            self.today_box.append(empty)

        self.append(self.today_box)

    def _on_mood_clicked(self, button):
        """Hantera klick på stämningsknapp."""
        buf = self.note_entry.get_buffer()
        note = buf.get_text(buf.get_start_iter(), buf.get_end_iter(), False)
        self.db.add_entry(button.mood_key, note)
        buf.set_text("")
        self._build_today_section()
        self.on_mood_logged()


class ChartView(Gtk.Box):
    """Vy för grafer och statistik."""

    def __init__(self, db):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        self.db = db

        self.set_margin_top(24)
        self.set_margin_bottom(24)
        self.set_margin_start(24)
        self.set_margin_end(24)

        header = Gtk.Label(label=_("Dina känslomönster"))
        header.add_css_class("title-1")
        self.append(header)

        # Period-väljare
        period_box = Gtk.Box(spacing=8)
        period_box.set_halign(Gtk.Align.CENTER)

        for days, label in [(7, _("7 dagar")), (30, _("30 dagar")), (90, _("90 dagar"))]:
            btn = Gtk.Button(label=label)
            btn.connect("clicked", self._on_period_changed, days)
            btn.add_css_class("pill")
            period_box.append(btn)

        self.append(period_box)

        # Grafområde
        self.chart_scroll = Gtk.ScrolledWindow()
        self.chart_scroll.set_vexpand(True)
        self.chart_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        self.chart_scroll.set_child(self.chart_box)
        self.append(self.chart_scroll)

        self.refresh(30)

    def _on_period_changed(self, button, days):
        self.refresh(days)

    def refresh(self, days=30):
        """Uppdatera graferna."""
        # Rensa
        while child := self.chart_box.get_first_child():
            self.chart_box.remove(child)

        daily_avgs = self.db.get_daily_averages(days)
        entries = self.db.get_entries_range(days)

        if not daily_avgs:
            empty = Gtk.Label(label=_("Ingen data ännu. Gör din första check-in!"))
            empty.add_css_class("dim-label")
            self.chart_box.append(empty)
            return

        # Trendgraf
        chart_data = create_mood_chart(
            daily_avgs, days, _("Stämning senaste %d dagarna") % days
        )
        if chart_data:
            self._add_chart_image(chart_data)

        # Fördelningsgraf
        dist_data = create_mood_distribution(entries, _("Känslofördelning"))
        if dist_data:
            self._add_chart_image(dist_data)

        # Statistik
        if daily_avgs:
            stats_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
            stats_box.add_css_class("card")
            stats_box.set_margin_top(8)

            avg_val = sum(r["avg_mood"] for r in daily_avgs) / len(daily_avgs)
            total = sum(r["count"] for r in daily_avgs)

            stats = [
                (_("Genomsnittlig stämning: %.1f / 5") % avg_val),
                (_("Total antal registreringar: %d") % total),
                (_("Days med data: %d") % len(daily_avgs)),
            ]
            for s in stats:
                lbl = Gtk.Label(label=s)
                lbl.set_halign(Gtk.Align.START)
                stats_box.append(lbl)

            self.chart_box.append(stats_box)

    def _add_chart_image(self, png_data):
        """Lägg till en grafbild i vyn."""
        loader = GdkPixbuf.PixbufLoader.new_with_type("png")
        loader.write(png_data)
        loader.close()
        pixbuf = loader.get_pixbuf()
        texture = Gdk.Texture.new_for_pixbuf(pixbuf)
        picture = Gtk.Picture.new_for_paintable(texture)
        picture.set_can_shrink(True)
        picture.set_size_request(-1, 300)
        picture.add_css_class("card")
        self.chart_box.append(picture)


class MoodTrackerWindow(Adw.ApplicationWindow):
    """Huvudfönster för MoodTracker."""

    def __init__(self, app):
        super().__init__(application=app)
        self.set_title("MoodTracker")
        self.set_default_size(480, 720)

        self.db = MoodDatabase()

        # CSS
        self._load_css()

        # Huvudlayout
        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        # HeaderBar
        header = Adw.HeaderBar()
        header.set_title_widget(Adw.WindowTitle(
            title="MoodTracker",
            subtitle=_("Känsloloapp")
        ))

        # Export-knapp
        export_btn = Gtk.Button(icon_name="document-save-symbolic")
        export_btn.set_tooltip_text(_("Exportera till CSV"))
        export_btn.connect("clicked", self._on_export)
        header.pack_end(export_btn)

        self.main_box.append(header)

        # ViewStack med Adw.ViewSwitcherBar
        self.view_stack = Adw.ViewStack()

        # Check-in-vy
        checkin_scroll = Gtk.ScrolledWindow()
        self.checkin_view = CheckInView(self.db, self._on_mood_logged)
        checkin_scroll.set_child(self.checkin_view)
        self.view_stack.add_titled_with_icon(
            checkin_scroll, "checkin", _("Check-in"), "emoji-people-symbolic"
        )

        # Grafvy
        self.chart_view = ChartView(self.db)
        self.view_stack.add_titled_with_icon(
            self.chart_view, "charts", _("Statistics"), "utilities-system-monitor-symbolic"
        )

        # ViewSwitcher i headern
        switcher = Adw.ViewSwitcher()
        switcher.set_stack(self.view_stack)
        switcher.set_policy(Adw.ViewSwitcherPolicy.WIDE)
        header.set_title_widget(switcher)

        # Bottom switcher bar för smala fönster
        switcher_bar = Adw.ViewSwitcherBar()
        switcher_bar.set_stack(self.view_stack)

        self.main_box.append(self.view_stack)
        self.main_box.append(switcher_bar)

        # Bind reveal för smal vy
        switcher.connect("notify::title-visible", lambda s, _: switcher_bar.set_reveal(True))

        self.view_stack.set_vexpand(True)
        self.set_content(self.main_box)

    def _load_css(self):
        """Ladda anpassad CSS."""
        css = b"""
        .mood-emoji {
            font-size: 36px;
        }
        .mood-label {
            font-size: 12px;
            font-weight: 600;
        }
        .mood-button {
            padding: 12px;
            border-radius: 16px;
            transition: all 200ms ease;
        }
        .mood-button:hover {
            background: alpha(@accent_color, 0.15);
            transform: scale(1.05);
        }
        .mood-button:active {
            background: alpha(@accent_color, 0.3);
        }
        """
        provider = Gtk.CssProvider()
        provider.load_from_data(css)
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(),
            provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
        )

    def _on_mood_logged(self):
        """Callback när en stämning har registrerats."""
        self.chart_view.refresh(30)
        # Visa bekräftelse
        toast = Adw.Toast(title=_("Känsla registrerad! ✓"))
        toast.set_timeout(2)
        # Adw.Toast behöver en ToastOverlay
        if not hasattr(self, "_toast_overlay"):
            self._toast_overlay = Adw.ToastOverlay()
            content = self.main_box
            self.set_content(None)
            self._toast_overlay.set_child(content)
            self.set_content(self._toast_overlay)
        self._toast_overlay.add_toast(toast)

    def _on_export(self, button):
        """Exportera data till CSV."""
        dialog = Gtk.FileDialog()
        dialog.set_initial_name("moodtracker_export.csv")

        csv_filter = Gtk.FileFilter()
        csv_filter.set_name("CSV-filer")
        csv_filter.add_pattern("*.csv")
        filters = Gio.ListStore.new(Gtk.FileFilter)
        filters.append(csv_filter)
        dialog.set_filters(filters)

        dialog.save(self, None, self._on_export_response)

    def _on_export_response(self, dialog, result):
        """Hantera export-svar."""
        try:
            file = dialog.save_finish(result)
            if file:
                path = file.get_path()
                self.db.export_csv(path)
                toast = Adw.Toast(title=_("Exporterad till %s") % path)
                toast.set_timeout(3)
                if hasattr(self, "_toast_overlay"):
                    self._toast_overlay.add_toast(toast)
        except GLib.Error:
            pass  # Användaren avbröt
