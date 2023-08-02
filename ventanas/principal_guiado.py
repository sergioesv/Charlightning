# Charlightning
# Copyright (C) 2022 Sergio Andrés Estrada Vélez
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 3 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

import tkinter as tk
import math
import PDF_Creator
from tkinter import ttk
from tkinter import messagebox

from ventanas.panel import Panel
from calculo_ddt_plot.ventana_calculo_ddt import Calculo_DDT
from variables.globales import papo
from variables.variable_generales import VAR
from calculate_risk.collect_entry_data_risk import DataEntryRiskTable

class Principal_guiado(Panel):
    """Panel que muestra una "terminal" negra y el botón para generar la tabla.
    Al pulsar ese botón llama a self.siguiente() para mostrar el panel que
    pide un número al usuario"""

    def __init__(self, master, titulo, ancho, alto):
        super().__init__(master, titulo=titulo, ancho=ancho, alto=alto)
        
        self.ddt_retorno = None

        self.vcmd = (self.register(self.check), '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')

        self.Frame4 = ttk.Frame(self)
        self.Frame5 = ttk.Frame(self.Frame4)
        self.Frame5.configure(height='200', relief='flat', width='200') 
        self.Frame5.grid(column='0', row='0')
        self.Frame6 = ttk.Frame(self.Frame4)
        self.Frame6.configure(height='200', relief='flat', width='200')
        self.Frame6.grid(column='1', row='0', sticky='nse')
        self.Frame7 = ttk.Frame(self.Frame4)
        self.Button3 = ttk.Button(self.Frame7)
        self.Button3.configure(text='Regresar', command=self.regresar_modo)
        self.Button3.place(anchor='nw', relx='0.68', rely='0.55', x='0', y='0')
        self.Button4 = ttk.Button(self.Frame7)
        self.Button4.configure(text='Informe', command=self.informe)
        self.Button4.place(anchor='nw', relx='0.68', rely='0.80', x='0', y='0')
        self.Button7 = ttk.Button(self.Frame7)
        self.Button7.configure(text='Calcular', command=self.calcular_funciones)
        self.Button7.place(anchor='nw', relx='0.68', rely='0.3', x='0', y='0')
        
        self.Frame7.configure(height='200', relief='flat', width='200')
        self.Frame7.grid(column='0', columnspan='2', row='1', sticky='ew')
        
        self.Frame4.configure(height='200', width='200')
        self.Frame4.pack(side='top')

        self.Notebook1 = ttk.Notebook(self.Frame5)
        self.Notebook2 = ttk.Notebook(self.Frame6)
    

        self.text_ddt = tk.StringVar()


        self.Frame1 = ttk.Frame(self.Notebook1)
        self.Frame2 = ttk.Frame(self.Notebook1)
        self.Frame3 = ttk.Frame(self.Notebook1)



        ancho_combobox_labelframe1 = "32"
        ancho_combobox_labelframe2 = "31"
        ancho_combobox_labelframe3 = "29"




        self.Labelframe1 = ttk.Labelframe(self.Frame1)
        self.Label1 = ttk.Label(self.Labelframe1)
        self.Label1.configure(text='Longitud:')
        self.Label1.grid(column='0', padx='3', pady='2', row='0', sticky='w')
        self.Labelframe1.rowconfigure('0', pad='0', weight='0')
        self.Label2 = ttk.Label(self.Labelframe1)
        self.Label2.configure(text='Ancho:')
        self.Label2.grid(column='0', padx='3', pady='2', row='1', sticky='w')
        self.Labelframe1.rowconfigure('1', pad='2')
        self.Label3 = ttk.Label(self.Labelframe1)
        self.Label3.configure(text='Altura:')
        self.Label3.grid(column='0', padx='3', pady='2', row='2', sticky='w')
        self.Labelframe1.rowconfigure('2', pad='2')
        self.Label4 = ttk.Label(self.Labelframe1)
        self.Label4.configure(text='Altura  mayor protuberancia:')
        self.Label4.grid(column='0', padx='3', pady='2', row='3', sticky='w')
        self.Labelframe1.rowconfigure('3', pad='2')
        self.Label5 = ttk.Label(self.Labelframe1)
        self.Label5.configure(text='Medida total de la estructura:')
        self.Label5.grid(column='0', padx='3', pady='2', row='4', sticky='w')
        self.Labelframe1.rowconfigure('4', pad='2')
        self.Entry1 = ttk.Entry(self.Labelframe1, textvariable = "1", validate='key', validatecommand=self.vcmd)
        self.Entry1.configure(width='10')
        _text_ = '''35'''
        self.Entry1.delete('0', 'end')
        self.Entry1.insert('0', _text_)
        self.Entry1.grid(column='1', padx='3', row='0', sticky='e')

        self.Labelframe1.columnconfigure('1', pad='0', weight='1')
        self.Entry2 = ttk.Entry(self.Labelframe1, validate='key', validatecommand=self.vcmd)
        self.Entry2.configure(width='10')
        _text_ = '''11'''
        self.Entry2.delete('0', 'end')
        self.Entry2.insert('0', _text_)
        self.Entry2.grid(column='1', padx='3', row='1', sticky='e')
        self.Entry3 = ttk.Entry(self.Labelframe1, validate='key', validatecommand=self.vcmd)
        self.Entry3.configure(width='10')
        _text_ = '''46'''
        self.Entry3.delete('0', 'end')
        self.Entry3.insert('0', _text_)
        self.Entry3.grid(column='1', padx='3', row='2', sticky='e')
        self.Entry4 = ttk.Entry(self.Labelframe1, validate='key', validatecommand=self.vcmd)
        self.Entry4.configure(width='10')
        _text_ = '''45'''
        self.Entry4.delete('0', 'end')
        self.Entry4.insert('0', _text_)
        self.Entry4.grid(column='1', padx='3', row='3', sticky='e')
        self.Entry5 = ttk.Entry(self.Labelframe1)
        self.Entry5.configure(style='Toolbutton', width='10')#(state='disabled', style='Toolbutton', width='10')
        self.Entry5.grid(column='1', padx='3', row='4', sticky='e')
        self.Labelframe1.configure(height='450', text='Dimensiones de la estructura', width='200')
        self.Labelframe1.grid(column='0', padx='10', pady='9', row='0', sticky='ew')
        self.Frame1.columnconfigure('0', weight='0')
        self.Labelframe2 = ttk.Labelframe(self.Frame1)
        # Label_risk_of_fire(r_f)
        self.Label_r_f = ttk.Label(self.Labelframe2)
        self.Label_r_f.configure(text='Riesgo de fuego en la estructura:')
        self.Label_r_f.grid(column='0', padx='3', pady='2', row='0', sticky='w')
        # Label__external_effectiveness
        self.Label_external_effectiveness = ttk.Label(self.Labelframe2)
        self.Label_external_effectiveness.configure(text='Eficacia del apantallamiento:')
        self.Label_external_effectiveness.grid(column='0', padx='3', pady='2', row='1', sticky='w')

        self.Label8 = ttk.Label(self.Labelframe2)
        self.Label8.configure(text='Tipo de cableado interno:')
        self.Label8.grid(column='0', padx='3', pady='2', row='2', sticky='w')
        # Combobox_risk_of_fire
        self.Combobox_r_f = ttk.Combobox(self.Labelframe2)
        self.Combobox_r_f.configure(state='readonly', 
                                 values=['Explosivo', 
                                         'Alto riesgo', 
                                         'Riesgo ordinario', 
                                         'Bajo riesgo', 
                                         'Ninguno'],
                                 width=ancho_combobox_labelframe1)
        self.Combobox_r_f.grid(column='1', padx='3', pady='2', row='0', sticky='e')
        self.Combobox_r_f.current(2)
        # Combobox_risk_of_fire
        self.Labelframe2.columnconfigure('1', weight='1')
        # Combobox_external_effectiveness
        self.Combobox_external_effectiveness = ttk.Combobox(self.Labelframe2)
        self.Combobox_external_effectiveness.configure(state='readonly',
                                                        values=['Escasa', 'Media', 'Buena'],
                                                        width=ancho_combobox_labelframe1)
        self.Combobox_external_effectiveness.grid(column='1', padx='3', pady='2', row='1', sticky='e')
        self.Combobox_external_effectiveness.current(1)

        self.Combobox3 = ttk.Combobox(self.Labelframe2)
        self.Combobox3.configure(state='readonly',
                                 values=['Apantallado', 'No apantallado'],
                                 width=ancho_combobox_labelframe1)
        self.Combobox3.grid(column='1', padx='3', pady='2', row='2', sticky='e')
        self.Combobox3.current(0)
        self.Labelframe2.configure(height='450', text='Riesgo de incendio y daños físicos', width='200')
        self.Labelframe2.grid(column='0', padx='10', pady='9', row='1', sticky='ew')
        self.Labelframe3 = ttk.Labelframe(self.Frame1)
        self.Label_factor_line_density_C_e = ttk.Label(self.Labelframe3)
        self.Label_factor_line_density_C_e.configure(text='Localización relativa:')
        self.Label_factor_line_density_C_e.grid(column='0', padx='3', pady='2', row='0', sticky='w')
        self.Label10 = ttk.Label(self.Labelframe3)
        self.Label10.configure(text='Factor ambiental:')
        self.Label10.grid(column='0', padx='3', pady='2', row='1', sticky='w')
        self.Labelframe3.rowconfigure('1', weight='0')
        self.Frame_ddt = ttk.Frame(self.Frame1)
        self.Frame_ddt.configure(height= 1000, width= 200)
        self.Frame_ddt.grid(column='0', row='3', sticky='ew')
        self.Label_ddt = ttk.Label(self.Frame_ddt)
        self.Label_ddt.configure(text='Densidad de descarga a tierra:')
        self.Label_ddt.grid(column='0', padx='3', row='0')

        self.Entry_ddt_calculado = ttk.Entry(self.Frame_ddt)
        _text_ = '''Calcular'''
        self.Entry_ddt_calculado.delete('0', 'end')
        self.Entry_ddt_calculado.insert('0', _text_)
        self.Entry_ddt_calculado.configure(state='readonly')                    
        self.Entry_ddt_calculado.grid(column='1', padx='3', row='0')

        self.Button_calculo_ddt = ttk.Button(self.Frame_ddt)
        self.Button_calculo_ddt.configure(text='Calcular ddt', command=self.ventana_calcular_DDT)
        self.Button_calculo_ddt.grid(column='2', padx='3', row='0')

        self.Labelframe3.rowconfigure('2', weight='25')
        # Combobox_height_factor_surrounding
        self.Combobox_height_factor_surrounding = ttk.Combobox(self.Labelframe3)
        self.Combobox_height_factor_surrounding.configure(state='readonly',
            values=["Altura menor",
                "Altura similar",
                "Estructura aislada",
                "Sobre una colina"],
            width=ancho_combobox_labelframe1)
        self.Combobox_height_factor_surrounding.grid(column='1', padx='3', row='0', sticky='e')
        self.Combobox_height_factor_surrounding.current(2)
        self.Labelframe3.columnconfigure('1', weight='1')
        # Combobox_factor_line_density_C_e
        self.Combobox_factor_line_density_C_e = ttk.Combobox(self.Labelframe3)
        self.Combobox_factor_line_density_C_e.configure(
            state='readonly',
            values=["Urbano edificios altos",
                    "Urbano",
                    "Suburbano",
                    "Rural"],
            width=ancho_combobox_labelframe1)
        self.Combobox_factor_line_density_C_e.grid(column='1', padx='3', pady='2', row='1', sticky='e')
        self.Combobox_factor_line_density_C_e.current(1)

        self.Label31 = ttk.Label(self.Labelframe3)
        self.Label31.configure(text='Resistividad del terreno [Ω.m]')
        self.Label31.grid(column='0', padx='3', pady='2', row='3', sticky='w')
        self.Labelframe3.rowconfigure('3', weight='25')
        
        
        self.Entry_var_resistividad = ttk.Entry(self.Labelframe3)
        _text_ = '''500'''
        self.Entry_var_resistividad.delete('0', 'end')
        self.Entry_var_resistividad.insert('0', _text_)
        self.Entry_var_resistividad['state'] = 'readonly'
        self.Entry_var_resistividad.grid(column='1', padx='3', pady='2', row='3', sticky='e')
        
        






        self.Radiobutton1 = ttk.Radiobutton(self.Labelframe3)
        
        self.Labelframe3.configure(height='450', text='Influencia ambiental', width='200')
        self.Labelframe3.grid(column='0', padx='10', pady='9', row='2', sticky='ew')
        self.Frame1.configure(height='460', width='200')
        self.Frame1.pack(side='top')

        self.Labelframe4 = ttk.Labelframe(self.Frame2)
        self.Label12 = ttk.Label(self.Labelframe4)
        self.Label12.configure(text='Línea que llega a la self:')
        self.Label12.grid(column='0', padx='3', pady='2', row='0', sticky='w')
        self.Label13 = ttk.Label(self.Labelframe4)
        self.Label13.configure(text='Tipo de cableado externo:')
        self.Label13.grid(column='0', padx='3', pady='2', row='1', sticky='w')
        self.Label14 = ttk.Label(self.Labelframe4)
        self.Label14.configure(text='Existencia de transformador:')
        self.Label14.grid(column='0', padx='3', pady='2', row='2', sticky='w')
        self.Entry28 = ttk.Entry(self.Labelframe4)


        self.Combobox6 = ttk.Combobox(self.Labelframe4)
        self.Combobox6.configure(state='readonly',
            values=["Aerea",
                "Subterránea",
                "Ninguna"],
            width=ancho_combobox_labelframe2)
        self.Combobox6.grid(column='1', padx='3', row='0', sticky='e')
        self.Combobox6.current(0)
        self.Labelframe4.columnconfigure('1', weight='1')
        self.Combobox22 = ttk.Combobox(self.Labelframe4)
        self.Combobox22.configure(state='readonly',
            values=["No apantallado",
                "Apantallado"],
            width=ancho_combobox_labelframe2)
        self.Combobox22.grid(column='1', padx='3', row='1', sticky='e')
        self.Combobox22.current(1)
        self.Combobox23 = ttk.Combobox(self.Labelframe4)
        self.Combobox23.configure(state='readonly',
            values=["Transformador",
                "Sin transformador"],
            width=ancho_combobox_labelframe2)
        self.Combobox23.grid(column='1', padx='3', row='2', sticky='e')
        self.Combobox23.current(0)
        self.Labelframe4.configure(height='200', text='Línea eléctrica', width='200')
        self.Labelframe4.grid(column='0', padx='10', pady='15', row='0', sticky='ew')
        self.Labelframe5 = ttk.Labelframe(self.Frame2)
        self.Label15 = ttk.Label(self.Labelframe5)
        self.Label15.configure(text='Número de servicios conducidos:')
        self.Label15.grid(column='0', padx='3', pady='2', row='0', sticky='w')
        self.Label16 = ttk.Label(self.Labelframe5)
        self.Label16.configure(text='Tipo de cableado externo:')
        self.Label16.grid(column='0', padx='3', pady='2', row='1', sticky='w')
        self.Combobox7 = ttk.Combobox(self.Labelframe5)
        self.Combobox7.configure(state='readonly',
            values=["No apantallado",
                    "Apantallado"],
            width=ancho_combobox_labelframe2)
        self.Combobox7.grid(column='1', padx='3', row='1', sticky='e')
        self.Combobox7.current(0)

        self.Labelframe5.columnconfigure('1', weight='1')
        self.Spinbox1 = ttk.Spinbox(self.Labelframe5)
        self.Spinbox1.configure(width='7', state='readonly', from_=0, to=3, increment=1)
        self.Spinbox1.grid(column='1', padx='3', row='0', sticky='e')


        self.Labelframe5.configure(height='200', text='Otros servicios aéreos', width='200')
        self.Labelframe5.grid(column='0', padx='10', pady='7', row='1', sticky='ew')
        self.Labelframe6 = ttk.Labelframe(self.Frame2)
        self.Label17 = ttk.Label(self.Labelframe6)
        self.Label17.configure(text='Número de servicios conducidos:')
        self.Label17.grid(column='0', padx='3', pady='2', row='0', sticky='w')
        self.Label18 = ttk.Label(self.Labelframe6)
        self.Label18.configure(text='Tipo de cable externo:')
        self.Label18.grid(column='0', padx='3', pady='2', row='1', sticky='w')
        self.Spinbox2 = ttk.Spinbox(self.Labelframe6)
        self.Spinbox2.configure(width='7', state='readonly', from_=0, to=3, increment=1)
        self.Spinbox2.grid(column='1', padx='3', row='0', sticky='e')
        self.Labelframe6.columnconfigure('1', weight='1')
        self.Combobox8 = ttk.Combobox(self.Labelframe6)
        self.Combobox8.configure(state='readonly',
            values=["No apantallado",
                    "Apantallado"],
            width=ancho_combobox_labelframe2)

        self.Combobox8.grid(column='1', padx='3', row='1', sticky='e')
        self.Combobox8.current(1)
        self.Labelframe6.configure(height='200', text='Otros servicios subterráneos', width='200')
        self.Labelframe6.grid(column='0', padx='10', pady='7', row='2', sticky='ew')
        self.Labelframe7 = ttk.Labelframe(self.Frame2)
        self.Label19 = ttk.Label(self.Labelframe7)
        self.Label19.configure(text='Clase de SPSR:')
        self.Label19.grid(column='0', padx='3', pady='2', row='0', sticky='w')
        self.Label20 = ttk.Label(self.Labelframe7)
        self.Label20.configure(text='Protección contra incendios:')
        self.Label20.grid(column='0', padx='3', pady='2', row='1', sticky='w')
        self.Label21 = ttk.Label(self.Labelframe7)
        self.Label21.configure(text='Protección contra sobretensiones:')
        self.Label21.grid(column='0', padx='3', pady='2', row='2', sticky='w')
        self.Combobox9 = ttk.Combobox(self.Labelframe7)
        self.Combobox9.configure(
            state='readonly',
            values=["No Protegida",
                    "Nivel IV",
                    "Nivel III",
                    "Nivel II",
                    "Nivel I"],
            width=ancho_combobox_labelframe2)
        self.Combobox9.grid(column='1', padx='3', row='0', sticky='e')
        self.Combobox9.current(3)
        self.Labelframe7.columnconfigure('1', weight='1')
        self.Combobox10 = ttk.Combobox(self.Labelframe7)
        self.Combobox10.configure(
            state='readonly',
            values=["Sin medida de prevención",
                    "Sistemas manuales",
                    "Sistemas automáticos"],
            width=ancho_combobox_labelframe2)
        self.Combobox10.grid(column='1', padx='3', row='1', sticky='e')
        self.Combobox10.current(1)
        self.Combobox11 = ttk.Combobox(self.Labelframe7)
        self.Combobox11.configure(
            state='readonly',
            values=["Sin medida de prevención",
                    "Solo en entrada de servicios",
                    "Según NTC42305-4"],
            width=ancho_combobox_labelframe2)
        self.Combobox11.grid(column='1', padx='3', row='2', sticky='e')
        self.Combobox11.current(1)
        self.Labelframe7.configure(height='200', text='Medidas de protección', width='200')
        self.Labelframe7.grid(column='0', padx='10', pady='12', row='3', sticky='ew')
        self.Frame2.configure(height='200', width='200')
        self.Frame2.pack(side='top')

        self.Labelframe8 = ttk.Labelframe(self.Frame3)
        self.Label22 = ttk.Label(self.Labelframe8)
        self.Label22.configure(text='Riesgos especiales para la vida:')
        self.Label22.grid(column='0', padx='3', pady='2', row='0', sticky='w')
        self.Labelframe8.rowconfigure('0', weight='0')
        self.Label23 = ttk.Label(self.Labelframe8)
        self.Label23.configure(text='Por incendios:')
        self.Label23.grid(column='0', row='1', sticky='w')
        self.Labelframe8.rowconfigure('1', weight='0')
        self.Label24 = ttk.Label(self.Labelframe8)
        self.Label24.configure(text='Por sobretensiones:')
        self.Label24.grid(column='0', ipadx='2', pady='3', row='2', sticky='w')
        self.Labelframe8.rowconfigure('2', weight='0')
        self.Combobox12 = ttk.Combobox(self.Labelframe8)
        self.Combobox12.configure(
            state='readonly',
            values=["Sin riesgo especial",
                    "Nivel bajo de pánico",
                    "Nivel medio de pánico",
                    "Nivel alto de pánico",
                    "Problemas de evacuación"
                    "Peligro por ambiente alrededor",
                    "Contaminación del ambiente alrededor"],
            width=ancho_combobox_labelframe3)
        self.Combobox12.grid(column='1', padx='3', row='0', sticky='e')
        self.Combobox12.current(3)


        self.Labelframe8.columnconfigure('1', weight='1')
        self.Combobox13 = ttk.Combobox(self.Labelframe8)
        self.Combobox13.configure(
            state='readonly',
            values=["Otras selfs",
                    "Iglesias, museos",
                    "Comercios, colegios",
                    "Hospitales, hoteles"],
            width=ancho_combobox_labelframe3)
        self.Combobox13.grid(column='1', padx='3', row='1', sticky='e')
        self.Combobox13.current(1)

        self.Combobox14 = ttk.Combobox(self.Labelframe8)
        self.Combobox14.configure(
            state='readonly',
            values=["No aplica",
                    "Riesgo de explosión",
                    "Hospitales",
                    "Hay sist. de seguridad críticos"],
            width=ancho_combobox_labelframe3)
        self.Combobox14.grid(column='1', padx='3', row='2', sticky='e')
        self.Combobox14.current(1)


        self.Labelframe8.configure(height='200', text='Tipos de pérdida', width='200')
        self.Labelframe8.grid(column='0', padx='10', pady='15', row='0', sticky='ew')
        self.Labelframe9 = ttk.Labelframe(self.Frame3)
        self.Label25 = ttk.Label(self.Labelframe9)
        self.Label25.configure(text='Por incendios')
        self.Label25.grid(column='0', padx='3', pady='2', row='0', sticky='w')
        self.Label26 = ttk.Label(self.Labelframe9)
        self.Label26.configure(text='Por sobretensiones')
        self.Label26.grid(column='0', padx='3', pady='2', row='1', sticky='w')
        self.Combobox15 = ttk.Combobox(self.Labelframe9)
        self.Combobox15.configure(
            state='readonly',
            values=["No hay servicios esenciales",
                    "Ferrocarril",
                    "Suministro eléctrico",
                    "Telecomunicaciones",
                    "radio y TV",
                    "Suministro de agua",
                    "Suministro de gas"],
            width=ancho_combobox_labelframe3)
        self.Combobox15.grid(column='1', padx='3', row='0', sticky='e')
        self.Combobox15.current(2)

        self.Labelframe9.columnconfigure('1', weight='1')
        self.Combobox16 = ttk.Combobox(self.Labelframe9)
        self.Combobox16.configure(
            state='readonly',
            values=["No hay servicios esenciales",
                    "Ferrocarril",
                    "Suministro eléctrico",
                    "Telecomunicaciones",
                    "radio y TV",
                    "Suministro de agua",
                    "Suministro de gas"],
            width=ancho_combobox_labelframe3)
        self.Combobox16.grid(column='1', padx='3', row='1', sticky='e')
        self.Labelframe9.configure(height='200', text='Pérdida de servicios esenciales', width='200')
        self.Combobox16.current(6)
        self.Labelframe9.grid(column='0', padx='10', pady='8', row='1', sticky='ew')
        self.Labelframe10 = ttk.Labelframe(self.Frame3)
        self.Label27 = ttk.Label(self.Labelframe10)
        self.Label27.configure(text='Por incendio')
        self.Label27.grid(column='0', row='0', sticky='w')
        self.Labelframe10.rowconfigure('0', weight='0')
        self.Combobox21 = ttk.Combobox(self.Labelframe10)
        self.Combobox21.configure(
            state='readonly',
            values=["Sin valor histórico",
                    "Perdidas irremplazables"],
            width=ancho_combobox_labelframe3,)
        self.Combobox21.grid(column='1', padx='3', pady='2', row='0', sticky='e')
        self.Combobox21.current(1)



        self.Labelframe10.columnconfigure('1', weight='1')
        self.Labelframe10.configure(height='200', relief='groove', text='Pérdida del patrimonio cultural', width='200')
        self.Labelframe10.grid(column='0', padx='10', pady='8', row='2', sticky='ew')
        self.Labelframe11 = ttk.Labelframe(self.Frame3)
        self.Label28 = ttk.Label(self.Labelframe11)
        self.Label28.configure(text='Riesgos económicos especiales')
        self.Label28.grid(column='0', padx='3', pady='2', row='0', sticky='w')
        self.Label29 = ttk.Label(self.Labelframe11)
        self.Label29.configure(text='Por incendios')
        self.Label29.grid(column='0', padx='3', pady='2', row='1', sticky='w')
        self.Label30 = ttk.Label(self.Labelframe11)
        self.Label30.configure(text='Por sobretensiones')
        self.Label30.grid(column='0', padx='3', pady='2', row='2', sticky='w')
        self.Label66 = ttk.Label(self.Labelframe11)
        self.Label66.configure(text='Por tension de paso y de contacto:')
        self.Label66.grid(column='0', padx='3', pady='2', row='3', sticky='w')
        self.Label32 = ttk.Label(self.Labelframe11)
        self.Label32.configure(text='Riesgos económicos especiales:')
        self.Label32.grid(column='0', padx='3', pady='2', row='4', sticky='w')



        self.Combobox17 = ttk.Combobox(self.Labelframe11)
        self.Combobox17.configure(
            state='readonly',
            values=["Sin riesgos especiales",
                    "Riesgos medioambientales",
                    "Riesgos  de contaminación"],
            width=ancho_combobox_labelframe3)
        self.Combobox17.grid(column='1', padx='3', row='0')
        self.Combobox17.current(2)
        self.Labelframe11.columnconfigure('1', weight='1')
        self.Combobox18 = ttk.Combobox(self.Labelframe11)
        self.Combobox18.configure(
            state='readonly',
            values=["No aplica",
                    "Otras esctructuras",
                    "Prisión, Iglesia",
                    "Propiedad comercial",
                    "Oficina, escuela",
                    "Propiedad pública",
                    "Hospitales, hoteles",
                    "Museo, Zona Agricola"],
            width=ancho_combobox_labelframe3)
        self.Combobox18.grid(column='1', padx='3', row='1')
        self.Combobox18.current(4)
        self.Combobox19 = ttk.Combobox(self.Labelframe11)
        self.Combobox19.configure(
            state='readonly',
            values=["No aplica",
                    "Otras esctructuras",
                    "Iglesia, Prisión, Zona pública",
                    "Museo, Escuela",
                    "Zona agricola",
                    "Zona Industrial o comercial",
                    "Hospital, hotel, oficina",
                    "Riesgo de explosión"],
            width=ancho_combobox_labelframe3)
        self.Combobox19.grid(column='1', padx='3', row='2')
        self.Combobox19.current(4)
        self.Combobox20 = ttk.Combobox(self.Labelframe11)
        self.Combobox20.configure(
            state='readonly',
            values=["Sin riesgo de Shock",
                    "Ganado en el interior",
                    "Ganado en el exterior"],
            width=ancho_combobox_labelframe3)
        self.Combobox20.grid(column='1', padx='3', row='3')
        self.Combobox20.current(2)
        self.Combobox24 = ttk.Combobox(self.Labelframe11)
        self.Combobox24.configure(
            state='readonly',
            values=["1 en 10 años",
                    "1 en 100 años",
                    "1 en 1000 años",
                    "1 en 10000 años",
                    "1 en 100000 años"],
            width=ancho_combobox_labelframe3)
        self.Combobox24.grid(column='1', padx='3', row='4')
        self.Combobox24.current(1)
        self.Labelframe11.configure(height='200', text='Pérdidas económicas', width='200')
        self.Labelframe11.grid(column='0', padx='10', pady='10', row='3', sticky='ew')
        self.Frame3.configure(height='200', relief='flat', width='200')
        self.Frame3.pack(side='top')

        self.Frame9 = ttk.Frame(self.Notebook2)
        self.Label65 = ttk.Label(self.Frame9)
        self.img_1 = tk.PhotoImage(file='archivos\plot.png')
        self.Label65.configure(image=self.img_1, text='Label65')
        self.Label65.pack(padx='10', pady='10', side='top')
        self.Frame9.configure(height='200', width='480')
        self.Frame9.pack(side='top')

        self.Frame10 = ttk.Frame(self.Notebook2)
        self.Labelframe12 = ttk.Labelframe(self.Frame10)
        self.Label39 = ttk.Label(self.Labelframe12)
        self.Label39.configure(text='Proyecto:')
        self.Label39.grid(column='0', padx='10', pady='5', row='0', sticky='sew')
        self.Labelframe12.rowconfigure('0', pad='3')
        self.Label40 = ttk.Label(self.Labelframe12)
        self.Label40.configure(text='diseñador:')
        self.Label40.grid(column='0', padx='10', pady='5', row='1', sticky='sew')
        self.Labelframe12.rowconfigure('1', pad='3')
        self.Label41 = ttk.Label(self.Labelframe12)
        self.Label41.configure(text='Dirección:')
        self.Label41.grid(column='0', padx='10', pady='5', row='2', sticky='sew')
        self.Labelframe12.rowconfigure('2', pad='3')
        self.Label42 = ttk.Label(self.Labelframe12)
        self.Label42.configure(text='Telefono:')
        self.Label42.grid(column='0', padx='10', pady='5', row='3', sticky='sew')
        self.Labelframe12.rowconfigure('3', pad='3', weight='0')
        self.Label43 = ttk.Label(self.Labelframe12)
        self.Label43.configure(text='Descripción:')
        self.Label43.grid(column='0', padx='10', pady='5', row='4', sticky='sew')
        self.Labelframe12.rowconfigure('4', pad='3', weight='0')
        self.Entry6 = ttk.Entry(self.Labelframe12)


        self.Entry6.grid(column='1', padx='10', row='0', sticky='sew')
        self.Labelframe12.columnconfigure('1', pad='3', weight='1')
        self.Entry8 = ttk.Entry(self.Labelframe12)
        self.Entry8.grid(column='1', padx='10', row='1', sticky='sew')
        self.Entry9 = ttk.Entry(self.Labelframe12)
        self.Entry9.grid(column='1', padx='10', row='2', sticky='sew')
        self.Entry10 = ttk.Entry(self.Labelframe12)
        self.Entry10.grid(column='1', padx='10', row='3', sticky='sew')
        self.Entry11 = ttk.Entry(self.Labelframe12)
        self.Entry11.grid(column='1', padx='10', pady='8', row='4', sticky='sew')
        self.Labelframe12.configure(height='200', relief='groove', text='Datos del proyecto', width='200')
        self.Labelframe12.grid(column='0', padx='15', pady='15', row='0', sticky='ew')
        self.Frame10.rowconfigure('0', weight='0')
        self.Frame10.columnconfigure('0', weight='1')
        self.Frame10.configure(height='200', width='200')
        self.Frame10.pack(side='top')



























        self.Labelframe13 = ttk.Labelframe(self.Frame7)


        self.Label44 = ttk.Label(self.Labelframe13)
        self.Label44.configure(text='Perdidas de vidas humanas:')
        self.Label44.grid(column='0', padx='5', pady='2', row='1', sticky='w')
        self.Label45 = ttk.Label(self.Labelframe13)
        self.Label45.configure(text='Perdida de servicios públicos:')
        self.Label45.grid(column='0', padx='5', pady='2', row='2', sticky='w')
        self.Label46 = ttk.Label(self.Labelframe13)
        self.Label46.configure(text='Perdida de patrimonio:')
        self.Label46.grid(column='0', padx='5', pady='2', row='3', sticky='w')
        self.Label47 = ttk.Label(self.Labelframe13)
        self.Label47.configure(text='Perdidas económicas:')
        self.Label47.grid(column='0', padx='5', pady='2', row='4', sticky='w')

        self.Entry_var_max_human_Loss = ttk.Entry(self.Labelframe13)
        self.Entry_var_max_human_Loss.configure(width='10')
        _text_ = '''1.00E-5'''
        self.Entry_var_max_human_Loss.insert('0', _text_)
        self.Entry_var_max_human_Loss['state'] = 'readonly'
        self.Entry_var_max_human_Loss.grid(column='1', row='1')
        self.Entry_var_max_loss_esencial_service = ttk.Entry(self.Labelframe13)
        self.Entry_var_max_loss_esencial_service.configure(width='10')
        _text_ = '''1.00E-3'''
        self.Entry_var_max_loss_esencial_service.insert('0', _text_)
        self.Entry_var_max_loss_esencial_service['state'] = 'readonly'
        self.Entry_var_max_loss_esencial_service.grid(column='1', row='2')
        self.Entry_var_max_loss_cultural = ttk.Entry(self.Labelframe13)
        self.Entry_var_max_loss_cultural.configure(width='10')
        _text_ = '''1.00E-3'''
        self.Entry_var_max_loss_cultural.insert('0', _text_)
        self.Entry_var_max_loss_cultural['state'] = 'readonly'
        self.Entry_var_max_loss_cultural.grid(column='1', row='3')
        self.Entry_var_max_loss_economic = ttk.Entry(self.Labelframe13)
        self.Entry_var_max_loss_economic.configure(width='10')
        _text_ = '''1.00E-3'''
        self.Entry_var_max_loss_economic.insert('0', _text_)
        self.Entry_var_max_loss_economic['state'] = 'readonly'
        self.Entry_var_max_loss_economic.grid(column='1', padx='3', pady='4', row='4')


        self.Label48 = ttk.Label(self.Labelframe13)
        self.Label48.configure(text='  =>')
        self.Label48.grid(column='2', padx='3', row='1')
        self.Label49 = ttk.Label(self.Labelframe13)
        self.Label49.configure(text='  =>')
        self.Label49.grid(column='2', padx='3', row='2')
        self.Label50 = ttk.Label(self.Labelframe13)
        self.Label50.configure(text='  =>')
        self.Label50.grid(column='2', padx='3', row='3')
        self.Label51 = ttk.Label(self.Labelframe13)
        self.Label51.configure(text='  =>')
        self.Label51.grid(column='2', padx='3', row='4')
        self.Entry16 = ttk.Entry(self.Labelframe13)
        self.Entry16.configure(width='10')
        self.Entry16.grid(column='3', row='1')
        self.Entry17 = ttk.Entry(self.Labelframe13)
        self.Entry17.configure(width='10')
        self.Entry17.grid(column='3', row='2')
        self.Entry18 = ttk.Entry(self.Labelframe13)
        self.Entry18.configure(width='10')
        self.Entry18.grid(column='3', row='3')
        self.Entry19 = ttk.Entry(self.Labelframe13)
        self.Entry19.configure(width='10')
        self.Entry19.grid(column='3', row='4')
        self.Label53 = ttk.Label(self.Labelframe13)
        self.Label53.configure(text='  +')
        self.Label53.grid(column='4', padx='3', row='1')
        self.Label54 = ttk.Label(self.Labelframe13)
        self.Label54.configure(text='  +')
        self.Label54.grid(column='4', padx='3', row='2')
        self.Label55 = ttk.Label(self.Labelframe13)
        self.Label55.configure(text='  +')
        self.Label55.grid(column='4', padx='3', row='3')
        self.Label56 = ttk.Label(self.Labelframe13)
        self.Label56.configure(text='  +')
        self.Label56.grid(column='4', padx='3', row='4')
        self.Entry20 = ttk.Entry(self.Labelframe13)
        self.Entry20.configure(width='10')
        self.Entry20.grid(column='5', row='1')
        self.Entry21 = ttk.Entry(self.Labelframe13)
        self.Entry21.configure(width='10')
        self.Entry21.grid(column='5', row='2')
        self.Entry22 = ttk.Entry(self.Labelframe13)
        self.Entry22.configure(width='10')
        self.Entry22.grid(column='5', row='3')
        self.Entry23 = ttk.Entry(self.Labelframe13)
        self.Entry23.configure(width='10')
        self.Entry23.grid(column='5', row='4')
        self.Label57 = ttk.Label(self.Labelframe13)
        self.Label57.configure(text='=')
        self.Label57.grid(column='6', padx='3', row='1')
        self.Label58 = ttk.Label(self.Labelframe13)
        self.Label58.configure(text='=')
        self.Label58.grid(column='6', padx='3', row='2')
        self.Label59 = ttk.Label(self.Labelframe13)
        self.Label59.configure(text='=')
        self.Label59.grid(column='6', padx='3', row='3')
        self.Label60 = ttk.Label(self.Labelframe13)
        self.Label60.configure(text='=')
        self.Label60.grid(column='6', padx='3', row='4')
        self.Entry24 = ttk.Entry(self.Labelframe13)
        self.Entry24.configure(width='10')
        self.Entry24.grid(column='7', padx='6', row='1')
        self.Entry25 = ttk.Entry(self.Labelframe13)
        self.Entry25.configure(width='10')
        self.Entry25.grid(column='7', padx='6', pady='4', row='2')
        self.Entry26 = ttk.Entry(self.Labelframe13)
        self.Entry26.configure(width='10')
        self.Entry26.grid(column='7', padx='6', row='3')
        self.Entry27 = ttk.Entry(self.Labelframe13)
        self.Entry27.configure(width='10')
        self.Entry27.grid(column='7', padx='6', row='4')
        self.Label61 = ttk.Label(self.Labelframe13)
        self.Label61.configure(text='  Riesgo \n tolerable')
        self.Label61.grid(column='1', row='0')
        self.Label62 = ttk.Label(self.Labelframe13)
        self.Label62.configure(text='    Riesgo por \n impacto directo')
        self.Label62.grid(column='3', row='0')
        self.Label63 = ttk.Label(self.Labelframe13)
        self.Label63.configure(text='     Riesgo por \n impacto indirecto')
        self.Label63.grid(column='5', row='0')
        self.Label64 = ttk.Label(self.Labelframe13)
        self.Label64.configure(text='  Riesgo \n calculado')
        self.Label64.grid(column='7', pady='5', row='0')
        self.Labelframe13.configure(height='600', text='Riesgos calculados', width='600')
        self.Labelframe13.pack(padx='10', side='left')





        self.Notebook1.add(self.Frame1, text='Tab1')
        self.Notebook1.add(self.Frame2, text='Tab2')
        self.Notebook1.add(self.Frame3, text='Tab3')
        self.Notebook1.configure(height='450', width='530')
        self.Notebook1.pack(anchor='ne', padx='10', pady='10', side='left')
        

        self.Notebook2.add(self.Frame9, text='Tab4')
        self.Notebook2.add(self.Frame10, text='Tab5')
        self.Notebook2.configure(height='450', width='500')
        self.Notebook2.pack(padx='10', pady='10', side='top')
        self.Notebook2.bind('<Button-1>', self.on_click)  

    def on_click(self, event):
        self.Entry6.delete(0, "end")
        self.Entry8.delete(0,"end")
        self.Entry9.delete(0,"end")
        self.Entry10.delete(0,"end")
        self.Entry11.delete(0,"end")

        self.Entry6.insert(0,papo['proyecto'])
        self.Entry8.insert(0,papo['disenador'])
        self.Entry9.insert(0,papo['direccion'])
        self.Entry10.insert(0,papo['telefono'])
        self.Entry11.insert(0,papo['descripcion'])


    def regresar_modo(self):
        print(papo)

        self.anterior_modo()


    def calcular_funciones(self):
        self.calcular_DDT()
        self.calcular_L_W_H_H_H_p()



        self.calcular_K_s3()
        self.calcular_pl()
        self.calcular_P_LD0()
        self.calcular_C_t0()
        self.calcular_n_oh()
        self.calcular_n_ug()
        self.calcular_P_LD1()
        self.calcular_P_LD2()
        self.calcular_h_1()
        self.calcular_L_f1()
        self.calcular_L_o1()
        self.calcular_L_f2()
        self.calcular_L_o2()
        self.calcular_L_f3()
        self.calcular_h4()
        self.calcular_L_f4()
        self.calcular_L_o4()
        self.calcular_L_t4()
        self.calcular_R_T4()
        self.calcular_E()
        self.calcular_r()
        self.calcular_SP()
        self.calcular_3_1()
        self.calcular_3_2()
        self.calcular_4()       
        self.calcular_4_1()
        self.calcular_4_2()
        self.calcular_5() 
        self.calcular_5_1()
        self.calcular_5_2()
        self.calcular_6_1()
        self.calcular_6_2()
        self.calcular_6_3()
        self.calcular_6_4()
        self.calcular_6_5()
        self.calcular_6_6()
        self.calcular_6_7()      
        self.calcular_6_8()
        self.calcular_6_9()
        self.calcular_6_10()
        self.calcular_7_1()
        self.calcular_7_2()
        self.calcular_7_3()
        self.calcular_7_4()
        self.calcular_7_5()
        self.calcular_7_6()
        self.calcular_7_7()
        self.calcular_8_1()
        self.calcular_8_2()
        self.calcular_8_3()
        self.calcular_9_1()
        self.calcular_9_2()
        self.calcular_9_3()
        self.calcular_9_4()
        self.calcular_9_5()
        self.calcular_9_6()
        self.calcular_9_7()
        self.calcular_9_8()
        self.calcular_9_9()
        #self.changeText()       
        self.valores()


    def informe(self):
        self.calcular_informe()

    #sirve para verificar que sean numeros los que se ingresan
    def check(self, d, i, P, s, S, v, V, W):

        text = P  #e.get()
        parts = text.split('.')
        parts_number = len(parts)

        if parts_number > 2:
            #print('too much dots')
            return False

        if parts_number > 1 and parts[1]: # don't check empty string
            if not parts[1].isdecimal() or len(parts[1]) > 2:
                #print('wrong second part')
                return False

        if parts_number > 0 and parts[0]: # don't check empty string
            if not parts[0].isdecimal() or len(parts[0]) > 4:
                #print('wrong first part')
                return False

        return True

    def ventana_calcular_DDT(self):
        Calculo_DDT(master=self.master, retornar = self.retorno_calculo_ddt)

    def retorno_calculo_ddt(self, ddt_retorno):
        VAR["DDT"] = ddt_retorno
        self.Entry_ddt_calculado['state'] = 'normal'
        self.Entry_ddt_calculado.delete('0', 'end')
        self.Entry_ddt_calculado.insert('0', VAR["DDT"])
        self.Entry_ddt_calculado.configure(state='readonly') 

    def obtener_valores(self):
        VAR["L"] = float(self.Entry1.get())
        VAR["W"] = float(self.Entry2.get())
        VAR["H"] = float(self.Entry3.get())
        VAR["H_P"] = float(self.Entry4.get())














