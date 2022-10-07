#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May  7 23:26:04 2022

@author: Sergio Andrés Estrada Vélez
"""

import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox

#importa el archivo netCDF4
from netCDF4 import Dataset



class Calculo_DDT:
    def __init__(self, master=None):
        # build ui
         # Como StrinVar pero en entero
        
        self.Toplevel1 = tk.Tk() if master is None else tk.Toplevel(master)
        self.opcion_radiobuttons = tk.IntVar()
        self.Label50 = ttk.Label(self.Toplevel1)
        self.Label50.configure(text='Cálculo DDT')
        self.Label50.grid(column='0', pady='15', row='0', sticky='e')
        self.Radiobutton1 = ttk.Radiobutton(self.Toplevel1)
        self.Radiobutton1.configure(text='Cálculo DDT latitud y longitud', value=1, variable=self.opcion_radiobuttons)
        self.Radiobutton1.grid(column='0', padx='20', pady='4', row='1')
        self.Radiobutton1.configure(command=self.calculo_latitud_longitud)
        self.Radiobutton2 = ttk.Radiobutton(self.Toplevel1)
        self.Radiobutton2.configure(text='Ingresar DDT manual', value=2, variable=self.opcion_radiobuttons)
        self.Radiobutton2.grid(column='1', padx='20', pady='4', row='1')
        self.Radiobutton2.configure(command=self.calculo_ingresar_ddt)
        self.Entry50 = ttk.Entry(self.Toplevel1)
        self.Entry50.configure(state='disabled')
        self.Entry50.grid(column='1', padx='10', pady='4', row='2')
        self.Entry51 = ttk.Entry(self.Toplevel1)
        self.Entry51.configure(state='disabled')
        self.Entry51.grid(column='1', pady='4', row='3')
        self.Label51 = ttk.Label(self.Toplevel1)
        self.Label51.configure(text='Ingrese Latitud')
        self.Label51.grid(column='0', row='2')
        self.Label52 = ttk.Label(self.Toplevel1)
        self.Label52.configure(text='Ingrese Longitud')
        self.Label52.grid(column='0', row='3')
        self.Entry52 = ttk.Entry(self.Toplevel1)
        self.Entry52.configure(state='disabled')
        self.Entry52.grid(column='1', pady='4', row='4')
        self.Label53 = ttk.Label(self.Toplevel1)
        self.Label53.configure(text='Ingrese DDT')
        self.Label53.grid(column='0', row='4')
        self.Button11 = ttk.Button(self.Toplevel1)
        self.Button11.configure(text='Calcular')
        self.Button11.grid(column='0', pady='10', row='5')
        self.Button11.grid_propagate(0)
        self.Label54 = ttk.Label(self.Toplevel1)
        self.Label54.configure(text='Label5')
        self.Label54.grid(column='1', row='5')
        self.Button11.configure(state='diabled', command=self.calcular_ddt)
        self.Toplevel1.configure(height='200', width='200')

        # Main widget
        self.mainwindow = self.Toplevel1
        
    def __str__(self):
        return str(DDT)     

    
    def run(self):
        self.mainwindow.mainloop()

    def calculo_latitud_longitud(self):
        self.Label53.configure(state='disabled', text='Ingrese DDT')
        self.Entry52.configure(state='disabled')
        self.Label51.configure(state='normal', text='Ingrese Latitud')
        self.Label52.configure(state='normal', text='Ingrese Longitud')
        self.Entry50.configure(state='normal')
        self.Entry51.configure(state='normal')
        self.Button11.configure(state='normal', command=self.calcular_ddt)
        
    def calculo_ingresar_ddt(self):
        self.Label51.configure(state='disabled', text='Ingrese Latitud')
        self.Label52.configure(state='disabled', text='Ingrese Longitud')
        self.Entry50.configure(state='disabled')
        self.Entry51.configure(state='disabled')
        self.Label53.configure(state='normal', text='Ingrese DDT') 
        self.Entry52.configure(state='normal')       
        self.Button11.configure(state='normal', command=self.calcular_ddt)
        
    def calcular_ddt(self):
        global DDT
        if self.opcion_radiobuttons.get() == 1:
            try:
                if float(self.Entry50.get()):
                    lat_x = float(self.Entry50.get())
                    if float(self.Entry51.get()):
                        lon_y = float(self.Entry51.get())

                        DDT = self.calcular_ddt_con_lat_long(lat_x, lon_y)
                        messagebox.showinfo(message=
                                            'La DDT en el punto:'
                                            + " \n "
                                            + "\nlatitud= " + str(lat_x) 
                                            + '\nlongitud= ' + str(lon_y) 
                                            + " es: \n"
                                            + "_______________________________       \n"
                                            + " \n "
                                            + "DDT= "
                                            + str(DDT) 
                                            + " rayos/km2", 
                                            title="Resultado DDT")
            except:
                messagebox.showinfo(message="¡Compa! recuerda que debes ingresar números, separarlo con punto, no por coma ", title="Algo raro por aquí")       

        if self.opcion_radiobuttons.get() == 2:
            try:
                if float(self.Entry52.get()):
                    DDT = float(self.Entry52.get())
                    messagebox.showinfo(message="La DDT es:" 
                                        + str(DDT) 
                                        + " rayos/km2", 
                                        title="Algo raro por aquí")
            except:
                messagebox.showinfo(message="¡Compa! recuerda que debes ingresar números, separarlo con punto, no por coma ", title="Algo raro por aquí") 
        
        
    def calcular_ddt_con_lat_long(self, lat_x, lon_y):
        if self.opcion_radiobuttons.get() == 1:

            #Lee el archivo netCDF
            data = Dataset('lis_vhrfc_1998_2013_v01.2.nc', 'r')
            
            # Almacena las variables 
            lat = data.variables['Latitude'][:]
            lon = data.variables['Longitude'][:]
            
            # Almacena las variables de rayos y los multiplica por ratio 
            rayos = data.variables['VHRFC_LIS_FRD'][:] * 0.227
            
            # Almacena la lat. y long. que ingresa el usuario
            lat_x = lat_x
            lon_y = lon_y
            
            # Saca el cuadrado de la diferencia entre lat y lon
            sq_diff_lat = (lat - lat_x)**2
            sq_diff_lon = (lon - lon_y)**2
            
            #cierra el archivo para desocupar la memoría
            data.close()
            
            # Identifica el indice menor entre lat y lon
            min_index_lat = sq_diff_lat.argmin()
            min_index_lon = sq_diff_lon.argmin()
            
            #print(rayos[min_index_lat, min_index_lon] ) #,rayos.units
            #10.32396 flashes/km^2/year
            #lat_medellin = 6.251
            #lon_medellin = -75.563
        return rayos[min_index_lat, min_index_lon]



if __name__ == '__main__':
    app = Calculo_DDT()
    app.run()