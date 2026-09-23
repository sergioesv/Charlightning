#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb 13 18:59:17 2022

@author: Sergio Andrés Estrada Vélez
"""
import tkinter as tk
from tkinter import ttk

from app import App


def main():
    """Crea la ventana principal y arranca la aplicación."""
    root = tk.Tk()
    style = ttk.Style(root)
    
    # "xpnative" solo existe en Windows. Si no está disponible,
    # usamos "clam", que viene con Python en todos los sistemas.
    if "xpnative" in style.theme_names():
        style.theme_use("xpnative")
    else:
        style.theme_use("clam")

    app = App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