##############################################################
#FUNCIONES STRUCTURAL DIMENSIONS
##############################################################

    def calcular_L_W_H_H_H_p(self, *args):
        VAR["L"] = float(self.Entry1.get())
        VAR["W"] = float(self.Entry2.get())
        VAR["H"] = float(self.Entry3.get())
        VAR["H_P"] = float(self.Entry4.get())


        collect_data_entry = DataEntryRiskTable()
        VAR["r_f"] = collect_data_entry.get_risk_of_fire(self.Combobox_r_f.current())
        VAR["Ks1"] = collect_data_entry.get_external_effectiveness(self.Combobox_external_effectiveness.current())
        VAR["Ks2"] = collect_data_entry.get_internal_effectiveness()
        VAR["P_A"] = collect_data_entry.get_shock_prob_humans_animals()
        VAR["D_m"] = collect_data_entry.get_lightning_strike_distance()
        VAR["C_d"] = collect_data_entry.get_height_factor_surrounding(
                                        self.Combobox_height_factor_surrounding.current()
                                        )
        VAR["C_e"] = collect_data_entry.get_factor_line_density_C_e(
                                        self.Combobox_factor_line_density_C_e.current()
                                        )
        # Se calcual DDT en calcular_DDT



        print(VAR["C_e"])
        print(VAR["C_e"])



    def calcular_DDT(self, *args):
        try:
            VAR["DDT"] = float(self.Entry_ddt_calculado.get())
        except:
            messagebox.showinfo(message="Debe ingresar la Densidad de descarga a tierra ",
                                 title="Algo raro por aquí")       




