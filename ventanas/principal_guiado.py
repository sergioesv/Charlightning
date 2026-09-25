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
from tkinter import ttk
from tkinter import messagebox

from ventanas.panel import Panel
from calculo_ddt_plot.ventana_calculo_ddt import Calculo_DDT
from variables.globales import papo
from variables.variable_generales import VAR
from calculate_risk.collect_entry_data_risk import DataEntryRiskTable
from calculate_risk.norma import memoria
from calculate_risk.norma.adaptador import resultados_pantalla
from calculate_risk.opciones import VALORES_OPCIONES

from pathlib import Path

#Carpeta principal del proyecto: dos niveles arriba de este archivo
CARPETA_PROYECTO = Path(__file__).resolve().parent.parent


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

        # Se quitó el campo "Resistividad del terreno": en la norma vigente
        # (IEC 62305-2:2010 / NTC 4552-2:2023) la distancia de influencia
        # para impactos cercanos a la estructura es fija (500 m) y ya no
        # depende de la resistividad del terreno (ver calcular_A_m).
      


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

        self.Labelframe14 = ttk.Labelframe(self.Frame2)
        self.Label_P_TU = ttk.Label(self.Labelframe14)
        self.Label_P_TU.configure(text='Medidas contra tensión de contacto:')
        self.Label_P_TU.grid(column='0', padx='3', pady='2', row='0', sticky='w')
        self.Label_C_LD = ttk.Label(self.Labelframe14)
        self.Label_C_LD.configure(text='Apantallamiento de línea (corriente directa):')
        self.Label_C_LD.grid(column='0', padx='3', pady='2', row='1', sticky='w')
        self.Label_C_LI = ttk.Label(self.Labelframe14)
        self.Label_C_LI.configure(text='Apantallamiento de línea (impacto cercano):')
        self.Label_C_LI.grid(column='0', padx='3', pady='2', row='2', sticky='w')
        self.Label_P_LI = ttk.Label(self.Labelframe14)
        self.Label_P_LI.configure(text='Tensión soportada de los equipos:')
        self.Label_P_LI.grid(column='0', padx='3', pady='2', row='3', sticky='w')
        self.Combobox25 = ttk.Combobox(self.Labelframe14)
        self.Combobox25.configure(
            state='readonly',
            values=["Sin medidas",
                    "Avisos de peligro",
                    "Aislamiento eléctrico",
                    "Restricciones físicas de acceso"],
            width=ancho_combobox_labelframe2)
        self.Combobox25.grid(column='1', padx='3', row='0', sticky='e')
        self.Combobox25.current(0)
        self.Labelframe14.columnconfigure('1', weight='1')
        self.Combobox26 = ttk.Combobox(self.Labelframe14)
        self.Combobox26.configure(
            state='readonly',
            values=["Normal",
                    "Apantallada y puesta a tierra en la entrada"],
            width=ancho_combobox_labelframe2)
        self.Combobox26.grid(column='1', padx='3', row='1', sticky='e')
        self.Combobox26.current(0)
        self.Combobox27 = ttk.Combobox(self.Labelframe14)
        self.Combobox27.configure(
            state='readonly',
            values=["Normal",
                    "Apantallada y puesta a tierra en la entrada"],
            width=ancho_combobox_labelframe2)
        self.Combobox27.grid(column='1', padx='3', row='2', sticky='e')
        self.Combobox27.current(0)
        self.Combobox28 = ttk.Combobox(self.Labelframe14)
        self.Combobox28.configure(
            state='readonly',
            values=["Equipos sensibles (U_W bajo)",
                    "Tensión soportada típica (U_W = 2,5 kV)"],
            width=ancho_combobox_labelframe2)
        self.Combobox28.grid(column='1', padx='3', row='3', sticky='e')
        self.Combobox28.current(0)
        self.Labelframe14.configure(height='200', text='Medidas adicionales en las líneas (Anexo B)', width='200')
        self.Labelframe14.grid(column='0', padx='10', pady='12', row='4', sticky='ew')

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
                    "Problemas de evacuación",
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
        self.img_1 = tk.PhotoImage(file=str(CARPETA_PROYECTO / "archivos" / "plot.png"))
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

        self.anterior_modo()


    def calcular_funciones(self):
        self.calcular_DDT()
        self.calcular_L_W_H_H_H_p()
        self.calcular_n_oh()
        self.calcular_n_ug()
        self.leer_combos()
        VAR.update(resultados_pantalla(VAR))
        self.mostrar_resultados()



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
        VAR["C_d"] = collect_data_entry.get_height_factor_surrounding(
                                        self.Combobox_height_factor_surrounding.current()
                                        )
        VAR["C_e"] = collect_data_entry.get_factor_line_density_C_e(
                                        self.Combobox_factor_line_density_C_e.current()
                                        )
        # Se calcual DDT en calcular_DDT



    def calcular_DDT(self, *args):
        try:
            VAR["DDT"] = float(self.Entry_ddt_calculado.get())
        except:
            messagebox.showinfo(message="Debe ingresar la Densidad de descarga a tierra ",
                                 title="Algo raro por aquí")       



