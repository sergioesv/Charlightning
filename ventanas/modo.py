import tkinter as tk
from tkinter import ttk

from .panel import Panel
from variables.globales import papo

class Modo(Panel):
    """Panel para elegir si quiere una vista compacta del programa o una vista
    paso a paso con ayuda lateral"""

    def __init__(self, master, titulo, ancho, alto):
        super().__init__(master, titulo=titulo, ancho=ancho, alto=alto)
        self.extraer_entry36=tk.StringVar()
        self.extraer_entry37=tk.StringVar()
        self.extraer_entry38=tk.StringVar()
        self.extraer_entry39=tk.StringVar()
        self.extraer_text1=tk.StringVar()

        self.extraer_entry36.set('')
        self.extraer_entry37.set('')
        self.extraer_entry38.set('')
        self.extraer_entry39.set('')
        self.extraer_text1.set('')

   



        self.Frame15 = ttk.Frame(self)
        self.Labelframe15 = ttk.Labelframe(self.Frame15)
        self.Label36 = ttk.Label(self.Labelframe15)
        self.Label36.configure(text='Proyecto:')
        self.Label36.grid(column='0', padx='10', pady='5', row='0', sticky='sew')
        self.Labelframe15.rowconfigure('0', pad='3')
        self.Label37 = ttk.Label(self.Labelframe15)
        self.Label37.configure(text='Diseñador:')
        self.Label37.grid(column='0', padx='10', pady='5', row='1', sticky='sew')
        self.Labelframe15.rowconfigure('1', pad='3')
        self.Label38 = ttk.Label(self.Labelframe15)
        self.Label38.configure(text='Dirección:')
        self.Label38.grid(column='0', padx='10', pady='5', row='2', sticky='sew')
        self.Labelframe15.rowconfigure('2', pad='3')
        self.Label52 = ttk.Label(self.Labelframe15)
        self.Label52.configure(text='Teléfono:')
        self.Label52.grid(column='0', padx='10', pady='5', row='3', sticky='sew')
        self.Labelframe15.rowconfigure('3', pad='3', weight='0')
        self.Label67 = ttk.Label(self.Labelframe15)
        self.Label67.configure(text='Descripción:')
        self.Label67.grid(column='0', padx='10', pady='5', row='4', sticky='new')
        self.Labelframe15.rowconfigure('4', pad='3', weight='0')
        self.Entry36 = ttk.Entry(self.Labelframe15)
        self.Entry36.configure(textvariable=self.extraer_entry36,width='35')
        self.Entry36.grid(column='1', padx='10', row='0', sticky='sew')
        self.Labelframe15.columnconfigure('1', pad='3', weight='1')
        self.Entry37 = ttk.Entry(self.Labelframe15)
        self.Entry37.configure(textvariable=self.extraer_entry37, width='22')
        self.Entry37.grid(column='1', padx='10', row='1', sticky='sew')
        self.Entry38 = ttk.Entry(self.Labelframe15)
        self.Entry38.configure(textvariable=self.extraer_entry38, width='22')
        self.Entry38.grid(column='1', padx='10', row='2', sticky='sew')
        self.Entry39 = ttk.Entry(self.Labelframe15)
        self.Entry39.configure(textvariable=self.extraer_entry39, width='22')
        self.Entry39.grid(column='1', padx='10', row='3', sticky='sew')
        self.Text1 = tk.Text(self.Labelframe15)
        self.Text1.configure(height='5', insertunfocussed='hollow', width='35')
        self.Text1.grid(column='1', pady='10', row='4')
        self.Labelframe15.configure(height='200',
                                    relief='groove',
                                    text='Datos del proyecto',
                                    width='350')
        self.Labelframe15.grid(column='1', padx='30', pady='30', row='1')
        self.Frame17 = ttk.Frame(self.Frame15)
        self.Label69 = ttk.Label(self.Frame17)
        self.Label69.configure(text='Seleccione el modo de trabajo ')
        self.Label69.pack(padx='30', pady='30', side='top')

        self.Button6 = ttk.Button(self.Frame17)
        self.Button6.configure(text='Guiado', command=self.guiado)
        self.Button6.pack(side='top')
        self.Frame17.configure(height='200', width='200')
        self.Frame17.grid(column='0', row='1', sticky='n')
        self.Frame15.columnconfigure('0', minsize='100')
        self.Frame18 = ttk.Frame(self.Frame15)
        self.Label70 = ttk.Label(self.Frame18)
        self.Label70.configure(font='TkCaptionFont',
                               foreground='#3b3cdb',
                               text='Charlightning NTC-4552')
        self.Label70.pack(padx='10', pady='10', side='top')
        self.Frame18.configure(height='200', width='200')
        self.Frame18.grid(column='0', columnspan='2', pady='30', row='0')
        self.Frame19 = ttk.Frame(self.Frame15)
        self.Label71 = ttk.Label(self.Frame19)
        self.Label71.configure(font='TkTooltipFont', 
                               justify='center',
                               relief='ridge', 
                               text='  Diseñado por: Sergio Andrés Estrada Vélez')
        self.Label71.grid(column='1', ipadx='10', row='0')
        self.Frame19.rowconfigure('0', pad='0')
        self.Label72 = ttk.Label(self.Frame19)
        self.Label72.configure(font='TkTooltipFont', 
                               justify='center', 
                               relief='ridge', 
                               text='  Versión 0.0.7  ')
        self.Label72.grid(column='2', ipadx='10', row='0')
        self.Label74 = ttk.Label(self.Frame19)
        self.Label74.configure(font='TkTooltipFont',
                               justify='center',
                               relief='ridge',
                               text='  2002-05-06')
        self.Label74.grid(column='3', ipadx='10', row='0')
        self.Frame24 = ttk.Frame(self.Frame19)
        self.Frame24.configure(height='18', relief='ridge', width='200')
        self.Frame24.grid(column='0', row='0', sticky='ew')
        self.Frame19.columnconfigure('0', pad='0', weight='1')
        self.Frame19.configure(height='20', relief='flat', width='200')
        self.Frame19.grid(column='0', columnspan='2', row='3', sticky='ew')
        self.Frame15.configure(height='300', width='200')
        self.Frame15.pack(side='top')




    def guiado(self):
        papo['proyecto'] = self.extraer_entry36.get()
        papo['disenador'] = self.extraer_entry37.get()
        papo['direccion'] = self.extraer_entry38.get()
        papo['telefono'] = self.extraer_entry39.get()
        papo['descripcion'] = self.extraer_text1.get()


        

        self.siguienteguiado()

        