# =============================================================================
# FUNCIONES BUILDING WIRING
# =============================================================================
    '''Factor de características del cableado interno véase la Tabla 17'''
    def calcular_K_s3(self, *args):
        if self.Combobox3.current() == 0:
            VAR["Ks3"] = 0.1
        elif self.Combobox3.current() == 1:
            VAR["Ks3"] = 1


# =============================================================================
# FUNCIONES CONDUCTIVE SERVICE LINES
# =============================================================================
        '''Power Lines'''

    def calcular_pl(self, *args):
        if self.Combobox6.current() == 0:
            VAR["pl"] = 1
        elif self.Combobox6.current() == 1:
            VAR["pl"] = 2
        elif self.Combobox6.current() == 2:
            VAR["pl"] = 0


    def calcular_P_LD0(self, *args):
        if self.Combobox22.current() == 0:
            VAR["P_LD0"] = 1
        elif self.Combobox22.current() == 1:
            VAR["P_LD0"] = 0.4

#Tabla 11. Factor de corrección por presencia de transformador'''
    def calcular_C_t0(self, *args):
        if self.Combobox23.current() == 0:
            VAR["C_t0"] = 0.2

        elif self.Combobox23.current() == 1:
            VAR["C_t0"] = 1


        '''Other Overhead Service Lines:'''

    def calcular_n_oh(self, *args):
        try:
            VAR["n_oh"] = float(self.Spinbox1.get())

        except ValueError:
            VAR["n_oh"] = 0

    def calcular_n_ug(self, *args):
        try:
            VAR["n_ug"] = float(self.Spinbox2.get())

        except ValueError:
            VAR["n_ug"] = 0


    def calcular_P_LD1(self, *args):
        if self.Combobox7.current() == 0:
            VAR["P_LD1"] = 1
        elif self.Combobox7.current() == 1:
            VAR["P_LD1"] = 0.4


        '''Conductive Underground Services - Electrical Services e.g.
        Communication Lines'''



    def calcular_P_LD2(self, *args):
        if self.Combobox8.current() == 0:
            VAR["P_LD2"] = 1
        elif self.Combobox8.current() == 1:
            VAR["P_LD2"] = 0.4


