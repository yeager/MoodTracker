# MoodTracker - Känsloloapp 😊

En GTK4/Adwaita-app för daglig stämnings-check-in med emoji och piktogram. Designad för emotionell självkännedom med stöd för export till psykolog/BUP.

## Funktioner

- **Daglig check-in** — Registrera din stämning med stora emoji-knappar (😊 😢 😠 😰 😴 🥰 m.fl.)
- **Anteckningar** — Lägg till valfria anteckningar till varje registrering
- **Trendgrafer** — Visualisera dina känslomönster över 7, 30 eller 90 dagar
- **Känslofördelning** — Cirkeldiagram som visar fördelningen av dina registrerade känslor
- **CSV-export** — Exportera all data för psykolog, BUP eller annan vårdgivare
- **i18n** — Svenska som huvudspråk, engelsk fallback via gettext
- **SQLite-databas** — Säker lokal lagring av all emotionell data

## Installation

### Förutsättningar

- Python 3.10+
- GTK4 och libadwaita
- PyGObject
- matplotlib

### Ubuntu/Debian

```bash
sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-4.0 gir1.2-adw-1 python3-matplotlib
```

### Fedora

```bash
sudo dnf install python3-gobject gtk4 libadwaita python3-matplotlib
```

### Arch Linux

```bash
sudo pacman -S python-gobject gtk4 libadwaita python-matplotlib
```

### macOS (Homebrew)

```bash
brew install gtk4 libadwaita pygobject3
pip install matplotlib
```

### Installera appen

```bash
pip install -e .
```

## Användning

### Starta appen

```bash
moodtracker
```

Eller kör direkt:

```bash
python -m moodtracker.app
```

### CSV-export

Klicka på spara-ikonen i headern för att exportera all data som CSV. Filen innehåller:

| Datum | Tid | Känsla | Emoji | Värde (1-5) | Anteckning |
|-------|-----|--------|-------|-------------|------------|
| 2026-03-16 | 14:30 | happy | 😊 | 5 | Bra dag! |

## Projektstruktur

```
MoodTracker/
├── moodtracker/
│   ├── __init__.py      # Paketinfo
│   ├── app.py           # Gtk.Application
│   ├── window.py        # UI-komponenter
│   ├── database.py      # SQLite-hantering
│   └── charts.py        # matplotlib-grafer
├── data/
│   └── se.moodtracker.app.desktop
├── po/
│   ├── moodtracker.pot  # Översättningsmall
│   ├── sv.po            # Svenska
│   └── en.po            # Engelska
├── setup.py
├── requirements.txt
└── README.md
```

## Data

All data lagras lokalt i `~/.local/share/moodtracker/moods.db` (SQLite).

## Licens

GPL-3.0
