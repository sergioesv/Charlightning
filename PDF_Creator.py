# refrernce : https://pyfpdf.readthedocs.io/en/latest/Tutorial/index.html
# Created by Sowmya.R

import os

from fpdf import FPDF


def crear(a):
    a = a
    
    ancho_celda1 = 55
    alto_celda1 = 4
    ancho_celda2 = 35
    alto_celda2 = 4
  # refrernce : https://pyfpdf.readthedocs.io/en/latest/Tutorial/index.html
# Created by Sowmya.R



def crear(a):
    a = a
    print(type(a))
    print('hola aqui voy')
    print(a)
#   print (a.get('L_2'))
    #creating a pdf 
    # A4 portrait and the measure unit is millimeter ==> this is default even if the parameter is not given
    #other measuring units ==> pt, cm, in
    #a4 page 210 X 297 mm
    pdf = FPDF('P', 'mm', 'A4')
    pdf.add_page() 
    # bold = B, italics=I, underline = U. Font size in Points
    # standard font names are Arial, Times, Courier, Symbol and ZapfDingbats
    # Arial bold 16

    
    ## We can now print a cell with cell. A cell is a rectangular area, possibly framed, which contains some text. 
    # It is output at the current position. 
    # We specify its dimensions, its text (centered or aligned), if borders should be drawn, and 
    # where the current position moves after it (to the right, below or to the beginning of the next line).
    #cell(width, height, borderYes?,gotoNewlineNext?,textalignment)
    ancho_celda1 = 55
    alto_celda1 = 4
    ancho_celda2 = 35
    alto_celda2 = 4
    

    pdf.set_font('Arial', 'B', 16)    
    #pdf.set_draw_color(r=255, g=255, b=255)
    
    pdf.cell(190, 10, 'CÁLCULO DEL RIESGO SEGÚN NTC 4552-2', 1, 1, 'C')
    # pdf.ln(10) # new line after 10 pts
    pdf.set_font('Arial', 'B', 10) 
    pdf.cell(100,10,'Datos Proyecto',0,1)
     
    
    pdf.set_font('Arial','',9)
    pdf.set_text_color (0,0,0)
    pdf.cell(ancho_celda1,alto_celda1,'Proyecto: ',0,0)
    pdf.cell(ancho_celda2, alto_celda1,str(a['proyecto']),0,0)
    pdf.cell(ancho_celda1,alto_celda1,'',0,0)
    pdf.cell(ancho_celda2, alto_celda1,'',0,0)
    pdf.ln(alto_celda1)
    pdf.cell(ancho_celda1,alto_celda1,'Diseñador: ',0,0)
    pdf.cell(ancho_celda2, alto_celda1,str(a['disenador']),0,0)
    pdf.cell(ancho_celda1,alto_celda1,' ',0,0)
    pdf.cell(ancho_celda2, alto_celda1,'',0,0)
    pdf.ln(alto_celda1)
    pdf.cell(ancho_celda1,alto_celda1,'Dirección: ',0,0)
    pdf.cell(ancho_celda2, alto_celda1,str(a['direccion']),0,0)
    pdf.cell(ancho_celda1,alto_celda1,'',0,0)
    pdf.cell(ancho_celda2, alto_celda1,'',0,0)
    pdf.ln(alto_celda1)
    pdf.cell(ancho_celda1,alto_celda1,'Telefono ',0,0)
    pdf.cell(ancho_celda2, alto_celda1,str(a['telefono']),0,0)
    pdf.cell(ancho_celda1,alto_celda1,' ',0,0)
    pdf.cell(ancho_celda2, alto_celda1,'',0,0)
    pdf.ln(alto_celda1)
    pdf.cell(ancho_celda1,alto_celda1,'Descripción ',0,0)
    pdf.cell(ancho_celda2, alto_celda1,'text3',0,0)
    pdf.cell(ancho_celda1,alto_celda1,' ',0,0)
    pdf.cell(ancho_celda2, alto_celda1,'',0,0)
    
 #   Línea de la mitad 
    pdf.ln(6)
    
    
    pdf.set_line_width(0.3)
    pdf.cell(ancho_celda1,0.3,'',1,0,'A')
    pdf.cell(ancho_celda2, 0.3,'',1,0,'A')
    pdf.cell(ancho_celda1,0.3,' ',1,0,'A')
    pdf.cell(ancho_celda2, 0.3,'',1,0,'A')
    pdf.ln(0.4)
    
    