# =============================================================================
# FUNCIONES ACCEPTABLE RISK & LOSS CATEGORIES
# =============================================================================
        '''Loss Category 1 - Loss of Human Life'''
    def calcular_h_1(self, *args):
        if self.Combobox12.current() == 0:
            VAR["h_1"] = 1
        elif self.Combobox12.current() == 1:
            VAR["h_1"] = 2
        elif self.Combobox12.current() == 2:
            VAR["h_1"] = 5
        elif self.Combobox12.current() == 3:
            VAR["h_1"] = 10
        elif self.Combobox12.current() == 4:
            VAR["h_1"] = 5
        elif self.Combobox12.current() == 5:
            VAR["h_1"] = 20
        elif self.Combobox12.current() == 6:
            VAR["h_1"] = 50

    def calcular_L_f1(self, *args):
        if self.Combobox13.current() == 0:
            VAR["L_f1"] = 0.01
        if self.Combobox13.current() == 1:
            VAR["L_f1"] = 0.02
        if self.Combobox13.current() == 2:
            VAR["L_f1"] = 0.05
        elif self.Combobox13.current() == 3:
            VAR["L_f1"] = 0.1

    def calcular_L_o1(self, *args):
        if self.Combobox14.current() == 0:
            VAR["L_o1"] = 0
        if self.Combobox14.current() == 1:
            VAR["L_o1"] = 0.1
        elif self.Combobox14.current() == 2:
            VAR["L_o1"] = 0.001
        elif self.Combobox14.current() == 3:
            VAR["L_o1"] = 0.00001
        elif self.Combobox14.current() == 4:
            VAR["L_o1"] = 10 **(-4)


        '''Loss Category 2 - Loss of Essential Service to the Public'''
    def calcular_L_f2(self, *args):
        if self.Combobox15.current() == 0:
            VAR["L_f2"] = 0
        if self.Combobox15.current() == 1:
            VAR["L_f2"] = 0.01
        elif self.Combobox15.current() == 2:
            VAR["L_f2"] = 0.01
        elif self.Combobox15.current() == 3:
            VAR["L_f2"] = 0.01
        elif self.Combobox15.current() == 4:
            VAR["L_f2"] = 0.01
        elif self.Combobox15.current() == 5:
            VAR["L_f2"] = 0.1
        elif self.Combobox15.current() == 6:
            VAR["L_f2"] = 0.1

    def calcular_L_o2(self, *args):
        if self.Combobox16.current() == 0:
            VAR["L_o2"] = 0
        if self.Combobox16.current() == 1:
            VAR["L_o2"] = 0.001
        elif self.Combobox16.current() == 2:
            VAR["L_o2"] = 0.001
        elif self.Combobox16.current() == 3:
            VAR["L_o2"] = 0.001
        elif self.Combobox16.current() == 4:
            VAR["L_o2"] = 0.001
        elif self.Combobox16.current() == 5:
            VAR["L_o2"] = 0.01
        elif self.Combobox16.current() == 6:
            VAR["L_o2"] = 0.01

        '''Loss Category 3 - Loss of Cultural Heritage'''
    def calcular_L_f3(self, *args):
        if self.Combobox21.current() == 0:
            VAR["L_f3"] = 0
        elif self.Combobox21.current() == 1:
            VAR["L_f3"] = 0.1

        '''Loss Category 4 - Economic Loss'''

    def calcular_h4(self, *args):
        if self.Combobox17.current() == 0:
            VAR["h4"] = 1
        elif self.Combobox17.current() == 1:
            VAR["h4"] = 20
        elif self.Combobox17.current() == 2:
            VAR["h4"] = 50

    def calcular_L_f4(self, *args):
        if self.Combobox18.current() == 0:
            VAR["L_f4"]    = 0
        elif self.Combobox18.current() == 1:
            VAR["L_f4"] = 0.1
        elif self.Combobox18.current() == 2:
            VAR["L_f4"] = 0.2
        elif self.Combobox18.current() == 3:
            VAR["L_f4"] = 0.2
        elif self.Combobox18.current() == 4:
            VAR["L_f4"] = 0.2
        elif self.Combobox18.current() == 5:
            VAR["L_f4"] = 0.2
        elif self.Combobox18.current() == 6:
            VAR["L_f4"] = 0.5
        elif self.Combobox18.current() == 7:
            VAR["L_f4"] = 0.5
        elif self.Combobox18.current() == 8:
            VAR["L_f4"] = 0.5

    def calcular_L_o4(self, *args):
        if self.Combobox19.current() == 0:
            VAR["L_o4"] = 0
        elif self.Combobox19.current() == 1:
            VAR["L_o4"] = 0.0001
        elif self.Combobox19.current() == 2:
            VAR["L_o4"] = 0.001
        elif self.Combobox19.current() == 3:
            VAR["L_o4"] = 0.001
        elif self.Combobox19.current() == 4:
            VAR["L_o4"] = 0.001
        elif self.Combobox19.current() == 5:
            VAR["L_o4"] = 0.01
        elif self.Combobox19.current() == 6:
            VAR["L_o4"] = 0.01
        elif self.Combobox19.current() == 7:
            VAR["L_o4"] = 0.1

    def calcular_L_t4(self, *args):
        if self.Combobox20.current() == 0:
            VAR["L_t4"] = 0
        elif self.Combobox20.current() == 1:
            VAR["L_t4"] = 1 * 10**(-2)
        elif self.Combobox20.current() == 2:
            VAR["L_t4"] = 1 * 10**(-2)

    def calcular_R_T4(self, *args):
        if self.Combobox24.current() == 0:
            VAR["R_T4"] = 0.1
        elif self.Combobox24.current() == 1:
            VAR["R_T4"] = 1 * 10**(-2)
        elif self.Combobox24.current() == 2:
            VAR["R_T4"] = 1 * 10**(-3)
        elif self.Combobox24.current() == 3:
            VAR["R_T4"] = 1 * 10**(-5)
        elif self.Combobox24.current() == 4:
            VAR["R_T4"] = 1 * 10**(-5)


