#!/usr/bin/env python3
"""
CLI entry point for the magic command
"""
from automation.menu import MainMenu


def main():
    """Entry point for the magic command"""
    menu = MainMenu()
    menu.run()


if __name__ == "__main__":
    main()