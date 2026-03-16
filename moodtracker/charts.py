"""Matplotlib-grafer för emotionella trender."""

import io
from datetime import datetime

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


def create_mood_chart(daily_averages, days=30, title="Stämning över tid"):
    """Skapa en graf över stämning med matplotlib.

    Returnerar PNG-data som bytes.
    """
    if not daily_averages:
        return None

    dates = [datetime.strptime(row["date"], "%Y-%m-%d") for row in daily_averages]
    values = [row["avg_mood"] for row in daily_averages]
    counts = [row["count"] for row in daily_averages]

    fig, ax = plt.subplots(figsize=(8, 4), dpi=100)
    fig.patch.set_facecolor("#fafafa")
    ax.set_facecolor("#fafafa")

    # Stämningslinje
    ax.plot(dates, values, color="#6366f1", linewidth=2.5, marker="o",
            markersize=6, markerfacecolor="#818cf8", zorder=3)

    # Fyll under kurvan
    ax.fill_between(dates, values, alpha=0.15, color="#6366f1")

    # Referenslinjer för stämningsnivåer
    mood_labels = {1: "😠", 2: "😢", 3: "😐", 4: "🙂", 5: "😊"}
    for level, emoji in mood_labels.items():
        ax.axhline(y=level, color="#e5e7eb", linewidth=0.8, linestyle="--", zorder=1)
        ax.text(dates[0] if dates else datetime.now(), level + 0.1, emoji,
                fontsize=12, alpha=0.6, ha="left")

    ax.set_ylim(0.5, 5.5)
    ax.set_ylabel("Stämning", fontsize=11, color="#374151")
    ax.set_title(title, fontsize=14, fontweight="bold", color="#1f2937", pad=15)

    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d/%m"))
    ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
    plt.xticks(rotation=45, ha="right", fontsize=9)

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#d1d5db")
    ax.spines["bottom"].set_color("#d1d5db")
    ax.tick_params(colors="#6b7280")

    plt.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    buf.seek(0)
    return buf.read()


def create_mood_distribution(entries, title="Känslofördelning"):
    """Skapa ett cirkeldiagram över känslofördelning."""
    if not entries:
        return None

    from collections import Counter
    mood_counts = Counter(entry["mood_key"] for entry in entries)

    from .database import MoodDatabase
    labels = []
    sizes = []
    colors_list = ["#34d399", "#60a5fa", "#a78bfa", "#f87171", "#fbbf24", "#fb923c", "#94a3b8", "#f472b6"]

    for i, (mood_key, count) in enumerate(mood_counts.most_common()):
        mood_info = MoodDatabase.MOODS.get(mood_key, {})
        label = f"{mood_info.get('emoji', '?')} {mood_info.get('label_sv', mood_key)}"
        labels.append(label)
        sizes.append(count)

    fig, ax = plt.subplots(figsize=(6, 5), dpi=100)
    fig.patch.set_facecolor("#fafafa")

    wedges, texts, autotexts = ax.pie(
        sizes, labels=labels, autopct="%1.0f%%",
        colors=colors_list[:len(sizes)],
        startangle=90, pctdistance=0.8,
        textprops={"fontsize": 11}
    )
    for autotext in autotexts:
        autotext.set_fontsize(9)
        autotext.set_color("white")
        autotext.set_fontweight("bold")

    ax.set_title(title, fontsize=14, fontweight="bold", color="#1f2937", pad=15)
    plt.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    buf.seek(0)
    return buf.read()