# =============================================================================
# FUNCIONESPROTECTION MEASURES IMPLEMENTED
# =============================================================================

    def calcular_E(self, *args):
        if self.Combobox9.current() == 0:
            VAR["E"] = 0
        elif self.Combobox9.current() == 1:
            VAR["E"] = 0.8
        elif self.Combobox9.current() == 2:
            VAR["E"] = 0.9
        elif self.Combobox9.current() == 3:
            VAR["E"] = 0.95
        elif self.Combobox9.current() == 4:
            VAR["E"] = 0.98

    def calcular_r(self, *args):
        if self.Combobox10.current() == 0:
            VAR["r"] = 1
        elif self.Combobox10.current() == 1:
            VAR["r"] = 0.5
        elif self.Combobox10.current() == 2:
            VAR["r"] = 0.2

    def calcular_SP(self, *args):
        if self.Combobox11.current() == 0:
            VAR["SP"] = 0
        elif self.Combobox11.current() == 1:
            VAR["SP"] = 1
        elif self.Combobox11.current() == 2:
            VAR["SP"] = 2


# =============================================================================
# 3.1. Direct Strikes to the Structure
# =============================================================================

    def calcular_3_1(self, *args):
        #ecu (6) pag. 35
        if VAR["H"]> VAR["H_P"] or VAR["H"] == VAR["H_P"]:
            VAR["A_d"] = ((VAR["L"]  * VAR["W"]) 
                            + (6 * VAR["H"] * (VAR["L"] + VAR["W"])) 
                            + (9 * math.pi * VAR["H"] ** 2))
        elif VAR["H"] < VAR["H_P"]:
            VAR["A_d"] = (9 * math.pi * VAR["H_P"] ** 2 )


        _text_ = round(VAR["A_d"], 3)
        self.Entry5.delete('0', 'end')
        self.Entry5.insert('0', _text_)


        VAR["N_g"] = VAR["DDT"]
        #ecu 5 pag. 34
        VAR["N_D"] = (VAR["N_g"] * VAR["A_d"] * VAR["C_d"] *10**(-6))