#    set sínea de la mitad al tamaño normal
    pdf.set_line_width(0.1)
    
    
    pdf.set_font('Arial','',10)
    pdf.set_text_color (0,0,255)
    pdf.cell(ancho_celda1,alto_celda2,'Dimensiones de la estructura',0,0)
    pdf.cell(ancho_celda2,alto_celda2,'',0,0)
    
    pdf.cell(ancho_celda1,alto_celda2,'Influencia ambiental',0,0)
    pdf.cell(ancho_celda2,alto_celda2,'',0,0)
    pdf.ln(alto_celda2)
    pdf.set_font('Arial','',9)
    pdf.set_text_color (0,0,0)
    pdf.cell(ancho_celda1,alto_celda1,'Longitud de la estructura [m]: ',0,0)
    pdf.cell(ancho_celda2, alto_celda1,str(a['L']),0,0)
    pdf.cell(ancho_celda1,alto_celda1,'Situación respecto a los alrededores: ',0,0)
    pdf.cell(ancho_celda2, alto_celda1,str(a['Combobox4']),0,0)
    pdf.ln(alto_celda1)
    pdf.cell(ancho_celda1,alto_celda1,'Ancho de la estructura [m]: ',0,0)
    pdf.cell(ancho_celda2, alto_celda1,str(a['W']),0,0)
    pdf.cell(ancho_celda1,alto_celda1,'Factor ambiental: ',0,0)
    pdf.cell(ancho_celda2, alto_celda1,str(a['Combobox5']),0,0)
    pdf.ln(alto_celda1)
    pdf.cell(ancho_celda1,alto_celda1,'Altura de la estructura [m]: ',0,0)
    pdf.cell(ancho_celda2, alto_celda1,str(a['H']),0,0)
    pdf.cell(ancho_celda1,alto_celda1,'Densidad anual equivalente de rayos: ',0,0)
    pdf.cell(ancho_celda2, alto_celda1,str(a['DDT']),0,0)
    pdf.ln(alto_celda1)
    pdf.cell(ancho_celda1,alto_celda1,'Área total de la estructura [m]: ',0,0)
    pdf.cell(ancho_celda2, alto_celda1,str(a['A_d']),0,0)
    pdf.cell(ancho_celda1,alto_celda1,' ',0,0)
    pdf.cell(ancho_celda2, alto_celda1,'',0,0)
    pdf.ln(alto_celda1)
    
    pdf.set_font('Arial','',10)
    pdf.set_text_color (0,0,255)
    pdf.cell(ancho_celda1,alto_celda2,'Características de la estructura:',0,0)
    pdf.cell(ancho_celda2,alto_celda2,'',0,0)
    pdf.cell(ancho_celda1,alto_celda2,'Medidas de protección:',0,0)
    pdf.cell(ancho_celda2,alto_celda2,'',0,0)
    pdf.ln(alto_celda2)
    pdf.set_font('Arial','',9)
    pdf.set_text_color (0,0,0)
    pdf.cell(ancho_celda1,alto_celda1,'Riesgo de incendio y daños físicos: ',0,0)
    pdf.cell(ancho_celda2, alto_celda1,str(a['Combobox1']),0,0)
    pdf.cell(ancho_celda1,alto_celda1,'Clase de SPCR: ',0,0)
    pdf.cell(ancho_celda2, alto_celda1,str(a['Combobox9']),0,0)
    pdf.ln(alto_celda1)
    pdf.cell(ancho_celda1,alto_celda1,'Eficacia del apantallamiento: ',0,0)
    pdf.cell(ancho_celda2, alto_celda1,str(a['Combobox2']),0,0)
    pdf.cell(ancho_celda1,alto_celda1,'Protección contra incendios: ',0,0)
    pdf.cell(ancho_celda2, alto_celda1,str(a['Combobox10']),0,0)
    pdf.ln(alto_celda1)
    pdf.cell(ancho_celda1,alto_celda1,'Tipo de cableado interno: ',0,0)
    pdf.cell(ancho_celda2, alto_celda1,str(a['Combobox3']),0,0)
    pdf.cell(ancho_celda1,alto_celda1,
             'Protección contra sobretensiones: ',0,0)
    pdf.cell(ancho_celda2, alto_celda1,str(a['Combobox11']),0,0)
    pdf.ln(alto_celda1)
    pdf.cell(ancho_celda1,alto_celda1,'',0,0)
    pdf.cell(ancho_celda2, alto_celda1,'',0,0)
    pdf.cell(ancho_celda1,alto_celda1,' ',0,0)
    pdf.cell(ancho_celda2, alto_celda1,'',0,0)
    
    
    #Línea de la mitad 
    pdf.ln(6)
    
    
    pdf.set_line_width(0.3)
    pdf.cell(ancho_celda1,0.3,'',1,0,'A')
    pdf.cell(ancho_celda2, 0.3,'',1,0,'A')
    pdf.cell(ancho_celda1,0.3,' ',1,0,'A')
    pdf.cell(ancho_celda2, 0.3,'',1,0,'A')
    pdf.ln(0.4)
    
    # #set sínea de la mitad al tamaño normal
    # pdf.set_line_width(0.1)
    
    
    
    pdf.set_font('Arial', 'B', 10) 
    pdf.cell(100,5,'Líneas de conducción eléctrica:',0,1)
    pdf.set_font('Arial','',10)
    pdf.set_text_color (0,0,255)
    pdf.cell(ancho_celda1,alto_celda2,'Línea eléctrica:',0,0)
    pdf.cell(ancho_celda2,alto_celda2,'',0,0)
    pdf.cell(ancho_celda1,alto_celda2,'Otros servicios aéreos:',0,0)
    pdf.cell(ancho_celda2,alto_celda2,'',0,0)
    pdf.ln(alto_celda2)
    pdf.set_font('Arial','',9)
    pdf.set_text_color (0,0,0)
    pdf.cell(ancho_celda1,alto_celda1,'Línea que llega a la estructura: ',0,0)
    pdf.cell(ancho_celda2, alto_celda1,str(a['Combobox6']),0,0)
    pdf.cell(ancho_celda1, alto_celda1,'Número de servicios conducidos: ',0,0)
    pdf.cell(ancho_celda2, alto_celda1,str(a['Spinbox1']),0,0)
    pdf.ln(alto_celda1)
    pdf.cell(ancho_celda1, alto_celda1,'Tipo de cable externo: ',0,0)
    pdf.cell(ancho_celda2, alto_celda1,str(a['Combobox22']),0,0)
    pdf.cell(ancho_celda1, alto_celda1,'Tipo de cable externo: ',0,0)
    pdf.cell(ancho_celda2, alto_celda1,str(a['Combobox7']),0,0)
    pdf.ln(alto_celda1)
    pdf.cell(ancho_celda1, alto_celda1,'Existencia de transformador MT/BT: ',0,0)
    pdf.cell(ancho_celda2, alto_celda1,str(a['Combobox23']),0,0)
    pdf.ln(alto_celda1)
    
    pdf.set_font('Arial','',10)
    pdf.set_text_color (0,0,255)
    pdf.cell(ancho_celda1,alto_celda2,'',0,0)
    pdf.cell(ancho_celda2,alto_celda2,'',0,0)
    pdf.cell(ancho_celda1,alto_celda2,'Otros servicios enterrados:',0,0)
    pdf.cell(ancho_celda2,alto_celda2,'',0,0)
    pdf.ln(alto_celda2)
    pdf.set_font('Arial','',9)
    pdf.set_text_color (0,0,0)
    pdf.cell(ancho_celda1, alto_celda1,'',0,0)
    pdf.cell(ancho_celda2, alto_celda1,'',0,0)
    pdf.cell(ancho_celda1, alto_celda1,'Número de servicios conducidos: ',0,0)
    pdf.cell(ancho_celda2, alto_celda1,str(a['Spinbox2']),0,0)
    pdf.ln(alto_celda1)
    pdf.cell(ancho_celda1, alto_celda1,'',0,0)
    pdf.cell(ancho_celda2, alto_celda1,'',0,0)
    pdf.cell(ancho_celda1, alto_celda1,'Tipo de cable externo:  ',0,0)
    pdf.cell(ancho_celda2, alto_celda1,str(a['Combobox8']),0,0)
    
    pdf.ln(alto_celda1)
    pdf.cell(ancho_celda1,alto_celda1,'',0,0)
    pdf.cell(ancho_celda2, alto_celda1,'',0,0)
    pdf.cell(ancho_celda1,alto_celda1,' ',0,0)
    pdf.cell(ancho_celda2, alto_celda1,'',0,0)
    
    
    #Línea de la mitad 
    pdf.ln(6)
    
    
    pdf.set_line_width(0.3)
    pdf.cell(ancho_celda1,0.3,'',1,0,'A')
    pdf.cell(ancho_celda2, 0.3,'',1,0,'A')
    pdf.cell(ancho_celda1,0.3,' ',1,0,'A')
    pdf.cell(ancho_celda2, 0.3,'',1,0,'A')
    pdf.ln(0.4)
    
    
    # #set sínea de la mitad al tamaño normal
    # pdf.set_line_width(0.1)
    
    
    
    
    
    pdf.set_font('Arial', 'B', 10) 
    pdf.cell(100,5,'Tipos de las pérdidas:',0,1)
    pdf.set_font('Arial','',10)
    pdf.set_text_color (0,0,255)
    pdf.cell(ancho_celda1,alto_celda2,'Tipo 1 - Pérdidas de vidas humanas:',0,0)
    pdf.cell(ancho_celda2,alto_celda2,'',0,0)
    pdf.cell(ancho_celda1,alto_celda2,'Tipo 3 - Pérdidas de patrimonio cultural:',0,0)
    pdf.cell(ancho_celda2,alto_celda2,'',0,0)
    
    pdf.ln(alto_celda2)
    pdf.set_font('Arial','',9)
    pdf.set_text_color (0,0,0)
    pdf.cell(ancho_celda1,alto_celda1,'Riesgos especiales para la vida: ',0,0)
    pdf.cell(ancho_celda2, alto_celda1,str(a['Combobox12']),0,0)
    pdf.cell(ancho_celda1,alto_celda1,'Por incendios: ',0,0)
    pdf.cell(ancho_celda2, alto_celda1,str(a['Combobox15']),0,0)
    pdf.ln(alto_celda1)
    pdf.cell(ancho_celda1,alto_celda1,'Por incendios: ',0,0)
    pdf.cell(ancho_celda2, alto_celda1,str(a['Combobox13']),0,0)
    pdf.ln(alto_celda1)
    pdf.cell(ancho_celda1,alto_celda1,'Por sobretensiones:',0,0)
    pdf.cell(ancho_celda2, alto_celda1, str(a['Combobox14']),0,0)
    pdf.ln(alto_celda1)
    
    pdf.set_font('Arial','',10)
    pdf.set_text_color (0,0,255)
    pdf.cell(ancho_celda1,alto_celda2,'Tipo 2 - Pérdidas de servicios esenciales:',0,0)
    pdf.cell(ancho_celda2,alto_celda2,'',0,0)
    pdf.cell(ancho_celda1,alto_celda2,'Tipo 4 - Pérdidas económicas:',0,0)
    pdf.cell(ancho_celda2,alto_celda2,'',0,0)
    pdf.ln(alto_celda2)
    pdf.set_font('Arial','',9)
    pdf.set_text_color (0,0,0)
    pdf.cell(ancho_celda1,alto_celda1,'Por incendios: ',0,0)
    pdf.cell(ancho_celda2, alto_celda1,str(a['Combobox21']),0,0)
    pdf.cell(ancho_celda1,alto_celda1,'Riesgos económicos especiales: ',0,0)
    pdf.cell(ancho_celda2, alto_celda1,str(a['Combobox17']),0,0)
    pdf.ln(alto_celda1)
    pdf.cell(ancho_celda1,alto_celda1,'Por sobretensiones: ',0,0)
    pdf.cell(ancho_celda2, alto_celda1,str(a['Combobox22']),0,0)
    pdf.cell(ancho_celda1,alto_celda1,'Por incendios: ',0,0)
    pdf.cell(ancho_celda2, alto_celda1,str(a['Combobox18']),0,0)
    pdf.ln(alto_celda1)
    pdf.cell(ancho_celda1,alto_celda1,'',0,0)
    pdf.cell(ancho_celda2, alto_celda1,'',0,0)
    pdf.cell(ancho_celda1,alto_celda1,'Por sobretensiones ',0,0)
    pdf.cell(ancho_celda2, alto_celda1,str(a['Combobox19']),0,0)
    pdf.ln(alto_celda1)
    pdf.cell(ancho_celda1,alto_celda1,'',0,0)
    pdf.cell(ancho_celda2, alto_celda1,'',0,0)
    pdf.cell(ancho_celda1,alto_celda1,'Por tensión de paso/contacto ',0,0)
    pdf.cell(ancho_celda2, alto_celda1,str(a['Combobox20']),0,0)
    pdf.ln(alto_celda1)
    pdf.cell(ancho_celda1,alto_celda1,'',0,0)
    pdf.cell(ancho_celda2, alto_celda1,'',0,0)
    pdf.cell(ancho_celda1,alto_celda1,'Riesgo tolerable de pérd. económ.: ',0,0)
    pdf.cell(ancho_celda2, alto_celda1,str(a['Combobox24']),0,0)
    pdf.ln(alto_celda1)
    
    
    
    
    
    #Línea de la mitad 
    pdf.ln(6)
    
    
    pdf.set_line_width(0.3)
    pdf.cell(ancho_celda1,0.3,'',1,0,'A')
    pdf.cell(ancho_celda2, 0.3,'',1,0,'A')
    pdf.cell(ancho_celda1,0.3,' ',1,0,'A')
    pdf.cell(ancho_celda2, 0.3,'',1,0,'A')
    pdf.ln(0.4)
    
    
    # #set sínea de la mitad al tamaño normal
    # pdf.set_line_width(0.1)
    
    
    
    
    
    pdf.set_font('Arial', 'B', 10) 
    pdf.cell(100,5,'Riesgos calculados:',0,1)
    pdf.set_font('Arial','',10)
    pdf.set_text_color (0,0,255)
    pdf.cell(ancho_celda1,alto_celda2,'',0,0)
    pdf.cell(31.5,alto_celda2,'Riesgo Tolerable ',0,0,'C')
    pdf.cell(31.5,alto_celda2,'Impacto directo',0,0,'C')
    pdf.cell(31.5,alto_celda2,'Impacto indirecto',0,0,'C')
    pdf.cell(31.5,alto_celda2,'Riesgo calculado',0,0,'C')
    pdf.ln(alto_celda2)
    pdf.cell(ancho_celda1,alto_celda2,'',0,0)
    pdf.cell(31.5,alto_celda2,'Rt',0,0,'C')
    pdf.cell(31.5,alto_celda2,'Rd',0,0,'C')
    pdf.cell(31.5,alto_celda2,'Ri',0,0,'C')
    pdf.cell(31.5,alto_celda2,'R',0,0,'C')
    
    
    
    pdf.ln(alto_celda2)
    pdf.set_font('Arial','',9)
    pdf.set_text_color (0,0,0)
    pdf.cell(ancho_celda1,alto_celda1,'Pérdidas de vidas humanas: ',0,0)
    pdf.cell(31.5, alto_celda1,'1.00e-5',0,0,'C')
    pdf.cell(31.5,alto_celda1,str(a['R_d1']),0,0,'C')
    pdf.cell(31.5, alto_celda1,str(a['R_i1']),0,0,'C')
    pdf.cell(31.5, alto_celda1,str(a['R_1']),0,0,'C')
    
    pdf.ln(alto_celda1)
    pdf.cell(ancho_celda1,alto_celda1,'Pérdidas de serv. públicos: ',0,0)
    pdf.cell(31.5, alto_celda1,'1.00e-3',0,0,'C')
    pdf.cell(31.5,alto_celda1,str(a['R_d2']),0,0,'C')
    pdf.cell(31.5, alto_celda1,str(a['R_i2']),0,0,'C')
    pdf.cell(31.5, alto_celda1,str(a['R_2']),0,0,'C')
    pdf.ln(alto_celda1)
    pdf.cell(ancho_celda1,alto_celda1,'Pérdidas de patrimonio: ',0,0)
    pdf.cell(31.5, alto_celda1,'1.00e-3',0,0,'C')
    pdf.cell(31.5,alto_celda1,str(a['R_d3']),0,0,'C')
    pdf.cell(31.5, alto_celda1,str(a['R_d3']),0,0,'C')
    pdf.cell(31.5, alto_celda1,str(a['R_3']),0,0,'C')
    pdf.ln(alto_celda1)
    pdf.cell(ancho_celda1,alto_celda1,'Pérdidas económicas: ',0,0)
    pdf.cell(31.5, alto_celda1,'1.00e-3',0,0,'C')
    pdf.cell(31.5,alto_celda1,str(a['R_d4']),0,0,'C')
    pdf.cell(31.5, alto_celda1,str(a['R_d4']),0,0,'C')
    pdf.cell(31.5, alto_celda1,str(a['R_4']),0,0,'C')
    
    
    #Línea de la mitad 
    pdf.ln(12)

    
    pdf.set_line_width(0.3)
    pdf.cell(ancho_celda1,0.3,'',1,0,'A')
    pdf.cell(ancho_celda2, 0.3,'',1,0,'A')
    pdf.cell(ancho_celda1,0.3,' ',1,0,'A')
    pdf.cell(ancho_celda2, 0.3,'',1,0,'A')
    pdf.ln(0.4)
    
    
    # #set sínea de la mitad al tamaño normal
    # pdf.set_line_width(0.1)
    


        
    pdf.set_font('Arial', 'B', 10) 
    pdf.cell(180,5,'POTTER VERSION 0.0.8',0,1)
    pdf.set_font('Arial', '', 9)
    pdf.set_text_color (255,0,0)
    pdf.cell(180,5,'Este cálculo de riesgo según NTC pretende orientar en el análisis de diversos criterios que determinan el riesgo de ',0,1)
    pdf.cell(180,5,'pérdidas debidas al rayo. No es posible cubrir todos los elementos especiales de una estructura que puedan hacer que',0,1)
    pdf.cell(180,5,'sufra más o menos daños debido al rayo. En casos especiales hay factores económicos y personales que podrían ser',0,1)
    pdf.cell(180,5,'muy importantes y considerarse junto con el indice obtenido mediante esta herramienta. Se pretende que este programa',0,1)
    pdf.cell(180,5,'se utilice en conbinación con la versión escrita de la norma NTC-4552-2 ',0,1)
    
    pdf.ln(12)
    
    # Crea una línea
    # pdf.set_line_width(1)
    # pdf.dashed_line(20, 40, 110, 40, 1, 10)


