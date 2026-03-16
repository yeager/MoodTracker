"""Setup-konfiguration för MoodTracker."""

from setuptools import setup, find_packages

setup(
    name="moodtracker",
    version="1.0.0",
    description="Känsloloapp med daglig check-in via emoji/piktogram",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="MoodTracker Team",
    license="GPL-3.0",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "PyGObject>=3.42",
        "matplotlib>=3.5",
    ],
    entry_points={
        "console_scripts": [
            "moodtracker=moodtracker.app:main",
        ],
        "gui_scripts": [
            "moodtracker-gui=moodtracker.app:main",
        ],
    },
    data_files=[
        ("share/applications", ["data/se.moodtracker.app.desktop"]),
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: X11 Applications :: GTK",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3",
        "Topic :: Desktop Environment",
    ],
)
