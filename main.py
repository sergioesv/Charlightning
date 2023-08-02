#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb 13 18:59:17 2022

@author: Sergio Andrés Estrada Vélez
"""
import sys
import tkinter as tk
from app import App
from tkinter import ttk
from ttkthemes import ThemedTk


def main():
    """El programa principal instancia la ventana raiz Tk() y la usa
    para inicializar la aplicación y el bucle de eventos"""
    root = tk.Tk()
    #root.tk.call("source", "azure.tcl")
    #root.tk.call("set_theme", "dark")
    style = ttk.Style(root)
    

    style.theme_use("xpnative")


    print(style.theme_names())
    app = App(root)
    root.mainloop()
    # Simply set the theme


if __name__ == "__main__":
    main()