# =============================================================================
# LECTURA DE LOS COMBOS Y SPINBOX
# =============================================================================

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

    def leer_combos(self):
        """Guarda en VAR el valor de la opción elegida en cada combo."""
        combos = {
            "Ks3": self.Combobox3,
            "pl": self.Combobox6,
            "P_LD0": self.Combobox22,
            "C_t0": self.Combobox23,
            "P_LD1": self.Combobox7,
            "P_LD2": self.Combobox8,
            "h_1": self.Combobox12,
            "L_f1": self.Combobox13,
            "L_o1": self.Combobox14,
            "L_f2": self.Combobox15,
            "L_o2": self.Combobox16,
            "L_f3": self.Combobox21,
            "h4": self.Combobox17,
            "L_f4": self.Combobox18,
            "L_o4": self.Combobox19,
            "L_t4": self.Combobox20,
            "R_T4": self.Combobox24,
            "E": self.Combobox9,
            "r": self.Combobox10,
            "SP": self.Combobox11,
            "P_TU": self.Combobox25,
            "C_LD": self.Combobox26,
            "C_LI": self.Combobox27,
            "P_LI": self.Combobox28,
        }
        for clave, combo in combos.items():
            VAR[clave] = VALORES_OPCIONES[clave][combo.current()]




    def mostrar_resultados(self):
        """Escribe los resultados calculados en las casillas de la pantalla."""
        
        self.Entry5.delete('0', 'end')
        self.Entry5.insert('0', round(VAR["A_d"], 3))
        
        casillas = [
            (self.Entry16, "R_d1"),
            (self.Entry17, "R_d2"),
            (self.Entry18, "R_d3"),
            (self.Entry19, "R_d4"),
            (self.Entry20, "R_i1"),
            (self.Entry21, "R_i2"),
            (self.Entry22, "R_i3"),
            (self.Entry23, "R_i4"),
            (self.Entry24, "R_1"),
            (self.Entry25, "R_2"),
            (self.Entry26, "R_3"),
            (self.Entry27, "R_4"),
        ]
        for casilla, clave in casillas:
            casilla['state'] = 'normal'
            casilla.delete('0', 'end')
            casilla.insert('0', "{:.2e}".format(VAR[clave]))
            casilla['state'] = 'readonly'

    def calcular_informe(self):
        """Genera la memoria de cálculo en LaTeX (y el PDF si hay pdflatex)."""
        proyecto = {
            "Proyecto": papo["proyecto"],
            "Diseñador": papo["disenador"],
            "Dirección": papo["direccion"],
            "Teléfono": papo["telefono"],
            "Descripción": papo["descripcion"],
        }
        # VAR trae los datos de entrada Y los resultados: calcular_funciones()
        # ya hizo VAR.update(resultados_pantalla(VAR)).
        ruta_tex, ruta_pdf = memoria.informe_completo(
            CARPETA_PROYECTO, VAR, proyecto=proyecto)

        if ruta_pdf:
            mensaje = f"Memoria de cálculo generada:\n{ruta_pdf}"
        else:
            mensaje = ("Se generó la memoria en LaTeX:\n"
                       f"{ruta_tex}\n\n"
                       "Para obtener el PDF hace falta tener LaTeX instalado.")
        messagebox.showinfo(message=mensaje, title="Memoria de cálculo")

