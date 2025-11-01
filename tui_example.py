#!/usr/bin/env python3
"""
TUI Example — Custom ANSI Shadow Font
-------------------------------------
Uses a local pyfiglet font file located at: ./font/ansi_shadow.flf
"""

import sys
from pathlib import Path
from pyfiglet import Figlet, FigletFont, FontNotFound
from colorama import Fore, Style, init

# Initialize colorama for Windows color support
init(autoreset=True)

# === Define the font path ===
font_path = Path(__file__).parent / "font" / "ansi_shadow.flf"

# === Verify the font exists ===
if not font_path.exists():
    print(Fore.RED + f"[ERROR] Font file not found at: {font_path}")
    print(Fore.YELLOW + "→ Make sure 'ansi_shadow.flf' is inside the 'font' folder.")
    sys.exit(1)

# === Try to load the font ===
try:
    custom_font = FigletFont(font=str(font_path))
    fig = Figlet(font=custom_font)
except FontNotFound as e:
    print(Fore.RED + f"[ERROR] Could not load custom font: {e}")
    sys.exit(1)

# === Render header ===
title = "Python Automation"
rendered = fig.renderText(title)
print(Fore.GREEN + rendered)
print(Style.BRIGHT + Fore.CYAN + f"Loaded custom font: {font_path.name}\n")

# === Interactive text renderer ===
try:
    while True:
        user_input = input(Fore.WHITE + ">>> Enter text to render (or 'q' to quit): ").strip()
        if user_input.lower() in ("q", "quit", "exit"):
            print(Fore.CYAN + "Goodbye!\n")
            break

        if not user_input:
            continue

        rendered_text = fig.renderText(user_input)
        print(Fore.GREEN + rendered_text)

except KeyboardInterrupt:
    print(Fore.CYAN + "\n[!] Exiting gracefully...\n")
    sys.exit(0)