# =============================================================================
# 3.2. Indirect Strikes to the Structure
# =============================================================================

    def calcular_3_2(self, *args):
        
        '''cambio
        self.A_m = round((self.L * self.W) 
                              + (2 * self.D_m ) * (self.L + self.W) 
                              + (math.pi * (self.D_m ** 2) 
                              - self.A_d * self.C_d), 3)'''


        VAR["A_m"] = (2 * VAR["L"] * VAR["D_m"] 
                        + 2 * VAR["W"]  * VAR["D_m"]
                        + math.pi * (VAR["D_m"] ** 2))

        
        if VAR["A_m"] < 0:
            VAR["A_m"] = 0
        else:
            pass


        #ecu (8) pag. 37
        '''cambio
        self.N_M = self.N_g * self.A_m *10**(-6)'''
        VAR["N_M"] = (VAR["N_g"] 
                        * (VAR["A_m"] - VAR["A_d"] * VAR["C_d"] )
                        * 10**(-6))


# =============================================================================
# 4. OVERHEAD SERVICE LINES
# =============================================================================

    # def calcular_4(self, *args):
    #     if self.C_e > 0.5:
    #         self.L_1 = 1000
    #     elif self.C_e > 0:
    #         self.L_1 = 500
    #     else:
    #         self.L_1 = 75

    def calcular_4(self, *args):
        if VAR["C_e"] > 0.5:
            VAR["L_1"] = 1000
            VAR["L_2"] = 1000
        elif VAR["C_e"] > 0:
            VAR["L_1"] = 1000
            VAR["L_2"] = 1000
        else:
            VAR["L_1"] = 1000
            VAR["L_2"] = 1000            
        if VAR["pl"] == 1:
            VAR["n_ohp"] = 1
        else:
            VAR["n_ohp"] = 0

#==============================================================================
# 4.1. Direct Strikes to Overhead Lines
# =============================================================================
    def calcular_4_1(self, *args):
        VAR["D_c1"] = 3 * VAR["H_c1"]    
        
        VAR["L_c1"] = VAR["L_1"] - 3 * VAR["H"] - 3 * VAR["h_a1"]
        if VAR["L_c1"] == 0:
            VAR["L_c1"] = 0
            '''cambio el signo
            elif self.L_c1 > 0:'''
        elif VAR["L_c1"] < 0:
            VAR["L_c1"] = 0
        
        #Tabla 12 AI, pag. 37
        VAR["A_c1"] =  2 * VAR["D_c1"] * VAR["L_c1"] 

        VAR["a1"] = (VAR["l_a1"] * VAR["w_a1"] 
                       + 6 * VAR["h_a1"] * (VAR["l_a1"] + VAR["w_a1"]) 
                       + 9 * math.pi * VAR["h_a1"]**2)
        
        VAR["N_L1p"] = VAR["N_g"] * VAR["A_c1"] * VAR["C_t0"] * VAR["C_d"] *10**(-6)   # ct = 0,2

        VAR["N_L1"] = VAR["N_g"] * VAR["A_c1"] * VAR["C_t1"] * VAR["C_d"] *10**(-6) # ct1 = 1



# =============================================================================
# 4.2. Indirect Strikes to Overhead Lines
# =============================================================================

    def calcular_4_2 (self, *args):
        #es igual a L_c, pag. 37
        #Tabla 12 Ai, pag. 38
        VAR["A_l1"] = 2 * VAR["D_L1"] * VAR["L_1"]
        VAR["N_I1p"] = (VAR["N_g"]
                          * VAR["A_l1"] 
                          * VAR["C_t0"] 
                          * VAR["C_e"] 
                          * 10**(-6))

        VAR["N_I1"] =  (VAR["N_g"]
                          * VAR["A_l1"] 
                          * VAR["C_t1"] 
                          * VAR["C_e"]
                          * 10**(-6))


# =============================================================================
# 5. UNDERGROUND SERVICE LINES
# =============================================================================
    def calcular_5(self, *args):
        if VAR["pl"] == 2:
            VAR["n_ugp"] = 1
        else:
            VAR["n_ugp"] = 0


# =============================================================================
# 5.1. Direct Strikes to Underground Service Lines
# =============================================================================

    def calcular_5_1 (self, *args):
        '''#cambio              
        # self.L_c2 = self.L_2 - 3 * self.H - 3 * self.h_a2'''
        VAR["L_c2"] = VAR["L_2"]


        '''#cambio
        VAR["A_c2"] = 2 * VAR["D_c1"] * VAR["L_c2"] '''

        VAR["A_c2"] = (VAR["L_c2"] - 3 *(VAR["h_a2"] + VAR["H"])) * math.isqrt(VAR["P_2"])
        
        VAR["A_a2"] = (VAR["l_a2"] * VAR["w_a2"] 
                         + 6 * VAR["h_a2"] * (VAR["l_a2"] + VAR["w_a2"]) 
                         + 9 * math.pi * VAR["h_a2"] **2)
        
        
        VAR["N_L2p"] = (VAR["N_g"]
                          * VAR["A_c2"] 
                          * VAR["C_t0"] 
                          * VAR["C_d"]
                          * 10**(-6))
        
        VAR["N_L2"] = (VAR["N_g"]
                         * VAR["A_c2"] 
                         * VAR["C_t2"] 
                         * VAR["C_d"]  
                         * 10**(-6)) 
        

# =============================================================================
# 5.2. Indirect Strikes to Underground Service Lines
# =============================================================================
    def calcular_5_2 (self, *args):
        #es igual a L_c, pag. 37
        #Tabla 12 Ai, pag. 38
        '''cambio
        self.A_l2 = 2 * self.D_c1 * self.L_2'''
        VAR["A_l2"] = 25 * VAR["L_c2"] * math.isqrt(VAR["P_2"])
        VAR["N_I2p"] = (VAR["N_g"]
                            * VAR["A_l2"] 
                            * VAR["C_t0"] 
                            * VAR["C_e"]
                            * 10**(-6))
        #para líneas aereas auxiliares
        #ecu. 10 pag. 39
        VAR["N_I2"] = (VAR["N_g"]
                         * VAR["A_l2"] 
                         * VAR["C_t2"] 
                         * VAR["C_e"]
                         * 10**(-6))

# =============================================================================
# 6. RISK CALCULATIONS FOR LOSS CATEGORY 1 - LOSS OF HUMAN LIFE
# 6.1. Risk of dangerous step & touch potential inside & outside structure due
# to direct strikes to the structure
# =============================================================================

    def calcular_6_1 (self, *args):
        #(16) pag.49
        VAR["L_a1"] = VAR["R_a"] * VAR["L_t1"]
        # Tabla 8
        VAR["R_A1"] = VAR["N_D"] * VAR["P_A"] * VAR["L_a1"]


# =============================================================================
# 6.2. Risk of physical destruction due to fire, explosion, mechanical damage
# and chemical
# discharge due to direct strikes to the structure
# =============================================================================

    def calcular_6_2 (self, *args):
        VAR["L_B1"] = (VAR["r"]                       
                        * VAR["h_1"]
                        * VAR["r_f"]
                        * VAR["L_f1"])

        VAR["P_B1"] = 1 - VAR["E"]
        VAR["R_B1"] = VAR["N_D"] * VAR["P_B1"] * VAR["L_B1"]