# =============================================================================
# Añade una nueva página
# =============================================================================
    pdf.add_page()
 
    
 
    pdf.set_font('Arial', 'B', 16)    
    #pdf.set_draw_color(r=255, g=255, b=255)
    
    pdf.cell(190, 10, 'CÁLCULO DEL RIESGO SEGÚN NTC 4552-2', 1, 1, 'C')
    # pdf.ln(10) # new line after 10 pts
    ancho_celda3 = 163
    alto_celda3 = 4
    ancho_celda4 = 27
    ancho_celda5 = 150

    pdf.ln(alto_celda3)
    pdf.set_text_color (0,0,0)
# =============================================================================
# Tipo 4 - Pérdidas económicas:
# =============================================================================
# pdf.ln(10) # new line after 10 pts
    pdf.set_font('Arial', 'B', 10) 
    pdf.cell(100,10,'Resultados del área de colección:',0,1)
# =============================================================================
# termina título
# =============================================================================
    pdf.set_font('Arial','',7.5)
    pdf.cell(ancho_celda5,alto_celda3,'Ad - Área de colección de impactos directos a la estructura',0,0)
    pdf.cell(ancho_celda4, alto_celda3,str(a['A_d'])+' m2',0,0)


 #  salto línea 
    pdf.ln(alto_celda3)
    pdf.cell(ancho_celda5,alto_celda3,'Nd - número medio de impactos directos a la estructura por año',0,0)
    pdf.cell(ancho_celda4, alto_celda3,str(a['N_D'])+' flashes/year',0,0)

    pdf.ln(alto_celda3)
    pdf.cell(ancho_celda4, alto_celda3,'',0,0)  


 #  salto línea 
    pdf.ln(alto_celda3)
    pdf.cell(ancho_celda5,alto_celda3,'Am - Área de colección de la estructura afectada por sobretensiones inducidas por impactos indirectos.',0,0)
    pdf.cell(ancho_celda4, alto_celda3,str(a['A_m'])+' m2',0,0)


 #  salto línea 
    pdf.ln(alto_celda3)
    pdf.cell(ancho_celda5,alto_celda3,'Nm - núm. de impactos directos a tierra o a objetos cercanos a la estructura conectados a tierra que inducen sobretensiones',0,0)
    pdf.cell(ancho_celda4, alto_celda3,str(a['N_M'])+' flashes/year',0,0)
    pdf.ln(alto_celda3)
    pdf.cell(ancho_celda4, alto_celda3,'',0,0)



 #  salto línea 
    pdf.ln(alto_celda3)
    pdf.cell(ancho_celda5,alto_celda3,'Ac1 - área de colección de las líneas aéreas a impactos directos.',0,0)
    pdf.cell(ancho_celda4, alto_celda3,str(a['A_c1'])+' m2',0,0)


 #  salto línea 
    pdf.ln(alto_celda3)
    pdf.cell(ancho_celda5,alto_celda3,'NL1 - número medio de impactos directos por año a las líneas aéreas que sean potencialmente peligrosos',0,0)
    pdf.cell(ancho_celda4, alto_celda3,str(a['N_L1'])+' flashes/year',0,0)
    pdf.ln(alto_celda3)
    pdf.cell(ancho_celda4, alto_celda3,'',0,0)
 


 #  salto línea 
    pdf.ln(alto_celda3)
    pdf.cell(ancho_celda5,alto_celda3,'Ac2 - área de colección de la línea enterrada a impactos directos',0,0)
    pdf.cell(ancho_celda4, alto_celda3,str(a['A_c2'])+' m2',0,0)


 #  salto línea 
    pdf.ln(alto_celda3)
    pdf.cell(ancho_celda5,alto_celda3,'NL2- número esperado de impactos directos anuales a la línea enterrada que sean potencialmente peligrosos',0,0)
    pdf.cell(ancho_celda4, alto_celda3,str(a['N_L2'])+' flashes/year',0,0)
    pdf.ln(alto_celda3)
    pdf.cell(ancho_celda4, alto_celda3,'',0,0)   
 


 #  salto línea 
    pdf.ln(alto_celda3)
    pdf.cell(ancho_celda5,alto_celda3,'AI2 - área de colección de la línea enterrada a impactos indirectos.',0,0)
    pdf.cell(ancho_celda4, alto_celda3,str(a['A_l2'])+' m2',0,0)


 #  salto línea 
    pdf.ln(alto_celda3)
    pdf.cell(ancho_celda5,alto_celda3,'NI2 - número de impactos indirectos anuales a la tierra cercana a la línea enterrada que induzcan sobretensiones peligrosas',0,0)
    pdf.cell(ancho_celda4, alto_celda3,str(a['N_I2'])+' flashes/year',0,0)


    #Línea de la mitad 
    pdf.ln(8)

    
    pdf.set_line_width(0.3)
    pdf.cell(ancho_celda1,0.3,'',1,0,'A')
    pdf.cell(ancho_celda2, 0.3,'',1,0,'A')
    pdf.cell(ancho_celda1,0.3,' ',1,0,'A')
    pdf.cell(ancho_celda2, 0.3,'',1,0,'A')
    pdf.ln(1)   
    
    
