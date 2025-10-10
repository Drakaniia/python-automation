#!/usr/bin/env python3
"""
Main entry point for Python Automation System
"""
import sys
from pathlib import Path

# Add automation modules to path
sys.path.insert(0, str(Path(__file__).parent / "automation"))

from automation.menu import MainMenu


def main():
    """Entry point for the automation system"""
    menu = MainMenu()
    menu.run()


if __name__ == "__main__":
    main()