# =============================================================================
# 6.3. Surge Protection Considerations
# =============================================================================
    def calcular_6_3 (self, *args):
        VAR["P_SPD"] = 0
        VAR["P_EB"] = 0 
        
        if VAR["P_B1"] > 0.3:
            VAR["P_SPD"] = 1
        elif VAR["P_B1"] > 0.06:
            VAR["P_SPD"] = 0.03
        elif VAR["P_B1"] > 0.03:            
            VAR["P_SPD"] = 0.02
        else:
            VAR["P_SPD"] = 0.01   
            
        VAR["P_EB"] = VAR["P_SPD"]
        '''cambio
        if VAR["SP >"] 0:'''
        if VAR["SP"] == 0:
            VAR["P_EB"] = 1
        else:
            pass
        
        if VAR["SP"] < 2:
            VAR["P_SPD"] = 1
        else:
            pass

# =============================================================================
# 6.4. Risk of electrical/electronic equipment malfunction or failure due to 
# overvoltages from direct strikes to the structure
# =============================================================================

    def calcular_6_4 (self, *args):
        VAR["P_C1"] = VAR["P_SPD"]
        VAR["L_C1"] = VAR["L_o1"]
        VAR["R_C1"] = VAR["N_D"] * VAR["P_C1"] * VAR["L_C1"]     


# =============================================================================
# 6.5. Risk of electrical/electronic equipment function or failure due to 
# overvoltages from indirect strikes to the structure
# =============================================================================
    def calcular_6_5(self, *args):
        VAR["K_MS1"] = (VAR["Ks1"]                         
                                * VAR["Ks2"]
                                * VAR["Ks3"] 
                                * VAR["Ks4"])        
        if VAR["K_MS1"] == 0.013:
            VAR["P_MS1"] = 0.0001
        elif VAR["K_MS1"] < 0.013:
            VAR["P_MS1"] = 0.0001         
        elif VAR["K_MS1"] == 0.014:
            VAR["P_MS1"] = 0.001
        elif VAR["K_MS1"] < 0.014:
            VAR["P_MS1"] = 0.001       
        elif VAR["K_MS1"] == 0.015:
            VAR["P_MS1"] = 0.003
        elif VAR["K_MS1"] < 0.015:
            VAR["P_MS1"] = 0.003          
        elif VAR["K_MS1"] == 0.016:
            VAR["P_MS1"] = 0.005
        elif VAR["K_MS1"] < 0.016:
            VAR["P_MS1"] = 0.005        
        elif VAR["K_MS1"] == 0.021:
            VAR["P_MS1"] = 0.01
        elif VAR["K_MS1"] < 0.021:
            VAR["P_MS1"] = 0.01
        elif VAR["K_MS1"] == 0.035:
            VAR["P_MS1"] = 0.1            
        elif VAR["K_MS1"] < 0.035:
            VAR["P_MS1"] = 0.1              
        elif VAR["K_MS1"] == 0.07:
            VAR["P_MS1"] = 0.5            
        elif VAR["K_MS1"] < 0.07:
            VAR["P_MS1"] = 0.5              
        elif VAR["K_MS1"] == 0.15:
            VAR["P_MS1"] = 0.9            
        elif VAR["K_MS1"] < 0.15:
            VAR["P_MS1"] = 0.9
        else:
            VAR["P_MS1"] = 1
        
        if VAR["P_SPD"] < VAR["P_MS1"]:
            VAR["P_M1"] = VAR["P_SPD"]
        else:
            VAR["P_M1"] = VAR["P_MS1"]
            
        VAR["L_M1"] = VAR["L_o1"]
        VAR["R_M1"] = (VAR["N_M"]
                                * VAR["P_M1"]
                                * VAR["L_M1"])
        
        

# =============================================================================
# 6.6. Risk of dangerous step & touch potential inside & outside structure due 
# to direct strikes to service lines
# =============================================================================
    def calcular_6_6(self, *args):
        
        if VAR["P_LD0"] < VAR["P_EB"]:
            VAR["P_U1p"] = VAR["P_LD0"]
        else:
            VAR["P_U1p"] = VAR["P_EB"]            
        if VAR["P_LD1"] < VAR["P_EB"]:
            VAR["P_U1oh"] = VAR["P_LD1"]
        else:
            VAR["P_U1oh"] = VAR["P_EB"]        
        if VAR["P_LD2"] < VAR["P_EB"]:
            VAR["P_U1ug"] = VAR["P_LD2"]
        else:
            VAR["P_U1ug"] = VAR["P_EB"]      
    

        VAR["X_U1"] = (VAR["n_ohp"] * VAR["N_L1p"] * VAR["P_U1p"]      # 1 * 0.025 * 0.02   peb=0.2
                         + VAR["n_oh"] * VAR["N_L1"] * VAR["P_U1oh"]     # 2 * 0.12 *  0.02   pld1 = 1
                         + VAR["n_ugp"] * VAR["N_L2p"] * VAR["P_U1p"]    # 0 *
                         + VAR["n_ug"] * VAR["N_L2"] * VAR["P_U1ug"])    # 2*
        
        VAR["L_U1"] = VAR["R_a"] * VAR["L_t1"] # ok
        
        VAR["R_U1"] = VAR["X_U1"] * VAR["L_U1"]



# =============================================================================
# 6.7. Risk of physical destruction due to fire,  explosion, mechanical damage 
# and chemical discharge due to direct strikes to service lines
# =============================================================================
    def calcular_6_7(self, *args):
        VAR["P_V1p"] = VAR["P_U1p"]
        VAR["P_V1oh1"] = VAR["P_U1oh"]
        VAR["P_V1ug"] = VAR["P_U1ug"]
        VAR["X_V1"] = VAR["X_U1"]        
        VAR["L_V1"] = VAR["L_B1"]        
        VAR["R_V1"] = VAR["X_V1"] * VAR["L_V1"]


# =============================================================================
# 6.8. Risk of electrical/electronic equipment malfunction or failure due to 
# overvoltages from direct strikes to service lines
# =============================================================================

    def calcular_6_8(self, *args):
        if VAR["P_LD0"] < VAR["P_SPD"]:
            VAR["P_W1p"] = VAR["P_LD0"]
        else:
            VAR["P_W1p"] = VAR["P_SPD"]
           
        if VAR["P_LD1"] < VAR["P_SPD"]:
            VAR["P_W1oh"] = VAR["P_LD1"]
        else:
            VAR["P_W1oh"] = VAR["P_SPD"]        
               
        if VAR["P_LD2"] < VAR["P_SPD"]:
            VAR["P_W1g"] = VAR["P_LD2"]
        else:
            VAR["P_W1ug"] = VAR["P_SPD"]


        VAR["X_W1"] = (VAR["n_ohp"] * VAR["N_L1p"] * VAR["P_W1p"] # 1 * 0.0127674 * 0.4
                        + VAR["n_oh"] * VAR["N_L1"] * VAR["P_W1oh"] # 2 * 0.063837 * 1
                        + VAR["n_ugp"] * VAR["N_L2p"] * VAR["P_W1p"] # 0
                        + VAR["n_ug"] * VAR["N_L2"] * VAR["P_W1ug"]) # 0* * 0.4

        VAR["L_W1"] = VAR["L_o1"]
        VAR["R_W1"] = VAR["X_W1"] * VAR["L_W1"]


# =============================================================================
# 6.9. Risk of electrical/electronic equipment malfunction or failure due to 
# overvoltages from indirect strikes to service lines
# =============================================================================

    def calcular_6_9(self, *args):
        VAR["P_Z1p"] = VAR["P_W1p"]        
        VAR["P_Z1oh"] = VAR["P_W1oh"]
        VAR["P_Z1ug"] = VAR["P_W1ug"]

        if (VAR["N_I1p"] - VAR["N_L1p"]) < 0:
            VAR["DELTA_N_1p"] = 0
        else:
            VAR["DELTA_N_1p"] = VAR["N_I1p"] - VAR["N_L1p"]
        if (VAR["N_I1"] - VAR["N_L1"]) < 0:
            VAR["DELTA_N_1"] = 0
        else:
            VAR["DELTA_N_1"] = VAR["N_I1"] - VAR["N_L1"]        
        if (VAR["N_I2p"] - VAR["N_L2p"]) < 0:
            VAR["DELTA_N_2p"] = 0
        else:
            VAR["DELTA_N_2p"] = VAR["N_I2p"] - VAR["N_L2p"]
        if (VAR["N_I2"]  - VAR["N_L2"]) < 0:
            VAR["DELTA_N_2"] = 0
        else:
            VAR["DELTA_N_2"] = VAR["N_I2"] - VAR["N_L2"]

        VAR["X_Z1"] = (VAR["n_ohp"] * VAR["DELTA_N_1p"] * VAR["P_Z1p"]
                                 + VAR["n_oh"] * VAR["DELTA_N_1"] * VAR["P_Z1oh"]
                                 + VAR["n_ugp"] * VAR["DELTA_N_2p"] * VAR["P_Z1p"]                       
                                 + VAR["n_ug"] * VAR["DELTA_N_2"] * VAR["P_Z1ug"])

        VAR["L_Z1"] = VAR["L_o1"]       
        VAR["R_Z1"] = VAR["X_Z1"]  * VAR["L_Z1"]
# =============================================================================
# 6.10. Total Risk of Electric Shock to animals and people (R1)
# =============================================================================

    def calcular_6_10(self, *args):
        VAR["R_d1"] = VAR["R_A1"] + VAR["R_B1"] + VAR["R_C1"]
        VAR["R_i1"] = VAR["R_M1"] + VAR["R_U1"] + VAR["R_V1"] + VAR["R_W1"] + VAR["R_Z1"]
        VAR["R_1"] = VAR["R_i1"] + VAR["R_d1"]
        VAR["R_S1"] = VAR["R_A1"] + VAR["R_U1"]
        VAR["R_F1"] = VAR["R_B1"] + VAR["R_V1"]
        VAR["R_o1"] = (VAR["R_C1"]
                         + VAR["R_M1"] 
                         + VAR["R_W1"] 
                         + VAR["R_Z1"])
        