# =============================================================================
#     
# =============================================================================

    pdf.set_font('Arial', 'B', 10) 
    pdf.cell(100,4,'Tipo 1 - Pérdidas de vidas humanas',0,1)


    pdf.set_font('Arial','',7.5)
    pdf.cell(ancho_celda3,alto_celda3,'RA1 - riesgo de tensiones de paso y contacto peligrosas dentro y fuera de la estructura causadas por un impacto directo a la estructura: ',0,0)
    pdf.cell(ancho_celda4, alto_celda3,str(a['R_A1']),0,0)
    
 #  salto línea  
    pdf.ln(alto_celda3)
    pdf.cell(ancho_celda3,alto_celda3,'RB1 - riesgo de destrucción debida a incendio, explosión, daños físicos o daños químicos causados por un impacto directo a la estructura',0,0)
    pdf.cell(ancho_celda4, alto_celda3,str(a['R_B1']),0,0)

 #  salto línea 
    pdf.ln(alto_celda3)
    pdf.cell(ancho_celda3,alto_celda3,'RC1 - riesgo de fallo de equipos eléctricos o electrónicos debido a sobretensiones causadas por un impacto directo a la estructura.',0,0)
    pdf.cell(ancho_celda4, alto_celda3,str(a['R_C1']),0,0)

 #  salto línea 
    pdf.ln(alto_celda3)
    pdf.cell(ancho_celda3,alto_celda3,'RM1 - riesgo de fallo de equipos eléctricos o electrónicos debido a sobretensiones causadas por un impacto indirecto a la estructura.',0,0)
    pdf.cell(ancho_celda4, alto_celda3,str(a['R_M1']),0,0)

 #  salto línea 
    pdf.ln(alto_celda3)
    pdf.cell(ancho_celda3,alto_celda3,'RU1 - riesgo de tensiones de paso y contacto peligrosas dentro y fuera de la estructura causadas por un impacto directo a las líneas.',0,0)
    pdf.cell(ancho_celda4, alto_celda3,str(a['R_U1']),0,0)

 #  salto línea 
    pdf.ln(alto_celda3)
    pdf.cell(ancho_celda3,alto_celda3,'RV1 - riesgo de destrucción debida a incendio, explosión, daños físicos o daños químicos causados por un impacto directo a las líneas.',0,0)
    pdf.cell(ancho_celda4, alto_celda3,str(a['R_V1']),0,0)

 #  salto línea 
    pdf.ln(alto_celda3)
    pdf.cell(ancho_celda3,alto_celda3,'RW1 - riesgo de fallo de equipos eléctricos o electrónicos debido a sobretensiones causadas por un impacto directo a las líneas.',0,0)
    pdf.cell(ancho_celda4, alto_celda3,str(a['R_W1']),0,0)

 #  salto línea 
    pdf.ln(alto_celda3)
    pdf.cell(ancho_celda3,alto_celda3,'RZ1 - riesgo de fallo de equipos eléctricos o electrónicos debido a sobretensiones causadas por un impacto indirecto a las líneas.',0,0)
    pdf.cell(ancho_celda4, alto_celda3,str(a['R_Z1']),0,0)
  
  #  salto línea 
    pdf.ln(alto_celda3)  
