#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb 13 18:59:17 2022

@author: Sergio Andrés Estrada Vélez
"""
import sys
import tkinter as tk
from tkinter import ttk

import PDF_Creator
#from tkinter import messagebox

import math

from calculo_ddt_plot import ventana_auxiliar



#Declaro estas variables globales
proyecto = ''
disenador = ''
direccion = ''
telefono = ''
DDT = 100



class Panel(tk.Frame):
    """Clase genérica para mostrar un Frame con un cierto título y
    tamaño dados, centrado en la pantalla"""

    def __init__(self, master, titulo="Sin título", ancho=360, alto=180):
        super().__init__()
        self.master: tk.Tk = master
        self.siguiente = (
            lambda: None
        )  # Valor por defecto no útil. El programa principal debe asignar otro
        self.titulo = titulo
        self.ancho = ancho
        self.alto = alto
        self.x = (self.master.winfo_screenwidth() - self.ancho) // 2
        self.y = (self.master.winfo_screenheight() - self.alto) // 2


    def mostrar(self):
        self.master.title(self.titulo)
        self.master.geometry(
            "{}x{}+{}+{}".format(self.ancho, self.alto, self.x, self.y)
        )
        self.lift()



class Modo(Panel):
    """Panel para elegir si quiere una vista compacta del programa o una vista
    paso a paso con ayuda lateral"""


    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.extraer_entry36=tk.StringVar()
        self.extraer_entry37=tk.StringVar()   
        self.extraer_entry38=tk.StringVar()
        self.extraer_entry39=tk.StringVar()
        self.extraer_entry36.set('')
        self.extraer_entry37.set('')
        self.extraer_entry38.set('')
        self.extraer_entry39.set('')



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
        self.Button5 = ttk.Button(self.Frame17)
        self.Button5.configure(text='Compacto', command=self.compacto)
        self.Button5.pack(pady='5', side='top')
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


    def compacto(self):
        self.siguiente()


    def guiado(self):
        global proyecto
        global disenador  
        global direccion
        global telefono

        proyecto = self.extraer_entry36.get()
        disenador = self.extraer_entry37.get()
        direccion = self.extraer_entry38.get()
        telefono = self.extraer_entry39.get()

        self.siguienteguiado()





class Principal_compacto(Panel):
    """Panel que muestra una "terminal" negra y el botón para generar la tabla.
    Al pulsar ese botón llama a self.siguiente() para mostrar el panel que
    pide un número al usuario"""

    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.vcmd = (self.register(self.check), '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')

        self.Frame8 = ttk.Frame(self)
        self.Frame11 = ttk.Frame(self.Frame8)
        self.Frame11.configure(height='200', relief='sunken', width='200')
        self.Frame11.grid(column='0', row='0')
        self.Frame12 = ttk.Frame(self.Frame8)
        self.Frame12.configure(height='200', relief='sunken', width='200')
        self.Frame12.grid(column='1', row='0')
        self.Frame13 = ttk.Frame(self.Frame8)
        self.Frame13.configure(height='200', relief='sunken', width='200')
        self.Frame13.grid(column='3', row='0', sticky='w')
        self.Frame14 = ttk.Frame(self.Frame8)
        self.Button1 = ttk.Button(self.Frame14)
        self.Button1.configure(text='Informe')
        self.Button1.place(anchor='nw', relx='0.86', rely='0.70', x='0', y='0')
        self.Button2 = ttk.Button(self.Frame14)
        self.Button2.configure(text='Regresar', command=self.regresar_modo)
        self.Button2.place(anchor='nw', relx='0.86', rely='0.48', x='0', y='0')
        self.Button8 = ttk.Button(self.Frame14)
        self.Button8.configure(text='Calcular', 
                               command=self.boton_calcular_funciones)
        self.Button8.place(anchor='nw', relx='0.86', rely='0.25', x='0', y='0')
        self.Frame14.configure(height='200', relief='flat', width='200')
        self.Frame14.grid(column='0', columnspan='3', row='1', sticky='ew')
        self.Frame15 = ttk.Frame(self.Frame8)
        self.Frame15.configure(height='200', width='200')
        self.Frame15.grid(column='3', row='1', sticky='nsew')
        self.Frame8.configure(height='200', width='200')
        self.Frame8.pack(side='top')

        Estructura.frame1(self, 2)
#        Estructura.frame2(self)
        Estructura.frame3(self,2)


    def boton_calcular_funciones(self):
        Estructura.calcular_funciones(self)


    def regresar_modo(self):
        self.anterior_modo()


    def guiado(self):
        self.siguienteguiado()


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


    def mostrarseleccionado(self):

        print('hola1')
        # ventana_auxiliar.Calculo_DDT(master=self.master)
        # self.Label11.configure(text=DDT)

        




        

class Principal_guiado(Panel):
    """Panel que muestra una "terminal" negra y el botón para generar la tabla.
    Al pulsar ese botón llama a self.siguiente() para mostrar el panel que
    pide un número al usuario"""

    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        self.vcmd = (self.register(self.check), 
                     '%d', 
                     '%i', 
                     '%P', 
                     '%s', 
                     '%S', 
                     '%v', 
                     '%V', 
                     '%W')

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

        Estructura.frame1(self,1)
        Estructura.frame2(self)
        Estructura.frame3(self,1)


        self.Notebook1.add(self.Frame1, text='Tab1')
        self.Notebook1.add(self.Frame2, text='Tab2')
        self.Notebook1.add(self.Frame3, text='Tab3')
        self.Notebook1.configure(height='450', width='530')
        self.Notebook1.pack(anchor='ne', padx='10', pady='10', side='left')

        self.Notebook2.add(self.Frame9, text='Tab4')
        self.Notebook2.add(self.Frame10, text='Tab5')
        self.Notebook2.configure(height='450', width='500')
        self.Notebook2.pack(padx='10', pady='10', side='top')


    def regresar_modo(self):
        self.anterior_modo()


    def calcular_funciones(self):
        Estructura.variables(self)
        Estructura.calcular_L_W_H_H_H_p(self)
        Estructura.calcular_r_f(self)
        Estructura.calcular_Ks1(self)
        Estructura.calcular_C_d(self)
        Estructura.calcular_C_e(self) #and var_L_1
        Estructura.calcular_DDT(self)
        Estructura.calcular_K_s3(self)
        Estructura.calcular_pl(self)
        Estructura.calcular_P_LD0(self)
        Estructura.calcular_C_t0(self)
        Estructura.calcular_n_oh(self)
        Estructura.calcular_n_ug(self)
        Estructura.calcular_P_LD1(self)
        Estructura.calcular_P_LD2(self)
        Estructura.calcular_h_1(self)
        Estructura.calcular_L_f1(self)
        Estructura.calcular_L_o1(self)
        Estructura.calcular_L_f2(self)
        Estructura.calcular_L_o2(self)
        Estructura.calcular_L_f3(self)
        Estructura.calcular_h4(self)
        Estructura.calcular_L_f4(self)
        Estructura.calcular_L_o4(self)
        Estructura.calcular_L_t4(self)
        Estructura.calcular_R_T4(self)
        Estructura.calcular_E(self)
        Estructura.calcular_r(self)
        Estructura.calcular_SP(self)



        Estructura.calcular_3_1(self)
        Estructura.calcular_3_2(self)
        Estructura.calcular_4(self)       
        Estructura.calcular_4_1(self)
        Estructura.calcular_4_2(self)
        Estructura.calcular_5(self) 
        Estructura.calcular_5_1(self)
        Estructura.calcular_5_2(self)
        Estructura.calcular_6_1(self)
        Estructura.calcular_6_2(self)
        Estructura.calcular_6_3(self)
        Estructura.calcular_6_4(self)
        Estructura.calcular_6_5(self)
        Estructura.calcular_6_6(self)
        Estructura.calcular_6_7(self)      
        Estructura.calcular_6_8(self)
        Estructura.calcular_6_9(self)
        Estructura.calcular_6_10(self)
        Estructura.calcular_7_1(self)
        Estructura.calcular_7_2(self)
        Estructura.calcular_7_3(self)
        Estructura.calcular_7_4(self)
        Estructura.calcular_7_5(self)
        Estructura.calcular_7_6(self)
        Estructura.calcular_7_7(self)
        Estructura.calcular_8_1(self)
        Estructura.calcular_8_2(self)
        Estructura.calcular_8_3(self)
        Estructura.calcular_9_1(self)
        Estructura.calcular_9_2(self)
        Estructura.calcular_9_3(self)
        Estructura.calcular_9_4(self)
        Estructura.calcular_9_5(self)
        Estructura.calcular_9_6(self)
        Estructura.calcular_9_7(self)
        Estructura.calcular_9_8(self)
        Estructura.calcular_9_9(self)
        Estructura.changeText(self)       
        
        




        Estructura.valores(self)

    def informe(self):
        Estructura.calcular_informe(self)


        

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

    def mostrarseleccionado(self):
        print('hola2')

        ventana_auxiliar.Calculo_DDT(master=self.master)


class Estructura(ttk.Frame):
    """Panel que muestra una "terminal" negra y el botón para generar la tabla.
    Al pulsar ese botón llama a self.siguiente() para mostrar el panel que
    pide un número al usuario"""

    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)



    def variables(self):
        
# =============================================================================
# VARIABLE USER ENTERED STRUCTURAL DIMENSIONS
# =============================================================================
        self.var_L = 1
        self.var_W = 2
        self.var_H = 3
        self.var_H_P = 4

# =============================================================================
# VARIABLE USER ENTERED STRUCTURAL ATTRIBUTES
# =============================================================================
        self.var_r_f = 0
        
        self.var_Ks1 = 1

# =============================================================================
# VARIABLE USER ENTERED ENVIRONMENTAL INFLUENCES
# =============================================================================
        self.var_C_d = 2
        self.var_C_e = 1
        self.var_DDT = 0
        self.var_N_g = 0
# =============================================================================
# VARIABLE USER ENTERED BUILDING WIRING
# =============================================================================
        self.var_Ks3 = 1

# =============================================================================
# VARIABLE USER ENTERED CONDUCTIVE SERVICE LINES
# =============================================================================

        '''Power Lines'''
        self.var_pl = 1
        self.var_P_LD0 = 1
        self.var_C_t0 = 1

        '''Other Overhead Service Lines:'''
        self.var_n_oh = 0
        self.var_P_LD1 = 1

        '''Conductive Underground Services - Electrical Services e.g.
        Communication Lines:'''
        self.var_n_ug = 0
        self.var_P_LD2 = 1

# =============================================================================
# VARIABLE USER ENTERED ACCEPTABLE RISK & LOSS CATEGORIES
# =============================================================================
        '''Loss Category 1 - Loss of Human Life'''
        self.var_h_1 = 1
        self.var_L_f1 = 0
        self.var_L_o1 = 0

        '''Loss Category 2 - Loss of Essential Service to the Public:'''
        self.var_L_f2 = 0
        self.var_L_o2 = 0

        '''Loss Category 3 - Loss of Cultural Heritage'''
        self.var_L_f3 = 0

        '''Loss Category 4 - Economic Loss'''
        self.var_h4 = 1
        self.var_L_f4 = 1
        self.var_L_o4 = 1
        self.var_L_t4 = 0
        self.var_R_T4 = 1 * 10**(-3)

# =============================================================================
# VARIABLE USER ENTERED PROTECTION MEASURES IMPLEMENTED
# =============================================================================
        self.var_E = 1
        self.var_r = 1
        self.var_SP = 0








        self.var_A_d = 0
        self.var_N_D = 0
        self.var_A_m = 0
        self.var_N_M = 0
        self.var_L_1 = 1000
        self.var_L_2 = 1000
        





        
        
# =============================================================================
# VARIABLE DEFAULT STRUCTURAL ATTRIBUTES
# =============================================================================
        self.var_Ks2 = 1
        self.var_P_A = 1
        self.var_D_m = 250



# =============================================================================
# VARIABLE DEFAULT EQUIPMENT
# =============================================================================
        self.var_Ks4 = 1

# =============================================================================
# VARIABLE DEFAULT CONDUCTIVE SERVICE LINES
# =============================================================================
        '''Other Overhead Service Lines'''
        self.var_H_c1 = 6
        self.var_D_L1 = 500
        self.var_C_t1 = 1
        self.var_l_a1 = 0
        self.var_w_a1 = 0
        self.var_h_a1 = 0

        '''Conductive Underground Services - Electrical Services e.g.
        Communication Lines:'''
        self.var_P_2 = 500
        self.var_C_t2 = 1
        self.var_l_a2 = 0
        self.var_w_a2 = 0
        self.var_h_a2 = 0


# =============================================================================
# VARIABLE DEFAULT RISK & LOSS CATEGORIES
# =============================================================================
        self.var_R_T1 = 10**(-5)
        self.var_L_t1 = 10**(-4)
        self.var_R_a = 10**(-2)
        self.var_R_T2 = 10**(-3)
        self.var_R_T3 = 10**(-3)
        self.var_n_ohp = 0
        self.var_D_c1 = 0
        self.var_L_c1 = 0
        self.var_A_c1 = 0
        self.var_a1 = 0
        
        self.var_N_L1p = 0
        self.var_N_L1 = 0
        self.var_A_l1 = 0
        self.var_N_I1p = 0
        self.var_N_I1 = 0
        self.var_n_ugp = 0
        self.var_L_c2 = 0
        self.var_A_c2 = 0
        self.var_A_a2 = 0 
        self.var_N_L2p = 0
        self.var_N_L2 = 0
        self.var_A_l2 = 0
        self.var_N_I2p = 0
        self.var_N_I2 = 0
        self.var_L_a1 = 0
        self.var_R_A1 = 0
        self.var_L_B1 = 0
        self.var_P_B1 = 0
        self.var_R_B1 = 0
        self.var_P_SPD = 0
        self.var_P_EB = 0
        self.var_P_C1 = 0
        self.var_L_C1 = 0
        self.var_R_C1 = 0     
        self.var_K_MS1 = 0
        self.var_P_MS1 = 0
        self.var_P_M1 = 0
        self.var_L_M1 = 0
        self.var_R_M1 = 0
        self.var_P_U1p = 0
        self.var_P_U1oh = 0
        self.var_P_U1ug = 0
        self.var_X_U1 = 0
        self.var_L_U1 = 0
        self.var_R_U1 = 0
        self.var_P_V1p = 0
        self.var_P_V1oh1 = 0
        self.var_P_V1ug = 0
        self.var_X_V1 = 0
        self.var_L_V1 = 0
        self.var_R_V1 = 0
        self.var_P_W1p = 0
        self.var_P_W1oh = 0
        self.var_P_W1ug = 0
        self.var_X_W1 = 0
        self.var_L_W1 = 0
        self.var_R_W1 = 0
        self.var_P_Z1p = 0
        self.var_P_Z1oh = 0
        self.var_P_Z1ug = 0
        self.var_DELTA_N_1p = 0
        self.var_DELTA_N_1 = 0
        self.var_DELTA_N_2p = 0
        self.var_DELTA_N_2 = 0
        self.var_X_Z1 = 0
        self.var_L_Z1 = 0
        self.var_R_Z1 = 0
        self.var_R_d1 = 0
        self.var_R_i1 = 0
        self.var_R_1 = 0
        self.var_R_S1 = 0
        self.var_R_F1 = 0
        self.var_R_o1 = 0

        self.var_P_B2 = 0
        self.var_R_B2 = 0
        self.var_P_C2 = 0
        self.var_L_C2 = 0
        self.var_R_C2 = 0
        self.var_P_M2 = 0
        self.var_L_M2 = 0
        self.var_R_M2 = 0
        self.var_X_V2 = 0
        self.var_L_V2 = 0
        self.var_R_V2 = 0
        self.var_X_W2 = 0
        self.var_L_W2 = 0
        self.var_R_W2 = 0
        self.var_X_Z2 = 0
        self.var_L_Z2 = 0
        self.var_R_Z2 = 0
        self.var_R_d2 = 0
        self.var_R_i2 =0
        self.var_R_2 = 0
        self.var_R_F2 = 0
        self.var_R_o2 = 0
        self.var_L_B3 = 0
        self.var_P_B3 = 0
        self.var_R_B3 = 0
        self.var_X_V3 = 0
        self.var_L_V3 = 0
        self.var_R_V3 = 0
        self.var_R_d3 = 0
        self.var_R_i3 = 0
        self.var_R_3 = 0
        self.var_R_F3 = 0
        self.var_R_o3 = 0
        self.var_L_a4 = 0
        self.var_R_A4 = 0
        self.var_L_B4 = 0
        self.var_P_B4 = 0
        self.var_R_B4 = 0
        self.var_P_C4 = 0
        self.var_L_C4 = 0
        self.var_R_C4 = 0
        self.var_P_M4 = 0
        self.var_L_M4 = 0
        self.var_R_M4 = 0
        self.var_X_U4 = 0
        self.var_L_U4 = 0
        self.var_R_U4 = 0
        self.var_X_V4 = 0
        self.var_L_V4 = 0
        self.var_R_V4 = 0
        self.var_X_W4 = 0
        self.var_L_W4 = 0
        self.var_R_W4 = 0
        self.var_X_Z4 = 0
        self.var_L_Z4 = 0
        self.var_R_Z4 = 0
        self.var_R_d4 = 0
        self.var_R_i4 = 0
        self.var_R_4 = 0
        self.var_R_S4 = 0
        self.var_R_F4 = 0
        self.var_R_o4 = 0



    def frame1(self, num, *args):
        global DDT

        self.extraer_combobox1=tk.StringVar()
        self.extraer_combobox2=tk.StringVar()       
        self.extraer_combobox3=tk.StringVar()
        self.extraer_combobox4=tk.StringVar()  
        self.extraer_combobox5=tk.StringVar()
        self.extraer_combobox6=tk.StringVar()      
        self.extraer_combobox7=tk.StringVar()
        self.extraer_combobox8=tk.StringVar()  
        self.extraer_combobox9=tk.StringVar()
        self.extraer_combobox10=tk.StringVar()     
        self.extraer_combobox11=tk.StringVar()
        self.extraer_combobox12=tk.StringVar()  
        self.extraer_combobox13=tk.StringVar()
        self.extraer_combobox14=tk.StringVar()      
        self.extraer_combobox15=tk.StringVar()
        self.extraer_combobox16=tk.StringVar()  
        self.extraer_combobox17=tk.StringVar()
        self.extraer_combobox18=tk.StringVar() 
        self.extraer_combobox19=tk.StringVar()
        self.extraer_combobox20=tk.StringVar()  
        self.extraer_combobox21=tk.StringVar()
        self.extraer_combobox22=tk.StringVar()      
        self.extraer_combobox23=tk.StringVar()
        self.extraer_combobox24=tk.StringVar()  
        self.text_ddt = tk.StringVar()

        if num == 1:
            self.Frame1 = ttk.Frame(self.Notebook1)
            self.Frame2 = ttk.Frame(self.Notebook1)
            self.Frame3 = ttk.Frame(self.Notebook1)
            ancho_combobox_labelframe1 = "32"
            ancho_combobox_labelframe2 = "31"
            ancho_combobox_labelframe3 = "29"
        else:
            self.Frame1 = ttk.Frame(self.Frame11)
            self.Frame2 = ttk.Frame(self.Frame12)
            self.Frame3 = ttk.Frame(self.Frame13)
            ancho_combobox_labelframe1 = "20"
            ancho_combobox_labelframe2 = "20"
            ancho_combobox_labelframe3 = "20"

        self.Labelframe1 = ttk.Labelframe(self.Frame1)
        self.Label1 = ttk.Label(self.Labelframe1)
        self.Label1.configure(text='Longitud de la estructura [m]:')
        self.Label1.grid(column='0', padx='3', pady='2', row='0', sticky='w')
        self.Labelframe1.rowconfigure('0', pad='0', weight='0')
        self.Label2 = ttk.Label(self.Labelframe1)
        self.Label2.configure(text='Ancho de la estructura [m]:')
        self.Label2.grid(column='0', padx='3', pady='2', row='1', sticky='w')
        self.Labelframe1.rowconfigure('1', pad='2')
        self.Label3 = ttk.Label(self.Labelframe1)
        self.Label3.configure(text='Altura de la estructura[m]:')
        self.Label3.grid(column='0', padx='3', pady='2', row='2', sticky='w')
        self.Labelframe1.rowconfigure('2', pad='2')
        self.Label4 = ttk.Label(self.Labelframe1)
        self.Label4.configure(text='Altura máxima de la estructura[m]:')
        self.Label4.grid(column='0', padx='3', pady='2', row='3', sticky='w')
        self.Labelframe1.rowconfigure('3', pad='2')
        self.Label5 = ttk.Label(self.Labelframe1)
        self.Label5.configure(text='Medida total de la estructura [m2]:')
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
        self.Labelframe1.grid(column='0', padx='10', pady='15', row='0', sticky='ew')
        self.Frame1.columnconfigure('0', weight='0')
        self.Labelframe2 = ttk.Labelframe(self.Frame1)
        self.Label6 = ttk.Label(self.Labelframe2)
        self.Label6.configure(text='Riesgo de fuego en la estructura:')
        self.Label6.grid(column='0', padx='3', pady='2', row='0', sticky='w')
        self.Label7 = ttk.Label(self.Labelframe2)
        self.Label7.configure(text='Eficacia del apantallamiento:')
        self.Label7.grid(column='0', padx='3', pady='2', row='1', sticky='w')
        self.Label8 = ttk.Label(self.Labelframe2)
        self.Label8.configure(text='Tipo de cableado interno:')
        self.Label8.grid(column='0', padx='3', pady='2', row='2', sticky='w')
        self.Combobox1 = ttk.Combobox(self.Labelframe2)
        self.Combobox1.configure(state='readonly', 
                                 values=['Explosivo', 
                                         'Alto', 
                                         'Normal', 
                                         'Bajo', 
                                         'Ninguno'],
                                 textvariable=self.extraer_combobox1,
                                 width=ancho_combobox_labelframe1)
        self.Combobox1.grid(column='1', padx='3', pady='2', row='0', sticky='e')
        self.Combobox1.current(2)
        self.Labelframe2.columnconfigure('1', weight='1')
        self.Combobox2 = ttk.Combobox(self.Labelframe2)
        self.Combobox2.configure(state='readonly',
                                 values=['Escasa', 'Media', 'Buena'],
                                 textvariable=self.extraer_combobox2,
                                 width=ancho_combobox_labelframe1)
        self.Combobox2.grid(column='1', padx='3', pady='2', row='1', sticky='e')
        self.Combobox2.current(1)
        self.Combobox3 = ttk.Combobox(self.Labelframe2)
        self.Combobox3.configure(state='readonly',
                                 values=['Apantallado', 'No apantallado'],
                                 textvariable=self.extraer_combobox3,
                                 width=ancho_combobox_labelframe1)
        self.Combobox3.grid(column='1', padx='3', pady='2', row='2', sticky='e')
        self.Combobox3.current(0)
        self.Labelframe2.configure(height='450', text='Riesgo de incendio y daños físicos', width='200')
        self.Labelframe2.grid(column='0', padx='10', pady='5', row='1', sticky='ew')
        self.Labelframe3 = ttk.Labelframe(self.Frame1)
        self.Label9 = ttk.Label(self.Labelframe3)
        self.Label9.configure(text='Localización relativa:')
        self.Label9.grid(column='0', padx='3', pady='2', row='0', sticky='w')
        self.Label10 = ttk.Label(self.Labelframe3)
        self.Label10.configure(text='Factor ambiental:')
        self.Label10.grid(column='0', padx='3', pady='2', row='1', sticky='w')
        self.Labelframe3.rowconfigure('1', weight='0')
        self.Label11 = ttk.Label(self.Labelframe3)
        self.Label11.configure(text='Densidad de descarga a tierra:', textvariable=self.text_ddt)
        self.Label11.grid(column='0', padx='3', pady='2', row='2', sticky='w')
        self.Labelframe3.rowconfigure('2', weight='25')
        self.Combobox4 = ttk.Combobox(self.Labelframe3)
        self.Combobox4.configure(state='readonly',
            values=["Altura menor",
                "Altura similar",
                "Estructura aislada",
                "Sobre una colina"],
            textvariable=self.extraer_combobox4,
            width=ancho_combobox_labelframe1)
        self.Combobox4.grid(column='1', padx='3', row='0', sticky='e')
        self.Combobox4.current(2)
        self.Labelframe3.columnconfigure('1', weight='1')
        self.Combobox5 = ttk.Combobox(self.Labelframe3)
        self.Combobox5.configure(
            state='readonly',
            values=["Urbano edificios altos",
                    "Urbano",
                    "Suburbano",
                    "Rural"],
            textvariable=self.extraer_combobox5,
            width=ancho_combobox_labelframe1)
        self.Combobox5.grid(column='1', padx='3', pady='2', row='1', sticky='e')
        self.Combobox5.current(1)
        self.Entry7 = ttk.Entry(self.Labelframe3)
        self.Entry7.configure(width='10')
        _text_ = '''4'''
        self.Entry7.delete('0', 'end')
        self.Entry7.insert('0', _text_)
        self.Entry7.grid(column='1', padx='3', pady='2', row='2', sticky='e')

        self.Label31 = ttk.Label(self.Labelframe3)
        self.Label31.configure(text='Resistividad del terreno [Ω.m]')
        self.Label31.grid(column='0', padx='3', pady='2', row='3', sticky='w')
        self.Labelframe3.rowconfigure('3', weight='25')
        self.Entry31 = ttk.Entry(self.Labelframe3)
        
        self.Entry31.configure(width='10')
        _text_ = '''500'''
        self.Entry31.delete('0', 'end')
        self.Entry31.insert('0', _text_)
        self.Entry31.grid(column='1', padx='3', pady='2', row='3', sticky='e')
        self.Radiobutton1 = ttk.Radiobutton(self.Labelframe3)
        # self.Radiobutton1.configure(text='Cálculo DDT latitud longitud',variable=radiobutton_valor, value=1 )
        # self.Radiobutton1.place(anchor='nw', relx='0.01', rely='0.74', x='0', y='0')
        # self.Radiobutton2 = ttk.Radiobutton(self.Labelframe3)
        # self.Radiobutton2.configure(text='Ingresar valor', variable=radiobutton_valor, value=2)
        # self.Radiobutton2.place(anchor='nw', relx='0.47', rely='0.74', x='0', y='0')
        self.Button9 = ttk.Button(self.Labelframe3)
        self.Button9.configure(text='Button9')
        self.Button9.place(anchor='nw', relx='0.82', rely='0.69', x='0', y='0')
        self.Button9.configure(command=self.mostrarseleccionado)
        
        self.Labelframe3.configure(height='450', text='Influencia ambiental', width='200')
        self.Labelframe3.grid(column='0', padx='10', pady='15', row='2', sticky='ew')
        self.Frame1.configure(height='460', width='200')
        self.Frame1.pack(side='top')

        self.Labelframe4 = ttk.Labelframe(self.Frame2)
        self.Label12 = ttk.Label(self.Labelframe4)
        self.Label12.configure(text='Línea que llega a la estructura:')
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
            textvariable=self.extraer_combobox6,
            width=ancho_combobox_labelframe2)
        self.Combobox6.grid(column='1', padx='3', row='0', sticky='e')
        self.Combobox6.current(0)
        self.Labelframe4.columnconfigure('1', weight='1')
        self.Combobox22 = ttk.Combobox(self.Labelframe4)
        self.Combobox22.configure(state='readonly',
            values=["No apantallado",
                "Apantallado"],
            textvariable=self.extraer_combobox22,
            width=ancho_combobox_labelframe2)
        self.Combobox22.grid(column='1', padx='3', row='1', sticky='e')
        self.Combobox22.current(1)
        self.Combobox23 = ttk.Combobox(self.Labelframe4)
        self.Combobox23.configure(state='readonly',
            values=["Transformador",
                "Sin transformador"],
            textvariable=self.extraer_combobox23,
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
            textvariable=self.extraer_combobox7,
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
            textvariable=self.extraer_combobox8,
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
            textvariable=self.extraer_combobox9,
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
            textvariable=self.extraer_combobox10,
            width=ancho_combobox_labelframe2)
        self.Combobox10.grid(column='1', padx='3', row='1', sticky='e')
        self.Combobox10.current(1)
        self.Combobox11 = ttk.Combobox(self.Labelframe7)
        self.Combobox11.configure(
            state='readonly',
            values=["Sin medida de prevención",
                    "Solo en entrada de servicios",
                    "Según NTC42305-4"],
            textvariable=self.extraer_combobox11,
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
            textvariable=self.extraer_combobox12,
            width=ancho_combobox_labelframe3)
        self.Combobox12.grid(column='1', padx='3', row='0', sticky='e')
        self.Combobox12.current(3)


        self.Labelframe8.columnconfigure('1', weight='1')
        self.Combobox13 = ttk.Combobox(self.Labelframe8)
        self.Combobox13.configure(
            state='readonly',
            values=["Otras estructuras",
                    "Iglesias, museos",
                    "Comercios, colegios",
                    "Hospitales, hoteles"],
            textvariable=self.extraer_combobox13,
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
            textvariable=self.extraer_combobox14,
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
            textvariable=self.extraer_combobox15,
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
            textvariable=self.extraer_combobox16,
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
            textvariable=self.extraer_combobox21,
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
            textvariable=self.extraer_combobox17,
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
            textvariable=self.extraer_combobox18,
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
            textvariable=self.extraer_combobox19,
            width=ancho_combobox_labelframe3)
        self.Combobox19.grid(column='1', padx='3', row='2')
        self.Combobox19.current(4)
        self.Combobox20 = ttk.Combobox(self.Labelframe11)
        self.Combobox20.configure(
            state='readonly',
            values=["Sin riesgo de Shock",
                    "Ganado en el interior",
                    "Ganado en el exterior"],
            textvariable=self.extraer_combobox20,
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
            textvariable=self.extraer_combobox24,
            width=ancho_combobox_labelframe3)
        self.Combobox24.grid(column='1', padx='3', row='4')
        self.Combobox24.current(1)
        self.Labelframe11.configure(height='200', text='Pérdidas económicas', width='200')
        self.Labelframe11.grid(column='0', padx='10', pady='10', row='3', sticky='ew')
        self.Frame3.configure(height='200', relief='flat', width='200')
        self.Frame3.pack(side='top')


    def frame2(self):
        self.Frame9 = ttk.Frame(self.Notebook2)
        self.Label65 = ttk.Label(self.Frame9)
        self.img_1 = tk.PhotoImage(file='plot.png')
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
        self.Label40.configure(text='disenador:')
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


    def frame3(self, num):
        if num == 1:
            self.Labelframe13 = ttk.Labelframe(self.Frame7)
        else:
            self.Labelframe13 = ttk.Labelframe(self.Frame14)

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
        self.Entry12 = ttk.Entry(self.Labelframe13)
        self.Entry12.configure(font='TkDefaultFont', state='readonly', width='10')
        _text_ = '''1.00E-5'''
        self.Entry12['state'] = 'normal'
        self.Entry12.delete('0', 'end')
        self.Entry12.insert('0', _text_)
        self.Entry12['state'] = 'readonly'
        self.Entry12.grid(column='1', row='1')
        self.Entry13 = ttk.Entry(self.Labelframe13)
        self.Entry13.configure(state='readonly', width='10')
        _text_ = '''1.00E-3'''
        self.Entry13['state'] = 'normal'
        self.Entry13.delete('0', 'end')
        self.Entry13.insert('0', _text_)
        self.Entry13['state'] = 'readonly'
        self.Entry13.grid(column='1', row='2')
        self.Entry14 = ttk.Entry(self.Labelframe13)
        self.Entry14.configure(state='readonly', width='10')
        _text_ = '''1.00E-3'''
        self.Entry14['state'] = 'normal'
        self.Entry14.delete('0', 'end')
        self.Entry14.insert('0', _text_)
        self.Entry14['state'] = 'readonly'
        self.Entry14.grid(column='1', row='3')
        self.Entry15 = ttk.Entry(self.Labelframe13)
        self.Entry15.configure(state='readonly', width='10')
        _text_ = '''1.00E-3'''
        self.Entry15['state'] = 'normal'
        self.Entry15.delete('0', 'end')
        self.Entry15.insert('0', _text_)
        self.Entry15['state'] = 'readonly'
        self.Entry15.grid(column='1', padx='3', pady='4', row='4')
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




##############################################################
#FUNCIONES STRUCTURAL DIMENSIONS
##############################################################

    def calcular_L_W_H_H_H_p(self, *args):
        self.var_L = float(self.Entry1.get())
        self.var_W = float(self.Entry2.get())
        self.var_H = float(self.Entry3.get())
        self.var_H_P = float(self.Entry4.get())

##############################################################
#FUNCIONES STRUCTURAL ATTRIBUTES
##############################################################
    def calcular_r_f(self, *args):
        if self.Combobox1.current() == 0:
            self.var_r_f = 1
        elif self.Combobox1.current() == 1:
            self.var_r_f = 0.1
        elif self.Combobox1.current() == 2:
            self.var_r_f = 0.01
        elif self.Combobox1.current() == 3:
            self.var_r_f = 0.001
        elif self.Combobox1.current() == 4:
            self.var_r_f = 0


    def calcular_Ks1(self, *args):
        if self.Combobox2.current() == 0:
            self.var_Ks1 = 1
        elif self.Combobox2.current() == 1:
            self.var_Ks1 = 0.2
        elif self.Combobox2.current() == 2:
            self.var_Ks1 = 10 **(-4)


##############################################################
#FUNCIONES ENVIRONMENTAL INFLUENCES
##############################################################

    def calcular_C_d(self, *args):
        if self.Combobox4.current() == 0:
            self.var_C_d = 0.25
        elif self.Combobox4.current() == 1:
            self.var_C_d = 0.5
        elif self.Combobox4.current() == 2:
            self.var_C_d = 1
        elif self.Combobox4.current() == 3:
            self.var_C_d = 2


    def calcular_C_e(self, *args):
        if self.Combobox5.current() == 0:
            self.var_C_e = 0
        elif self.Combobox5.current() == 1:
            self.var_C_e = 0.1
        elif self.Combobox5.current() == 2:
            self.var_C_e = 0.5
        elif self.Combobox5.current() == 3:
            self.var_C_e = 1


    def calcular_DDT(self, *args):
        self.var_DDT = float(self.Entry7.get())



# =============================================================================
# FUNCIONES BUILDING WIRING
# =============================================================================
    '''Factor de características del cableado interno véase la Tabla 17'''
    def calcular_K_s3(self, *args):
        if self.Combobox3.current() == 0:
            self.var_Ks3 = 0.1
        elif self.Combobox3.current() == 1:
            self.var_Ks3 = 1


# =============================================================================
# FUNCIONES CONDUCTIVE SERVICE LINES
# =============================================================================
        '''Power Lines'''

    def calcular_pl(self, *args):
        if self.Combobox6.current() == 0:
            self.var_pl = 1
        elif self.Combobox6.current() == 1:
            self.var_pl = 2
        elif self.Combobox6.current() == 2:
            self.var_pl = 0


    def calcular_P_LD0(self, *args):
        if self.Combobox22.current() == 0:
            self.var_P_LD0 = 1
        elif self.Combobox22.current() == 1:
            self.var_P_LD0 = 0.4

#Tabla 11. Factor de corrección por presencia de transformador'''
    def calcular_C_t0(self, *args):
        if self.Combobox23.current() == 0:
            self.var_C_t0 = 0.2

        elif self.Combobox23.current() == 1:
            self.var_C_t0 = 1


        '''Other Overhead Service Lines:'''

    def calcular_n_oh(self, *args):
        try:
            self.var_n_oh = float(self.Spinbox1.get())

        except ValueError:
            self.var_n_oh = 0

    def calcular_n_ug(self, *args):
        try:
            self.var_n_ug = float(self.Spinbox2.get())

        except ValueError:
            self.var_n_ug = 0


    def calcular_P_LD1(self, *args):
        if self.Combobox7.current() == 0:
            self.var_P_LD1 = 1
        elif self.Combobox7.current() == 1:
            self.var_P_LD1 = 0.4


        '''Conductive Underground Services - Electrical Services e.g.
        Communication Lines'''



    def calcular_P_LD2(self, *args):
        if self.Combobox8.current() == 0:
            self.var_P_LD2 = 1
        elif self.Combobox8.current() == 1:
            self.var_P_LD2 = 0.4


# =============================================================================
# FUNCIONES ACCEPTABLE RISK & LOSS CATEGORIES
# =============================================================================
        '''Loss Category 1 - Loss of Human Life'''
    def calcular_h_1(self, *args):
        if self.Combobox12.current() == 0:
            self.var_h_1 = 1
        elif self.Combobox12.current() == 1:
            self.var_h_1 = 2
        elif self.Combobox12.current() == 2:
            self.var_h_1 = 5
        elif self.Combobox12.current() == 3:
            self.var_h_1 = 10
        elif self.Combobox12.current() == 4:
            self.var_h_1 = 5
        elif self.Combobox12.current() == 5:
            self.var_h_1 = 20
        elif self.Combobox12.current() == 6:
            self.var_h_1 = 50

    def calcular_L_f1(self, *args):
        if self.Combobox13.current() == 0:
            self.var_L_f1 = 0.01
        if self.Combobox13.current() == 1:
            self.var_L_f1 = 0.02
        if self.Combobox13.current() == 2:
            self.var_L_f1 = 0.05
        elif self.Combobox13.current() == 3:
            self.var_L_f1 = 0.1

    def calcular_L_o1(self, *args):
        if self.Combobox14.current() == 0:
            self.var_L_o1 = 0
        if self.Combobox14.current() == 1:
            self.var_L_o1 = 0.1
        elif self.Combobox14.current() == 2:
            self.var_L_o1 = 0.001
        elif self.Combobox14.current() == 3:
            self.var_L_o1 = 0.00001
        elif self.Combobox14.current() == 4:
            self.var_L_o1 = 10 **(-4)


        '''Loss Category 2 - Loss of Essential Service to the Public'''
    def calcular_L_f2(self, *args):
        if self.Combobox15.current() == 0:
            self.var_L_f2 = 0
        if self.Combobox15.current() == 1:
            self.var_L_f2 = 0.01
        elif self.Combobox15.current() == 2:
            self.var_L_f2 = 0.01
        elif self.Combobox15.current() == 3:
            self.var_L_f2 = 0.01
        elif self.Combobox15.current() == 4:
            self.var_L_f2 = 0.01
        elif self.Combobox15.current() == 5:
            self.var_L_f2 = 0.1
        elif self.Combobox15.current() == 6:
            self.var_L_f2 = 0.1

    def calcular_L_o2(self, *args):
        if self.Combobox16.current() == 0:
            self.var_L_o2 = 0
        if self.Combobox16.current() == 1:
            self.var_L_o2 = 0.001
        elif self.Combobox16.current() == 2:
            self.var_L_o2 = 0.001
        elif self.Combobox16.current() == 3:
            self.var_L_o2 = 0.001
        elif self.Combobox16.current() == 4:
            self.var_L_o2 = 0.001
        elif self.Combobox16.current() == 5:
            self.var_L_o2 = 0.01
        elif self.Combobox16.current() == 6:
            self.var_L_o2 = 0.01

        '''Loss Category 3 - Loss of Cultural Heritage'''
    def calcular_L_f3(self, *args):
        if self.Combobox21.current() == 0:
            self.var_L_f3 = 0
        elif self.Combobox21.current() == 1:
            self.var_L_f3 = 0.1

        '''Loss Category 4 - Economic Loss'''

    def calcular_h4(self, *args):
        if self.Combobox17.current() == 0:
            self.var_h4 = 1
        elif self.Combobox17.current() == 1:
            self.var_h4 = 20
        elif self.Combobox17.current() == 2:
            self.var_h4 = 50

    def calcular_L_f4(self, *args):
        if self.Combobox18.current() == 0:
            self.var_L_f4    = 0
        elif self.Combobox18.current() == 1:
            self.var_L_f4 = 0.1
        elif self.Combobox18.current() == 2:
            self.var_L_f4 = 0.2
        elif self.Combobox18.current() == 3:
            self.var_L_f4 = 0.2
        elif self.Combobox18.current() == 4:
            self.var_L_f4 = 0.2
        elif self.Combobox18.current() == 5:
            self.var_L_f4 = 0.2
        elif self.Combobox18.current() == 6:
            self.var_L_f4 = 0.5
        elif self.Combobox18.current() == 7:
            self.var_L_f4 = 0.5
        elif self.Combobox18.current() == 8:
            self.var_L_f4 = 0.5

    def calcular_L_o4(self, *args):
        if self.Combobox19.current() == 0:
            self.var_L_o4 = 0
        elif self.Combobox19.current() == 1:
            self.var_L_o4 = 0.0001
        elif self.Combobox19.current() == 2:
            self.var_L_o4 = 0.001
        elif self.Combobox19.current() == 3:
            self.var_L_o4 = 0.001
        elif self.Combobox19.current() == 4:
            self.var_L_o4 = 0.001
        elif self.Combobox19.current() == 5:
            self.var_L_o4 = 0.01
        elif self.Combobox19.current() == 6:
            self.var_L_o4 = 0.01
        elif self.Combobox19.current() == 7:
            self.var_L_o4 = 0.1

    def calcular_L_t4(self, *args):
        if self.Combobox20.current() == 0:
            self.var_L_t4 = 0
        elif self.Combobox20.current() == 1:
            self.var_L_t4 = 1 * 10**(-2)
        elif self.Combobox20.current() == 2:
            self.var_L_t4 = 1 * 10**(-2)

    def calcular_R_T4(self, *args):
        if self.Combobox24.current() == 0:
            self.var_R_T4 = 0.1
        elif self.Combobox24.current() == 1:
            self.var_R_T4 = 1 * 10**(-2)
        elif self.Combobox24.current() == 2:
            self.var_R_T4 = 1 * 10**(-3)
        elif self.Combobox24.current() == 3:
            self.var_R_T4 = 1 * 10**(-5)
        elif self.Combobox24.current() == 4:
            self.var_R_T4 = 1 * 10**(-5)


# =============================================================================
# FUNCIONESPROTECTION MEASURES IMPLEMENTED
# =============================================================================

    def calcular_E(self, *args):
        if self.Combobox9.current() == 0:
            self.var_E = 0
        elif self.Combobox9.current() == 1:
            self.var_E = 0.8
        elif self.Combobox9.current() == 2:
            self.var_E = 0.9
        elif self.Combobox9.current() == 3:
            self.var_E = 0.95
        elif self.Combobox9.current() == 4:
            self.var_E = 0.98

    def calcular_r(self, *args):
        if self.Combobox10.current() == 0:
            self.var_r = 1
        elif self.Combobox10.current() == 1:
            self.var_r = 0.5
        elif self.Combobox10.current() == 2:
            self.var_r = 0.2

    def calcular_SP(self, *args):
        if self.Combobox11.current() == 0:
            self.var_SP = 0
        elif self.Combobox11.current() == 1:
            self.var_SP = 1
        elif self.Combobox11.current() == 2:
            self.var_SP = 2



# =============================================================================
# 3.1. Direct Strikes to the Structure
# =============================================================================

    def calcular_3_1(self, *args):
        #ecu (6) pag. 35
        if self.var_H > self.var_H_P or self.var_H == self.var_H_P:
            self.var_A_d = ((self.var_L  * self.var_W) 
                            + (6 * self.var_H * (self.var_L + self.var_W)) 
                            + (9 * math.pi * self.var_H ** 2))
        elif self.var_H < self.var_H_P:
            self.var_A_d = (9 * math.pi * self.var_H_P ** 2 )


        _text_ = round(self.var_A_d, 3)
        self.Entry5.delete('0', 'end')
        self.Entry5.insert('0', _text_)


        self.var_N_g = self.var_DDT
        #ecu 5 pag. 34
        self.var_N_D = (self.var_N_g * self.var_A_d * self.var_C_d *10**(-6))


# =============================================================================
# 3.2. Indirect Strikes to the Structure
# =============================================================================

    def calcular_3_2(self, *args):
        
        '''cambio
        self.var_A_m = round((self.var_L * self.var_W) 
                              + (2 * self.var_D_m ) * (self.var_L + self.var_W) 
                              + (math.pi * (self.var_D_m ** 2) 
                              - self.var_A_d * self.var_C_d), 3)'''
        
        self.var_A_m = (2 * self.var_L * self.var_D_m 
                        + 2 * self.var_W * self.var_D_m
                        + math.pi * (self.var_D_m ** 2))

        
        if self.var_A_m < 0:
            self.var_A_m = 0
        else:
            pass


        #ecu (8) pag. 37
        '''cambio
        self.var_N_M = self.var_N_g * self.var_A_m *10**(-6)'''
        self.var_N_M = (self.var_N_g 
                        * (self.var_A_m - self.var_A_d * self.var_C_d )
                        * 10**(-6))


# =============================================================================
# 4. OVERHEAD SERVICE LINES
# =============================================================================

    # def calcular_4(self, *args):
    #     if self.var_C_e > 0.5:
    #         self.var_L_1 = 1000
    #     elif self.var_C_e > 0:
    #         self.var_L_1 = 500
    #     else:
    #         self.var_L_1 = 75

    def calcular_4(self, *args):
        if self.var_C_e > 0.5:
            self.var_L_1 = 1000
            self.var_L_2 = 1000
        elif self.var_C_e > 0:
            self.var_L_1 = 1000
            self.var_L_2 = 1000
        else:
            self.var_L_1 = 1000
            self.var_L_2 = 1000            

                      
        if self.var_pl == 1:
            self.var_n_ohp = 1
        else:
            self.var_n_ohp = 0


# =============================================================================
# 4.1. Direct Strikes to Overhead Lines
# =============================================================================

    def calcular_4_1(self, *args):
        self.var_D_c1 = 3 * self.var_H_c1    
        
        self.var_L_c1 = self.var_L_1 - 3 * self.var_H - 3 * self.var_h_a1
        if self.var_L_c1 == 0:
            self.var_L_c1 = 0
            '''cambio el signo
            elif self.var_L_c1 > 0:'''
        elif self.var_L_c1 < 0:
            self.var_L_c1 = 0
        
        #Tabla 12 AI, pag. 37
        self.var_A_c1 =  2 * self.var_D_c1 * self.var_L_c1 

        self.var_a1 = (self.var_l_a1 * self.var_w_a1 
                       + 6 * self.var_h_a1 * (self.var_l_a1 + self.var_w_a1) 
                       + 9 * math.pi * self.var_h_a1**2)
        
        self.var_N_L1p = self.var_N_g * self.var_A_c1 * self.var_C_t0 * self.var_C_d *10**(-6)   # ct = 0,2


        self.var_N_L1 = self.var_N_g * self.var_A_c1 * self.var_C_t1 * self.var_C_d *10**(-6) # ct1 = 1




# =============================================================================
# 4.2. Indirect Strikes to Overhead Lines
# =============================================================================

    def calcular_4_2 (self, *args):
        #es igual a L_c, pag. 37
        #Tabla 12 Ai, pag. 38
        self.var_A_l1 = 2 *self.var_D_L1 * self.var_L_1

        self.var_N_I1p = (self.var_N_g 
                          * self.var_A_l1 
                          * self.var_C_t0 
                          * self.var_C_e
                          *10**(-6))

        self.var_N_I1 =  (self.var_N_g 
                          * self.var_A_l1 
                          * self.var_C_t1 
                          * self.var_C_e 
                          * 10**(-6))



# =============================================================================
# 5. UNDERGROUND SERVICE LINES
# =============================================================================
    def calcular_5(self, *args):
        if self.var_pl == 2:
            self.var_n_ugp = 1
        else:
            self.var_n_ugp = 0


# =============================================================================
# 5.1. Direct Strikes to Underground Service Lines
# =============================================================================

    def calcular_5_1 (self, *args):
        '''#cambio              
        # self.var_L_c2 = self.var_L_2 - 3 * self.var_H - 3 * self.var_h_a2'''
        self.var_L_c2 = self.var_L_2 


        '''#cambio
        self.var_A_c2 = 2 * self.var_D_c1 * self.var_L_c2 '''

        self.var_A_c2 = (self.var_L_c2 - 3 *(self.var_h_a2 + self.var_H)) * math.isqrt(self.var_P_2)
        
        self.var_A_a2 = (self.var_l_a2 * self.var_w_a2 
                         + 6 * self.var_h_a2 * (self.var_l_a2 + self.var_w_a2) 
                         + 9 * math.pi * self.var_h_a2 **2)
        
        
        self.var_N_L2p = (self.var_N_g 
                          * self.var_A_c2 
                          * self.var_C_t0 
                          * self.var_C_d
                          * 10**(-6))
        
        self.var_N_L2 = (self.var_N_g 
                         * self.var_A_c2 
                         * self.var_C_t2 
                         * self.var_C_d
                         * 10**(-6)) 

        

# =============================================================================
# 5.2. Indirect Strikes to Underground Service Lines
# =============================================================================
    def calcular_5_2 (self, *args):
        #es igual a L_c, pag. 37
        #Tabla 12 Ai, pag. 38
        '''cambio
        self.var_A_l2 = 2 * self.var_D_c1 * self.var_L_2'''
        self.var_A_l2 = 25 * self.var_L_c2 * math.isqrt(self.var_P_2)
        self.var_N_I2p = (self.var_N_g 
                            * self.var_A_l2 
                            * self.var_C_t0 
                            * self.var_C_e
                            * 10**(-6))
        #para líneas aereas auxiliares
        #ecu. 10 pag. 39
        self.var_N_I2 = (self.var_N_g
                         * self.var_A_l2 
                         * self.var_C_t2 
                         * self.var_C_e
                         * 10**(-6))

# =============================================================================
# 6. RISK CALCULATIONS FOR LOSS CATEGORY 1 - LOSS OF HUMAN LIFE
# 6.1. Risk of dangerous step & touch potential inside & outside structure due
# to direct strikes to the structure
# =============================================================================

    def calcular_6_1 (self, *args):
        #(16) pag.49
        self.var_L_a1 = self.var_R_a * self.var_L_t1
        # Tabla 8
        self.var_R_A1 = self.var_N_D * self.var_P_A * self.var_L_a1


# =============================================================================
# 6.2. Risk of physical destruction due to fire, explosion, mechanical damage
# and chemical
# discharge due to direct strikes to the structure
# =============================================================================

    def calcular_6_2 (self, *args):
        self.var_L_B1 = (self.var_r 
                        * self.var_h_1 
                        * self.var_r_f 
                        * self.var_L_f1)

        self.var_P_B1 = 1 - self.var_E 
        self.var_R_B1 = self.var_N_D * self.var_P_B1 * self.var_L_B1



# =============================================================================
# 6.3. Surge Protection Considerations
# =============================================================================

    def calcular_6_3 (self, *args):
        self.var_P_SPD = 0
        self.var_P_EB = 0
        
       
        if self.var_P_B1 > 0.3:
            self.var_P_SPD = 1
        elif self.var_P_B1 > 0.06:
            self.var_P_SPD = 0.03
        elif self.var_P_B1 > 0.03:            
            self.var_P_SPD = 0.02
        else:
            self.var_P_SPD = 0.01   
            
        self.var_P_EB = self.var_P_SPD
        '''cambio
        if self.var_SP > 0:'''
        if self.var_SP == 0:
            self.var_P_EB = 1
        else:
            pass
        
        if self.var_SP < 2:
            self.var_P_SPD = 1
        else:
            pass

# =============================================================================
# 6.4. Risk of electrical/electronic equipment malfunction or failure due to 
# overvoltages from direct strikes to the structure
# =============================================================================

    def calcular_6_4 (self, *args):
        self.var_P_C1 = self.var_P_SPD
        self.var_L_C1 = self.var_L_o1
        self.var_R_C1 = self.var_N_D * self.var_P_C1 * self.var_L_C1     


# =============================================================================
# 6.5. Risk of electrical/electronic equipment function or failure due to 
# overvoltages from indirect strikes to the structure
# =============================================================================

    def calcular_6_5(self, *args):
        self.var_K_MS1 = (self.var_Ks1 
                         * self.var_Ks2 
                         * self.var_Ks3 
                         * self.var_Ks4)
        
        if self.var_K_MS1 == 0.013:
            self.var_P_MS1 = 0.0001
        elif self.var_K_MS1 < 0.013:
            self.var_P_MS1 = 0.0001         
        elif self.var_K_MS1 == 0.014:
            self.var_P_MS1 = 0.001
        elif self.var_K_MS1 < 0.014:
            self.var_P_MS1 = 0.001       
        elif self.var_K_MS1 == 0.015:
            self.var_P_MS1 = 0.003
        elif self.var_K_MS1 < 0.015:
            self.var_P_MS1 = 0.003          
        elif self.var_K_MS1 == 0.016:
            self.var_P_MS1 = 0.005
        elif self.var_K_MS1 < 0.016:
            self.var_P_MS1 = 0.005        
        elif self.var_K_MS1 == 0.021:
            self.var_P_MS1 = 0.01
        elif self.var_K_MS1 < 0.021:
            self.var_P_MS1 = 0.01
        elif self.var_K_MS1 == 0.035:
            self.var_P_MS1 = 0.1            
        elif self.var_K_MS1 < 0.035:
            self.var_P_MS1 = 0.1              
        elif self.var_K_MS1 == 0.07:
            self.var_P_MS1 = 0.5            
        elif self.var_K_MS1 < 0.07:
            self.var_P_MS1 = 0.5              
        elif self.var_K_MS1 == 0.15:
            self.var_P_MS1 = 0.9            
        elif self.var_K_MS1 < 0.15:
            self.var_P_MS1 = 0.9
        else:
            self.var_P_MS1 = 1
        
        if self.var_P_SPD < self.var_P_MS1:
            self.var_P_M1 = self.var_P_SPD
        else:
            self.var_P_M1 = self.var_P_MS1
            
        self.var_L_M1 = self.var_L_o1
        self.var_R_M1 = (self.var_N_M
                         * self.var_P_M1
                         * self.var_L_M1)
        
        

# =============================================================================
# 6.6. Risk of dangerous step & touch potential inside & outside structure due 
# to direct strikes to service lines
# =============================================================================
    def calcular_6_6(self, *args):
        
        if self.var_P_LD0 < self.var_P_EB:
            self.var_P_U1p = self.var_P_LD0
        else:
            self.var_P_U1p = self.var_P_EB
            
        if self.var_P_LD1 < self.var_P_EB:
            self.var_P_U1oh = self.var_P_LD1
        else:
            self.var_P_U1oh = self.var_P_EB
        
        if self.var_P_LD2 < self.var_P_EB:
            self.var_P_U1ug = self.var_P_LD2
        else:
            self.var_P_U1ug = self.var_P_EB       
    

        self.var_X_U1 = (self.var_n_ohp * self.var_N_L1p * self.var_P_U1p      # 1 * 0.025 * 0.02   peb=0.2
                         + self.var_n_oh * self.var_N_L1 * self.var_P_U1oh     # 2 * 0.12 *  0.02   pld1 = 1
                         + self.var_n_ugp * self.var_N_L2p * self.var_P_U1p    # 0 *
                         + self.var_n_ug * self.var_N_L2 * self.var_P_U1ug)    # 2*
        
        self.var_L_U1 = self.var_R_a * self.var_L_t1 # ok
        
        self.var_R_U1 = self.var_X_U1 * self.var_L_U1



# =============================================================================
# 6.7. Risk of physical destruction due to fire,  explosion, mechanical damage 
# and chemical discharge due to direct strikes to service lines
# =============================================================================
    def calcular_6_7(self, *args):
        self.var_P_V1p = self.var_P_U1p
        self.var_P_V1oh1 = self.var_P_U1oh
        self.var_P_V1ug = self.var_P_U1ug
        self.var_X_V1 = self.var_X_U1
        self.var_L_V1 = self.var_L_B1
        self.var_R_V1 = self.var_X_V1 * self.var_L_V1


# =============================================================================
# 6.8. Risk of electrical/electronic equipment malfunction or failure due to 
# overvoltages from direct strikes to service lines
# =============================================================================

    def calcular_6_8(self, *args):
        if self.var_P_LD0 < self.var_P_SPD:
            self.var_P_W1p = self.var_P_LD0
        else:
            self.var_P_W1p = self.var_P_SPD
           
        if self.var_P_LD1 < self.var_P_SPD:
            self.var_P_W1oh = self.var_P_LD1
        else:
            self.var_P_W1oh = self.var_P_SPD        
               
        if self.var_P_LD2 < self.var_P_SPD:
            self.var_P_W1ug = self.var_P_LD2
        else:
            self.var_P_W1ug = self.var_P_SPD


        self.var_X_W1 = (self.var_n_ohp * self.var_N_L1p * self.var_P_W1p # 1 * 0.0127674 * 0.4
                        + self.var_n_oh * self.var_N_L1 * self.var_P_W1oh # 2 * 0.063837 * 1
                        + self.var_n_ugp * self.var_N_L2p * self.var_P_W1p # 0
                        + self.var_n_ug * self.var_N_L2 * self.var_P_W1ug) # 0* * 0.4

        self.var_L_W1 = self.var_L_o1
        self.var_R_W1 = self.var_X_W1 * self.var_L_W1


# =============================================================================
# 6.9. Risk of electrical/electronic equipment malfunction or failure due to 
# overvoltages from indirect strikes to service lines
# =============================================================================

    def calcular_6_9(self, *args):
        self.var_P_Z1p = self.var_P_W1p
        self.var_P_Z1oh = self.var_P_W1oh
        self.var_P_Z1ug = self.var_P_W1ug

        if (self.var_N_I1p - self.var_N_L1p) < 0:
            self.var_DELTA_N_1p = 0
        else:
            self.var_DELTA_N_1p = self.var_N_I1p - self.var_N_L1p

        if (self.var_N_I1 - self.var_N_L1) < 0:
            self.var_DELTA_N_1 = 0
        else:
            self.var_DELTA_N_1 = self.var_N_I1 - self.var_N_L1
         
        if (self.var_N_I2p - self.var_N_L2p) < 0:
            self.var_DELTA_N_2p = 0
        else:
            self.var_DELTA_N_2p = self.var_N_I2p - self.var_N_L2p

        if (self.var_N_I2 - self.var_N_L2) < 0:
            self.var_DELTA_N_2 = 0
        else:
            self.var_DELTA_N_2 = self.var_N_I2 - self.var_N_L2

        self.var_X_Z1 = (self.var_n_ohp * self.var_DELTA_N_1p * self.var_P_Z1p
                        + self.var_n_oh * self.var_DELTA_N_1 * self.var_P_Z1oh
                        + self.var_n_ugp * self.var_DELTA_N_2p * self.var_P_Z1p
                        + self.var_n_ug * self.var_DELTA_N_2 * self.var_P_Z1ug)

        self.var_L_Z1 = self.var_L_o1
        
        self.var_R_Z1 = self.var_X_Z1 * self.var_L_Z1


# =============================================================================
# 6.10. Total Risk of Electric Shock to animals and people (R1)
# =============================================================================

    def calcular_6_10(self, *args):
        self.var_R_d1 = self.var_R_A1 + self.var_R_B1 + self.var_R_C1
        self.var_R_i1 = self.var_R_M1 + self.var_R_U1 + self.var_R_V1 + self.var_R_W1 + self.var_R_Z1
        self.var_R_1 = self.var_R_i1 + self.var_R_d1
        self.var_R_S1 = self.var_R_A1 + self.var_R_U1
        self.var_R_F1 = self.var_R_B1 + self.var_R_V1
        self.var_R_o1 = (self.var_R_C1
                         + self.var_R_M1 
                         + self.var_R_W1 
                         + self.var_R_Z1)
        
        
# =============================================================================
# 7. RISK CALCULATIONS FOR LOSS CATEGORY 2 - LOSS OF ESSENTIAL SERVICE TO THE 
# PUBLIC
# 7.1. Risk of physical destruction due to fire, Explosion, mechanical damage 
# and chemical discharge due to direct strikes to the structure
# =============================================================================
    def calcular_7_1(self, *args):
        self.var_L_B2 = self.var_r * self.var_r_f * self.var_L_f2
        self.var_P_B2 = self.var_P_B1
        self.var_R_B2 = self.var_N_D * self.var_P_B2 * self.var_L_B2 

# =============================================================================
# 7.2. Risk of electrical/electronic equipment malfunction or failure due to 
# overvoltages from direct strikes to the structure
# =============================================================================
    def calcular_7_2(self, *args):
        self.var_P_C2 = self.var_P_C1
        self.var_L_C2 = self.var_L_o2
        self.var_R_C2 = self.var_N_D * self.var_P_C2 * self.var_L_C2 #   ,1


    def calcular_7_3(self, *args):
        self.var_P_M2 = self.var_P_M1
        self.var_L_M2 = self.var_L_o2
        self.var_R_M2 = self.var_N_M * self.var_P_M2 * self.var_L_M2

    def calcular_7_4(self, *args):
        self.var_X_V2 = self.var_X_V1
        self.var_L_V2 = self.var_L_B2
        self.var_R_V2 = self.var_X_V1 * self.var_L_B2

    def calcular_7_5(self, *args):
        self.var_X_W2 = self.var_X_W1
        self.var_L_W2 = self.var_L_o2
        self.var_R_W2 = self.var_X_W2 * self.var_L_W2 

    def calcular_7_6(self, *args):
        self.var_X_Z2 = self.var_X_Z1
        self.var_L_Z2 = self.var_L_o2
        self.var_R_Z2 = self.var_X_Z2 * self.var_L_Z2

    def calcular_7_7(self, *args):
        self.var_R_d2 = self.var_R_B2 + self.var_R_C2
        self.var_R_i2 = (self.var_R_M2  #0
                         + self.var_R_V2 #0
                         + self.var_R_W2 
                         + self.var_R_Z2)
        self.var_R_2 = self.var_R_i2 + self.var_R_d2
        self.var_R_F2 = self.var_R_B2 + self.var_R_V2
        self.var_R_o2 = (self.var_R_C2 
                         + self.var_R_M2 
                         + self.var_R_W2 
                         + self.var_R_Z2)

# =============================================================================
# 8. RISK CALCULATIONS FOR LOSS CATEGORY 3 - LOSS OF CULTURAL HERITAGE
# =============================================================================
    def calcular_8_1(self, *args):
        self.var_L_B3 = self.var_r * self.var_r_f * self.var_L_f3
        self.var_P_B3 = self.var_P_B1
        self.var_R_B3 = self.var_N_D * self.var_P_B3 * self.var_L_B3

    def calcular_8_2(self, *args):
        self.var_X_V3 = self.var_X_V1
        self.var_L_V3 = self.var_L_B3
        self.var_R_V3 = self.var_X_V3 * self.var_L_V3

    def calcular_8_3(self, *args):
        self.var_R_d3 = self.var_R_B3
        self.var_R_i3 = self.var_R_V3
        self.var_R_3 = self.var_R_i3 + self.var_R_d3
        self.var_R_F3 = self.var_R_B3 + self.var_R_V3
        self.var_R_o3 = 0

# =============================================================================
# 9. RISK CALCULATIONS FOR LOSS CATEGORY 4 - ECONOMIC LOSS
# =============================================================================
    def calcular_9_1(self, *args):
        self.var_L_a4 = self.var_R_a * self.var_L_t4
        self.var_R_A4 = self.var_N_D * self.var_P_A * self.var_L_a4


    def calcular_9_2(self, *args):
        self.var_L_B4 = self.var_r * self.var_h4 * self.var_r_f * self.var_L_f4
        self.var_P_B4 = self.var_P_B1
        self.var_R_B4 = self.var_N_D * self.var_P_B4 * self.var_L_B4

    def calcular_9_3(self, *args):
        self.var_P_C4 = self.var_P_C1
        self.var_L_C4 = self.var_L_o4
        self.var_R_C4 = self.var_N_D * self.var_P_C4 * self.var_L_C4

    def calcular_9_4(self, *args):
        self.var_P_M4 = self.var_P_M1
        self.var_L_M4 = self.var_L_o4
        self.var_R_M4 = self.var_N_M * self.var_P_M4 * self.var_L_M4

    def calcular_9_5(self, *args):
        self.var_X_U4 = self.var_X_U1
        self.var_L_U4 = self.var_R_a * self.var_L_t4
        self.var_R_U4 = self.var_X_U4 * self.var_L_U4

    def calcular_9_6(self, *args):        
        self.var_X_V4 = self.var_X_V1
        self.var_L_V4 = self.var_L_B4
        self.var_R_V4 = self.var_X_V4 * self.var_L_V4

    def calcular_9_7(self, *args):
        self.var_X_W4 = self.var_X_W1
        self.var_L_W4 = self.var_L_o4
        self.var_R_W4 = self.var_X_W4 * self.var_L_W4 

    def calcular_9_8(self, *args):
        self.var_X_Z4 = self.var_X_Z1
        self.var_L_Z4 = self.var_L_o4
        self.var_R_Z4 = self.var_X_Z4 * self.var_L_Z4

    def calcular_9_9(self, *args):
        self.var_R_d4 = self.var_R_A4 + self.var_R_B4 + self.var_R_C4
        self.var_R_i4 = (self.var_R_M4 
                         + self.var_R_U4 
                         + self.var_R_V4 
                         + self.var_R_W4 
                         + self.var_R_Z4)
        self.var_R_4 = self.var_R_i4 + self.var_R_d4
        self.var_R_S4 = self.var_R_A4 + self.var_R_U4
        self.var_R_F4 = self.var_R_B4 + self.var_R_V4
        self.var_R_o4 = (self.var_R_C4 
                         + self.var_R_M4 
                         +self.var_R_W4 
                         + self.var_R_Z4)


        _text_ = "{:.2e}".format(self.var_R_d1)
        self.Entry16['state'] = 'normal'
        self.Entry16.delete('0', 'end')
        self.Entry16.insert('0', _text_)
        self.Entry16['state'] = 'readonly'
        self.Entry16.grid(column='3', row='1')

        _text_ = "{:.2e}".format(self.var_R_d2)
        self.Entry17['state'] = 'normal'
        self.Entry17.delete('0', 'end')
        self.Entry17.insert('0', _text_)
        self.Entry17['state'] = 'readonly'
        self.Entry17.grid(column='3', row='2')

        _text_ = "{:.2e}".format(self.var_R_d3)
        self.Entry18['state'] = 'normal'
        self.Entry18.delete('0', 'end')
        self.Entry18.insert('0', _text_)
        self.Entry18['state'] = 'readonly'
        self.Entry18.grid(column='3', row='3')

        _text_ = "{:.2e}".format(self.var_R_d4)
        self.Entry19['state'] = 'normal'
        self.Entry19.delete('0', 'end')
        self.Entry19.insert('0', _text_)
        self.Entry19['state'] = 'readonly'
        self.Entry19.grid(column='3', row='4')


        _text_ = "{:.2e}".format(self.var_R_i1)
        self.Entry20['state'] = 'normal'
        self.Entry20.delete('0', 'end')
        self.Entry20.insert('0', _text_)
        self.Entry20['state'] = 'readonly'
        self.Entry20.grid(column='5', row='1')

        _text_ = "{:.2e}".format(self.var_R_i2)
        self.Entry21['state'] = 'normal'
        self.Entry21.delete('0', 'end')
        self.Entry21.insert('0', _text_)
        self.Entry21['state'] = 'readonly'
        self.Entry21.grid(column='5', row='2')

        _text_ = "{:.2e}".format(self.var_R_i3)
        self.Entry22['state'] = 'normal'
        self.Entry22.delete('0', 'end')
        self.Entry22.insert('0', _text_)
        self.Entry22['state'] = 'readonly'
        self.Entry22.grid(column='5', row='3')

        _text_ = "{:.2e}".format(self.var_R_i4)
        self.Entry23['state'] = 'normal'
        self.Entry23.delete('0', 'end')
        self.Entry23.insert('0', _text_)
        self.Entry23['state'] = 'readonly'
        self.Entry23.grid(column='5', row='4')



        _text_ = "{:.2e}".format(self.var_R_1)
        self.Entry24['state'] = 'normal'
        self.Entry24.delete('0', 'end')
        self.Entry24.insert('0', _text_)
        self.Entry24['state'] = 'readonly'
        self.Entry24.grid(column='7', row='1')

        _text_ = "{:.2e}".format(self.var_R_2)
        self.Entry25['state'] = 'normal'
        self.Entry25.delete('0', 'end')
        self.Entry25.insert('0', _text_)
        self.Entry25['state'] = 'readonly'
        self.Entry25.grid(column='7', row='2')

        _text_ = "{:.2e}".format(self.var_R_3)
        self.Entry26['state'] = 'normal'
        self.Entry26.delete('0', 'end')
        self.Entry26.insert('0', _text_)
        self.Entry26['state'] = 'readonly'
        self.Entry26.grid(column='7', row='3')

        _text_ = "{:.2e}".format(self.var_R_4)
        self.Entry27['state'] = 'normal'
        self.Entry27.delete('0', 'end')
        self.Entry27.insert('0', _text_)
        self.Entry27['state'] = 'readonly'
        self.Entry27.grid(column='7', row='4')

    def calcular_informe(self):
        a = self.pasar_tupla_a_dicionario
        PDF_Creator.crear(a)




    def valores(self, *args):
        global proyecto
        global disenador  
        global direccion
        global telefono

        self.lst = [
           ('var_L_2',"{:.3e}".format(self.var_L_2)),
           ('var_R_Z4',"{:.3e}".format(self.var_R_Z4)),
           ('var_R_W4',"{:.3e}".format(self.var_R_W4)),
           ('var_R_V4',"{:.3e}".format(self.var_R_V4)),
           ('var_R_U4',"{:.3e}".format(self.var_R_U4)),
           ('var_R_M4',"{:.3e}".format(self.var_R_M4)),
           ('var_R_C4',"{:.3e}".format(self.var_R_C4)),
           ('var_R_B4',"{:.3e}".format(self.var_R_B4)),
           ('var_R_A4',"{:.3e}".format(self.var_R_A4)),
           

           ('var_R_V3',"{:.3e}".format(self.var_R_V3)),
           ('var_R_B3',"{:.3e}".format(self.var_R_B3)),
           ('var_R_Z2',"{:.3e}".format(self.var_R_Z2)),
           ('var_R_W2',"{:.3e}".format(self.var_R_W2)),
           ('var_R_V2',"{:.3e}".format(self.var_R_V2)),
           ('var_R_M2',"{:.3e}".format(self.var_R_M2)),
           ('var_R_C2',"{:.3e}".format(self.var_R_C2)),
           ('var_R_B2',"{:.3e}".format(self.var_R_B2)),
           ('var_R_Z1',"{:.3e}".format(self.var_R_Z1)),
           ('var_R_W1',"{:.3e}".format(self.var_R_W1)),
           ('var_R_V1',"{:.3e}".format(self.var_R_V1)),
           ('var_R_U1',"{:.3e}".format(self.var_R_U1)),
           ('var_R_M1',"{:.3e}".format(self.var_R_M1)),
           ('var_R_C1',"{:.3e}".format(self.var_R_C1)),
           ('var_R_B1',"{:.3e}".format(self.var_R_B1)),
           ('var_R_A1',"{:.3e}".format(self.var_R_A1)),




           ('var_L',self.var_L),
           ('var_W',self.var_W),
           ('var_H',self.var_H),
           ('var_H_P',self.var_H_P),
           ('var_r_f',self.var_r_f),
           ('var_Ks1',self.var_Ks1),
           ('var_C_d',self.var_C_d),
           ('var_C_e',self.var_C_e),
           ('var_DDT',self.var_DDT),
           ('var_N_g',self.var_N_g),
           ('var_Ks3',self.var_Ks3),
           ('var_pl',self.var_pl),
           ('var_P_LD0',self.var_P_LD0),
           ('var_C_t0',self.var_C_t0),
           ('var_n_oh',self.var_n_oh),
           ('var_P_LD1',self.var_P_LD1),
           ('var_n_ug',self.var_n_ug),
           ('var_P_LD2',self.var_P_LD2),
           ('var_h_1',self.var_h_1),
           ('var_L_f1',self.var_L_f1),
           ('var_L_o1',self.var_L_o1),
           ('var_L_f2',self.var_L_f2),
           ('var_L_o2',self.var_L_o2),
           ('var_L_f3',self.var_L_f3),
           ('var_h4',self.var_h4),
           ('var_L_f4',self.var_L_f4),
           ('var_L_o4',self.var_L_o4),
           ('var_L_t4',self.var_L_t4),
           ('var_R_T4',self.var_R_T4),
           ('var_E',self.var_E),
           ('var_r',self.var_r),
           ('var_SP',self.var_SP),
           ('var_A_d',round(self.var_A_d, 0)),
           ('var_N_D',"{:.3e}".format(self.var_N_D)),
           ('var_A_m',round(self.var_A_m, 0)),
           ('var_N_M',"{:.3e}".format(self.var_N_M)),          
           ('var_L_1',self.var_L_1),
           ('var_L_2',self.var_L_2),
           ('var_Ks2',self.var_Ks2),
           ('var_P_A',self.var_P_A),
           ('var_D_m',self.var_D_m),
           ('var_Ks4',self.var_Ks4),
           ('var_H_c1',self.var_H_c1),
           ('var_D_L1',self.var_D_L1),
           ('var_C_t1',self.var_C_t1),
           ('var_l_a1',self.var_l_a1),
           ('var_w_a1',self.var_w_a1),
           ('var_h_a1',self.var_h_a1),
           ('var_P_2',self.var_P_2),
           ('var_C_t2',self.var_C_t2),
           ('var_l_a2',self.var_l_a2),
           ('var_w_a2',self.var_w_a2),
           ('var_h_a2',self.var_h_a2),
           ('var_R_T1',self.var_R_T1),
           ('var_L_t1',self.var_L_t1),
           ('var_R_a',self.var_R_a),
           ('var_R_T2',self.var_R_T2),
           ('var_R_T3',self.var_R_T3),
           ('var_n_ohp',self.var_n_ohp),
           ('var_D_c1',self.var_D_c1),
           ('var_L_c1',self.var_L_c1),
           ('var_A_c1',round(self.var_A_c1, 0)),
           ('var_a1',self.var_a1),
           ('var_N_L1p',self.var_N_L1p),
           ('var_N_L1',"{:.3e}".format(self.var_N_L1)),   
           ('var_A_l1',self.var_A_l1),
           ('var_N_I1p',self.var_N_I1p),
           ('var_N_I1',self.var_N_I1),
           ('var_n_ugp',self.var_n_ugp),
           ('var_L_c2',self.var_L_c2),
           ('var_A_c2',round(self.var_A_c2, 0)),
           ('var_A_a2',self.var_A_a2),
           ('var_N_L2p',self.var_N_L2p),
           ('var_N_L2',"{:.3e}".format(self.var_N_L2)),
           ('var_A_l2',round(self.var_A_l2, 0)),          
           ('var_N_I2p',self.var_N_I2p),
           ('var_N_I2',"{:.3e}".format(self.var_N_I2)),  
           ('var_L_a1',self.var_L_a1),
           ('var_L_B1',self.var_L_B1),
           ('var_P_B1',self.var_P_B1),
           ('var_P_SPD',self.var_P_SPD),
           ('var_P_EB',self.var_P_EB),
           ('var_P_C1',self.var_P_C1),
           ('var_L_C1',self.var_L_C1),
           ('var_K_MS1',self.var_K_MS1),
           ('var_P_MS1',self.var_P_MS1),
           ('var_P_M1',self.var_P_M1),
           ('var_L_M1',self.var_L_M1),
           ('var_P_U1p',self.var_P_U1p),
           ('var_P_U1oh',self.var_P_U1oh),
           ('var_P_U1ug',self.var_P_U1ug),
           ('var_X_U1',self.var_X_U1),
           ('var_L_U1',self.var_L_U1),
           ('var_P_V1p',self.var_P_V1p),
           ('var_P_V1oh1',self.var_P_V1oh1),
           ('var_P_V1ug',self.var_P_V1ug),
           ('var_X_V1',self.var_X_V1),
           ('var_L_V1',self.var_L_V1),
           ('var_P_W1p',self.var_P_W1p),
           ('var_P_W1oh',self.var_P_W1oh),
           ('var_P_W1ug',self.var_P_W1ug),
           ('var_X_W1',self.var_X_W1),
           ('var_L_W1',self.var_L_W1),
           ('var_P_Z1p',self.var_P_Z1p),
           ('var_P_Z1oh',self.var_P_Z1oh),
           ('var_P_Z1ug',self.var_P_Z1ug),
           ('var_DELTA_N_1p',self.var_DELTA_N_1p),
           ('var_DELTA_N_1',self.var_DELTA_N_1),
           ('var_DELTA_N_2p',self.var_DELTA_N_2p),
           ('var_DELTA_N_2',self.var_DELTA_N_2),
           ('var_X_Z1',self.var_X_Z1),
           ('var_L_Z1',self.var_L_Z1),
           ('var_R_d1',"{:.3e}".format(self.var_R_d1)),
           ('var_R_i1',"{:.3e}".format(self.var_R_i1)),
           ('', ''),
           ('', ''),
           ('', ''),
           ('var_L_o4', self.var_L_o4),
           ('var_R_1',"{:.3e}".format(self.var_R_1) ),
           ('var_R_S1',self.var_R_S1),
           ('var_R_F1', self.var_R_F1),
           ('var_R_o1', self.var_R_o1),
           ('var_L_B2', self.var_L_B2),
           ('var_P_B2', self.var_P_B2),
           ('var_P_C2', self.var_P_C2),
           ('var_L_C2', self.var_L_C2),           
           ('var_P_M2', self.var_P_M2),
           ('var_L_M2', self.var_L_M2),
           ('var_X_V2', self.var_X_V2),
           ('var_L_V2', self.var_L_V2),
           ('var_X_W2', self.var_X_W2),
           ('var_L_W2', self.var_L_W2),
           ('var_X_Z2', self.var_X_Z2),
           ('var_L_Z2', self.var_L_Z2),
           ('var_R_d2',"{:.3e}".format(self.var_R_d2)),
           ('var_R_i2',"{:.3e}".format(self.var_R_i2)),
           ('var_R_2',"{:.3e}".format(self.var_R_2)),
           ('var_R_F2', self.var_R_F2),
           ('var_R_o2', self.var_R_o2),
           ('var_L_B3', self.var_L_B3),
           ('var_P_B3', self.var_P_B3),           
           ('var_X_V3', self.var_X_V3),
           ('var_L_V3', self.var_L_V3),
           ('var_R_d3',"{:.3e}".format(self.var_R_d3)),
           ('var_R_i3',"{:.3e}".format(self.var_R_i3)),
           ('var_R_3',"{:.3e}".format(self.var_R_3)),       
           ('var_R_F3', self.var_R_F3),
           ('var_R_o3', self.var_R_o3),
           ('var_L_a4', self.var_L_a4),           
           ('var_L_B4', self.var_L_B4),
           ('var_P_B4', self.var_P_B4),
           ('var_P_C4', self.var_P_C4),
           ('var_L_C4', self.var_L_C4),
           ('var_P_M4', self.var_P_M4),
           ('var_L_M4', self.var_L_M4),
           ('var_X_U4', self.var_X_U4),
           ('var_L_U4', self.var_L_U4),
           ('var_X_V4', self.var_X_V4),
           ('var_L_V4', self.var_L_V4),
           ('var_X_W4', self.var_X_W4),
           ('var_L_W4', self.var_L_W4),
           ('var_X_Z4', self.var_X_Z4),
           ('var_L_Z4', self.var_L_Z4),
           ('var_R_d4',"{:.3e}".format(self.var_R_d4)),
           ('var_R_i4',"{:.3e}".format(self.var_R_i4)),
           ('var_R_4',"{:.3e}".format(self.var_R_4)),     
           ('var_R_S4', self.var_R_S4),
           ('var_R_F4', self.var_R_F4),
           ('var_R_o4', self.var_R_o4),
           ('Combobox1', self.extraer_combobox1.get()),
           ('Combobox2', self.extraer_combobox2.get()),
           ('Combobox3', self.extraer_combobox3.get()),
           ('Combobox4', self.extraer_combobox4.get()),
           ('Combobox5', self.extraer_combobox5.get()),
           ('Combobox6', self.extraer_combobox6.get()),
           ('Combobox7', self.extraer_combobox7.get()),
           ('Combobox8', self.extraer_combobox8.get()),
           ('Combobox9', self.extraer_combobox9.get()),
           ('Combobox10', self.extraer_combobox10.get()),
           ('Combobox11', self.extraer_combobox11.get()),
           ('Combobox12', self.extraer_combobox12.get()),
           ('Combobox13', self.extraer_combobox13.get()),
           ('Combobox14', self.extraer_combobox14.get()),
           ('Combobox15', self.extraer_combobox15.get()),
           ('Combobox16', self.extraer_combobox16.get()),
           ('Combobox17', self.extraer_combobox17.get()),
           ('Combobox18', self.extraer_combobox18.get()),
           ('Combobox19', self.extraer_combobox19.get()),
           ('Combobox20', self.extraer_combobox20.get()),
           ('Combobox21', self.extraer_combobox21.get()),
           ('Combobox22', self.extraer_combobox22.get()),
           ('Combobox23', self.extraer_combobox23.get()),
           ('Combobox24', self.extraer_combobox24.get()),
           ('Spinbox1', self.Spinbox1.get()),
           ('Spinbox2', self.Spinbox2.get()),

           ('proyecto', proyecto),
           ('disenador',disenador),
           ('direccion', direccion),
           ('telefono',telefono),

           ] 

        
        # self.total_rows = len(self.lst)
        # self.total_columns = len(self.lst[0]) 
    
        # self.ventana_nueva2 = tk.Toplevel()
        # self.ventana_nueva2.geometry("400x200")
        # self.ventana_nueva2.title("Ventana secundaria")

        
        # self.scrollbar = tk.Scrollbar(self.ventana_nueva2)
        # self.scrollbar.pack(side="right", fill="y")

        # self.listbox = tk.Listbox(self.ventana_nueva2, yscrollcommand=self.scrollbar.set)
        # for i in range(self.total_rows):
        #     for j in range(self.total_columns):
        #             self.listbox.insert('end', self.lst[i][j]) 
        # self.listbox.pack(side="left", fill="both")

        # self.scrollbar.config(command=self.listbox.yview)

        

# converting to dictionary
        self.pasar_tupla_a_dicionario = dict(self.lst)

# printing the result dict
#       print(self.pasar_tupla_a_dicionario)
        print(type(self.pasar_tupla_a_dicionario))

    
    def changeText(self):
        a = ventana_auxiliar.DDT
        self.text_ddt.set(a)
        self.var_DDT = a
        print(str(a))


class App(tk.Frame):
    """Clase principal que crea los diferentes paneles y los "conecta" entre
    sí de modo que la función .siguiente() de uno llame al .mostrar() del
    siguiente"""
    def __init__(self, master):
        super().__init__()

        # Creacion de los paneles
        modo = Modo(master, titulo="Modo", ancho=740, alto=452)

        principal_guiado = Principal_guiado(
            master, titulo="principal guiadooooo", ancho=1366, alto=768
        )

        principal_compacto = Principal_compacto(
            master, titulo="principal compacto", ancho=1366, alto=768
        )

        # Conexión entre sí de la secuencia
        modo.siguiente = principal_compacto.mostrar
        modo.siguienteguiado = principal_guiado.mostrar
        principal_guiado.anterior_modo = modo.mostrar
        principal_compacto.anterior_modo = modo.mostrar

        # Configuración de los  frames
        for frame in (principal_compacto, principal_guiado, modo):
            frame.place(x=0, y=0, relwidth=1, relheight=1)

        # Empezamos por el de modo

        modo.mostrar()



def main():
    """El programa principal instancia la ventana raiz Tk() y la usa
    para inicializar la aplicación y el bucle de eventos"""
    root = tk.Tk()
    root.tk.call("source", "azure.tcl")
    root.tk.call("set_theme", "dark")   
    app = App(root)
    root.mainloop()
    # Simply set the theme


if __name__ == "__main__":
    main()