# =============================================================================
# 7. RISK CALCULATIONS FOR LOSS CATEGORY 2 - LOSS OF ESSENTIAL SERVICE TO THE 
# PUBLIC
# 7.1. Risk of physical destruction due to fire, Explosion, mechanical damage 
# and chemical discharge due to direct strikes to the structure
# =============================================================================
    def calcular_7_1(self, *args):
        VAR["L_B2"] = VAR["r"] * VAR["r_f"] * VAR["L_f2"]
        VAR["P_B2"] = VAR["P_B1"]
        VAR["R_B2"] = VAR["N_D"] * VAR["P_B2"] * VAR["L_B2"] 

# =============================================================================
# 7.2. Risk of electrical/electronic equipment malfunction or failure due to 
# overvoltages from direct strikes to the structure
# =============================================================================
    def calcular_7_2(self, *args):
        VAR["P_C2"] = VAR["P_C1"]
        VAR["L_C2"] = VAR["L_o2"]
        VAR["R_C2"] = VAR["N_D"] * VAR["P_C2"] * VAR["L_C2"] #   ,1


    def calcular_7_3(self, *args):
        VAR["P_M2"] = VAR["P_M1"]
        VAR["L_M2"] = VAR["L_o2"]
        VAR["R_M2"] = VAR["N_M"] * VAR["P_M2"] * VAR["L_M2"]

    def calcular_7_4(self, *args):
        VAR["X_V2"] = VAR["X_V1"]
        VAR["L_V2"] = VAR["L_B2"]
        VAR["R_V2"] = VAR["X_V1"] * VAR["L_B2"]

    def calcular_7_5(self, *args):
        VAR["X_W2"] = VAR["X_W1"]
        VAR["L_W2"] = VAR["L_o2"]
        VAR["R_W2"] = VAR["X_W2"] * VAR["L_W2"] 

    def calcular_7_6(self, *args):
        VAR["X_Z2"] = VAR["X_Z1"]
        VAR["L_Z2"] = VAR["L_o2"]
        VAR["R_Z2"] = VAR["X_Z2"] * VAR["L_Z2"]

    def calcular_7_7(self, *args):
        VAR["R_d2"] = VAR["R_B2"] + VAR["R_C2"]
        VAR["R_i2"] = (VAR["R_M2"]  #0
                         + VAR["R_V2"] #0
                         + VAR["R_W2"] 
                         + VAR["R_Z2"])
        VAR["R_2"] = VAR["R_i2"] + VAR["R_d2"]
        VAR["R_F2"] = VAR["R_B2"] + VAR["R_V2"]
        VAR["R_o2"] = (VAR["R_C2"] 
                         + VAR["R_M2"] 
                         + VAR["R_W2"] 
                         + VAR["R_Z2"])

# =============================================================================
# 8. RISK CALCULATIONS FOR LOSS CATEGORY 3 - LOSS OF CULTURAL HERITAGE
# =============================================================================
    def calcular_8_1(self, *args):
        VAR["L_B3"] = VAR["r"] * VAR["r_f"] * VAR["L_f3"]
        VAR["P_B3"] = VAR["P_B1"]
        VAR["R_B3"] = VAR["N_D"] * VAR["P_B3"] * VAR["L_B3"]

    def calcular_8_2(self, *args):
        VAR["X_V3"] = VAR["X_V1"]
        VAR["L_V3"] = VAR["L_B3"]
        VAR["R_V3"] = VAR["X_V3"] * VAR["L_V3"]

    def calcular_8_3(self, *args):
        VAR["R_d3"] = VAR["R_B3"]
        VAR["R_i3"] = VAR["R_V3"]
        VAR["R_3"] = VAR["R_i3"] + VAR["R_d3"]
        VAR["R_F3"] = VAR["R_B3"] + VAR["R_V3"]
        VAR["R_o3"] = 0

# =============================================================================
# 9. RISK CALCULATIONS FOR LOSS CATEGORY 4 - ECONOMIC LOSS
# =============================================================================
    def calcular_9_1(self, *args):
        VAR["L_a4"] = VAR["R_a"] * VAR["L_t4"]
        VAR["R_A4"] = VAR["N_D"] * VAR["P_A"] * VAR["L_a4"]


    def calcular_9_2(self, *args):
        VAR["L_B4"] = VAR["r"] * VAR["h4"] * VAR["r_f"] * VAR["L_f4"]
        VAR["P_B4"] = VAR["P_B1"]
        VAR["R_B4"] = VAR["N_D"] * VAR["P_B4"] * VAR["L_B4"]

    def calcular_9_3(self, *args):
        VAR["P_C4"] = VAR["P_C1"]
        VAR["L_C4"] = VAR["L_o4"]
        VAR["R_C4"] = VAR["N_D"] * VAR["P_C4"] * VAR["L_C4"]

    def calcular_9_4(self, *args):
        VAR["P_M4"] = VAR["P_M1"]
        VAR["L_M4"] = VAR["L_o4"]
        VAR["R_M4"] = VAR["N_M"] * VAR["P_M4"] * VAR["L_M4"]

    def calcular_9_5(self, *args):
        VAR["X_U4"] = VAR["X_U1"]
        VAR["L_U4"] = VAR["R_a"] * VAR["L_t4"]
        VAR["R_U4"] = VAR["X_U4"] * VAR["L_U4"]

    def calcular_9_6(self, *args):        
        VAR["X_V4"] = VAR["X_V1"]
        VAR["L_V4"] = VAR["L_B4"]
        VAR["R_V4"] = VAR["X_V4"] * VAR["L_V4"]

    def calcular_9_7(self, *args):
        VAR["X_W4"] = VAR["X_W1"]
        VAR["L_W4"] = VAR["L_o4"]
        VAR["R_W4"] = VAR["X_W4"] * VAR["L_W4"] 

    def calcular_9_8(self, *args):
        VAR["X_Z4"] = VAR["X_Z1"]
        VAR["L_Z4"] = VAR["L_o4"]
        VAR["R_Z4"] = VAR["X_Z4"] * VAR["L_Z4"]

    def calcular_9_9(self, *args):
        VAR["R_d4"] = VAR["R_A4"] + VAR["R_B4"] + VAR["R_C4"]
        VAR["R_i4"] = (VAR["R_M4"] 
                         + VAR["R_U4"] 
                         + VAR["R_V4"] 
                         + VAR["R_W4"] 
                         + VAR["R_Z4"])
        VAR["R_4"] = VAR["R_i4"] + VAR["R_d4"]
        VAR["R_S4"] = VAR["R_A4"] + VAR["R_U4"]
        VAR["R_F4"] = VAR["R_B4"] + VAR["R_V4"]
        VAR["R_o4"] = (VAR["R_C4"] 
                         + VAR["R_M4"] 
                         +VAR["R_W4"] 
                         + VAR["R_Z4"])

        _text_ = "{:.2e}".format(VAR["R_d1"])
        self.Entry16['state'] = 'normal'
        self.Entry16.delete('0', 'end')
        self.Entry16.insert('0', _text_)
        self.Entry16['state'] = 'readonly'
        self.Entry16.grid(column='3', row='1')

        _text_ = "{:.2e}".format(VAR["R_d2"])
        self.Entry17['state'] = 'normal'
        self.Entry17.delete('0', 'end')
        self.Entry17.insert('0', _text_)
        self.Entry17['state'] = 'readonly'
        self.Entry17.grid(column='3', row='2')

        _text_ = "{:.2e}".format(VAR["R_d3"])
        self.Entry18['state'] = 'normal'
        self.Entry18.delete('0', 'end')
        self.Entry18.insert('0', _text_)
        self.Entry18['state'] = 'readonly'
        self.Entry18.grid(column='3', row='3')

        _text_ = "{:.2e}".format(VAR["R_d4"])
        self.Entry19['state'] = 'normal'
        self.Entry19.delete('0', 'end')
        self.Entry19.insert('0', _text_)
        self.Entry19['state'] = 'readonly'
        self.Entry19.grid(column='3', row='4')

        _text_ = "{:.2e}".format(VAR["R_i1"])
        self.Entry20['state'] = 'normal'
        self.Entry20.delete('0', 'end')
        self.Entry20.insert('0', _text_)
        self.Entry20['state'] = 'readonly'
        self.Entry20.grid(column='5', row='1')

        _text_ = "{:.2e}".format(VAR["R_i2"])
        self.Entry21['state'] = 'normal'
        self.Entry21.delete('0', 'end')
        self.Entry21.insert('0', _text_)
        self.Entry21['state'] = 'readonly'
        self.Entry21.grid(column='5', row='2')

        _text_ = "{:.2e}".format(VAR["R_i3"])
        self.Entry22['state'] = 'normal'
        self.Entry22.delete('0', 'end')
        self.Entry22.insert('0', _text_)
        self.Entry22['state'] = 'readonly'
        self.Entry22.grid(column='5', row='3')

        _text_ = "{:.2e}".format(VAR["R_i4"])
        self.Entry23['state'] = 'normal'
        self.Entry23.delete('0', 'end')
        self.Entry23.insert('0', _text_)
        self.Entry23['state'] = 'readonly'
        self.Entry23.grid(column='5', row='4')

        _text_ = "{:.2e}".format(VAR["R_1"])
        self.Entry24['state'] = 'normal'
        self.Entry24.delete('0', 'end')
        self.Entry24.insert('0', _text_)
        self.Entry24['state'] = 'readonly'
        self.Entry24.grid(column='7', row='1')

        _text_ = "{:.2e}".format(VAR["R_2"])
        self.Entry25['state'] = 'normal'
        self.Entry25.delete('0', 'end')
        self.Entry25.insert('0', _text_)
        self.Entry25['state'] = 'readonly'
        self.Entry25.grid(column='7', row='2')

        _text_ = "{:.2e}".format(VAR["R_3"])
        self.Entry26['state'] = 'normal'
        self.Entry26.delete('0', 'end')
        self.Entry26.insert('0', _text_)
        self.Entry26['state'] = 'readonly'
        self.Entry26.grid(column='7', row='3')

        _text_ = "{:.2e}".format(VAR["R_4"])
        self.Entry27['state'] = 'normal'
        self.Entry27.delete('0', 'end')
        self.Entry27.insert('0', _text_)
        self.Entry27['state'] = 'readonly'
        self.Entry27.grid(column='7', row='4')

    def calcular_informe(self):
        a = VAR
        PDF_Creator.crear(a)

    def valores(self, *args):
        print("LA DDT ES:")
        print(VAR["DDT"])
    
    def changeText(self):
        a = VAR["DDT"]
        self.text_ddt.set(a)
        VAR["DDT"] = a
        #print(str(a))