# =============================================================================
# Tipo 2 - Pérdidas de servicios esenciales:
# =============================================================================
# pdf.ln(10) # new line after 10 pts
    pdf.set_font('Arial', 'B', 10) 
    pdf.cell(100,10,'Tipo 2 - Pérdidas de servicios esenciales:',0,1)


# =============================================================================
# termina título
# =============================================================================
    pdf.set_font('Arial','',7.5)
    pdf.set_text_color (0,0,0)
    pdf.cell(ancho_celda3,alto_celda3,'RB2 - riesgo de destrucción debida a incendio, explosión, daños físicos o daños químicos causados por un impacto directo a la estructura.',0,0)
    pdf.cell(ancho_celda4, alto_celda3,str(a['R_B2']),0,0)

 #  salto línea 
    pdf.ln(alto_celda3)

    pdf.set_text_color (0,0,0)
    pdf.cell(ancho_celda3,alto_celda3,'RC2 - riesgo de fallo de equipos eléctricos o electrónicos debido a sobretensiones causadas por un impacto directo a la estructura.',0,0)
    pdf.cell(ancho_celda4, alto_celda3,str(a['R_C2']),0,0)

 #  salto línea 
    pdf.ln(alto_celda3)
    pdf.cell(ancho_celda3,alto_celda3,'RM2 - riesgo de fallo de equipos eléctricos o electrónicos debido a sobretensiones causadas por un impacto indirecto a la estructura.',0,0)
    pdf.cell(ancho_celda4, alto_celda3,str(a['R_M2']),0,0)

 #  salto línea 
    pdf.ln(alto_celda3)

    pdf.set_text_color (0,0,0)
    pdf.cell(ancho_celda3,alto_celda3,'RV2 - riesgo de destrucción debida a incendio, explosión, daños físicos o daños químicos causados por un impacto directo a las líneas.',0,0)
    pdf.cell(ancho_celda4, alto_celda3,str(a['R_V2']),0,0)

 #  salto línea 
    pdf.ln(alto_celda3)
    pdf.cell(ancho_celda3,alto_celda3,'RW2 - riesgo de fallo de equipos eléctricos o electrónicos debido a sobretensiones causadas por un impacto directo a las líneas.',0,0)
    pdf.cell(ancho_celda4, alto_celda3,str(a['R_W2']),0,0)

 #  salto línea 
    pdf.ln(alto_celda3)

    pdf.set_text_color (0,0,0)
    pdf.cell(ancho_celda3,alto_celda3,'RZ2 - riesgo de fallo de equipos eléctricos o electrónicos debido a sobretensiones causadas por un impacto indirecto a las líneas.',0,0)
    pdf.cell(ancho_celda4, alto_celda3,str(a['R_Z2']),0,0)

  #  salto línea 
    pdf.ln(alto_celda3)  

# =============================================================================
# Tipo 3 - Pérdidas de patrimonio cultural:
# =============================================================================
# pdf.ln(10) # new line after 10 pts
    pdf.set_font('Arial', 'B', 10) 
    pdf.cell(100,10,'Tipo 3 - Pérdidas de patrimonio cultural:',0,1)
# =============================================================================
# termina título
# =============================================================================
    pdf.set_font('Arial','',7.5)
    pdf.set_text_color (0,0,0)

    pdf.cell(ancho_celda3,alto_celda3,'RB3 - riesgo de destrucción debida a incendio, explosión, daños físicos o daños químicos causados por un impacto directo a la estructura',0,0)
    pdf.cell(ancho_celda4, alto_celda3,str(a['R_B3']),0,0)

 #  salto línea 
    pdf.ln(alto_celda3)
    pdf.cell(ancho_celda3,alto_celda3,'RV3 - riesgo de destrucción debida a incendio, explosión, daños físicos o daños químicos causados por un impacto directo a las líneas.',0,0)
    pdf.cell(ancho_celda4, alto_celda3,str(a['R_V3']),0,0)

  #  salto línea 
    pdf.ln(alto_celda3)  
# =============================================================================
# Tipo 4 - Pérdidas económicas:
# =============================================================================
# pdf.ln(10) # new line after 10 pts
    pdf.set_font('Arial', 'B', 10) 
    pdf.cell(100,10,'Tipo 4 - Pérdidas económicas:',0,1)
# =============================================================================
# termina título
# =============================================================================
    pdf.set_font('Arial','',7.5)
    pdf.set_text_color (0,0,0)

    pdf.cell(ancho_celda3,alto_celda3,'RA4 - riesgo de tensiones de paso y contacto peligrosas dentro y fuera de la estructura causadas por un impacto directo a la estructura.',0,0)
    pdf.cell(ancho_celda4, alto_celda3,str(a['R_A4']),0,0)

 #  salto línea 
    pdf.ln(alto_celda3)
    pdf.cell(ancho_celda3,alto_celda3,'RB4 - riesgo de destrucción debida a incendio, explosión, daños físicos o daños químicos causados por un impacto directo a la estructura.',0,0)
    pdf.cell(ancho_celda4, alto_celda3,str(a['R_B4']),0,0)

 #  salto línea 
    pdf.ln(alto_celda3)
    pdf.cell(ancho_celda3,alto_celda3,'RC4 - riesgo de fallo de equipos eléctricos o electrónicos debido a sobretensiones causadas por un impacto directo a la estructura.',0,0)
    pdf.cell(ancho_celda4, alto_celda3,str(a['R_C4']),0,0)

 #  salto línea 
    pdf.ln(alto_celda3)
    pdf.cell(ancho_celda3,alto_celda3,'RM4 - riesgo de fallo de equipos eléctricos o electrónicos debido a sobretensiones causadas por un impacto indirecto a la estructura.',0,0)
    pdf.cell(ancho_celda4, alto_celda3,str(a['R_M4']),0,0)

 #  salto línea 
    pdf.ln(alto_celda3)
    pdf.cell(ancho_celda3,alto_celda3,'RU4 - riesgo de tensiones de paso y contacto peligrosas dentro y fuera de la estructura causadas por un impacto directo a las líneas.',0,0)
    pdf.cell(ancho_celda4, alto_celda3,str(a['R_U4']),0,0)

 #  salto línea 
    pdf.ln(alto_celda3)
    pdf.cell(ancho_celda3,alto_celda3,'RV4 - riesgo de destrucción debida a incendio, explosión, daños físicos o daños químicos causados por un impacto directo a las líneas.',0,0)
    pdf.cell(ancho_celda4, alto_celda3,str(a['R_V4']),0,0)

 #  salto línea 
    pdf.ln(alto_celda3)
    pdf.cell(ancho_celda3,alto_celda3,'RW4 - riesgo de fallo de equipos eléctricos o electrónicos debido a sobretensiones causadas por un impacto directo a las líneas.',0,0)
    pdf.cell(ancho_celda4, alto_celda3,str(a['R_W4']),0,0)

 #  salto línea 
    pdf.ln(alto_celda3)
    pdf.cell(ancho_celda3,alto_celda3,'RZ4 - riesgo de fallo de equipos eléctricos o electrónicos debido a sobretensiones causadas por un impacto indirecto a las líneas.',0,0)
    pdf.cell(ancho_celda4, alto_celda3,str(a['R_Z4']),0,0)


    #Línea de la mitad 
    pdf.ln(8)

    
    pdf.set_line_width(0.3)
    pdf.cell(ancho_celda1,0.3,'',1,0,'A')
    pdf.cell(ancho_celda2, 0.3,'',1,0,'A')
    pdf.cell(ancho_celda1,0.3,' ',1,0,'A')
    pdf.cell(ancho_celda2, 0.3,'',1,0,'A')
    pdf.ln(1)   
    
    
# =============================================================================
#     
# =============================================================================

    pdf.set_font('Arial', 'B', 10)  
    pdf.cell(180,5,'POTTER VERSION 0.0.8',0,1)
    pdf.set_font('Arial', '', 9)
    pdf.set_text_color (255,0,0)
    pdf.cell(180,5,'Este cálculo de riesgo según NTC pretende orientar en el análisis de diversos criterios que determinan el riesgo de ',0,1)
    pdf.cell(180,5,'pérdidas debidas al rayo. No es posible cubrir todos los elementos especiales de una estructura que puedan hacer que',0,1)
    pdf.cell(180,5,'sufra más o menos daños debido al rayo. En casos especiales hay factores económicos y personales que podrían ser',0,1)
    pdf.cell(180,5,'muy importantes y considerarse junto con el indice obtenido mediante esta herramienta. Se pretende que este programa',0,1)
    pdf.cell(180,5,'se utilice en conbinación con la versión escrita de la norma NTC-4552-2 ',0,1)
    
    pdf.ln(12)








    # pdf.ln(10)
    # pdf.set_line_width(0.5)
    # pdf.set_draw_color(r=255, g=128, b=0)
    # pdf.line(x1=50, y1=50, x2=150, y2=50)
    
    # pdf.ln(10)
    # pdf.cell(20,10,'image 1',0,0)
    # pdf.cell(20,10,'image 2',0,0)
    # pdf.cell(20,10,'image 3',0,0)
    
    # pdf.image("butterfly.JPG", 10, 130,40,40,'JPG')
    # pdf.image("butterfly.JPG", 70, 130,40,40,'JPG')
    # pdf.image("butterfly.JPG", 130, 130,40,40,'JPG')
    
    pdf.output('Informe Riesgo.pdf', 'F')
