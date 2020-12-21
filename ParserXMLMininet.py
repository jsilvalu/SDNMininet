#!/usr/bin/python
# coding=utf-8

from xml.dom import minidom
import urllib
import requests
import xml.etree.cElementTree as ET
import numpy as np
import os
import sys


#URL desde la que queremos importar el archivo XML que define la red
URL='http://sndlib.zib.de/coredata.download.action?objectName=abilene&format=xml&objectType=network'
#Nombre del archivo XML que se generará (No hace falta modificar)
archivoXML = 'XMLSDNlib.xml'
#Nombre de la topologia que será creada
nombreArchivoDestino='SDNlibTopology.py'

#Listas que almacenan todos los hosts como índice para generar la matriz de tráfico
listaHosts=[]


class text:
    createSwitch="info(colors.YELLOW + '[!] Creando los switches ...\n' + colors.ENDC)"
    createHost="info(colors.YELLOW + '[!] Creando los hosts ...\n'+colors.ENDC)"
    createLinks="info(colors.YELLOW + '[!] Creando enlaces ...\n'+colors.ENDC)"




def matriz_trafico1(XML, first_demand, last_demand):


    #Preparo el parser de XML a python para comezar el parsing
    doc = minidom.parse(XML)

    #Lectura de la matriz de tráfico
    itemlist = doc.getElementsByTagName('demand')  
    print("[!] Se han detectado "+ str(len(itemlist))+" demandas de tráfico.")
    matriz=np.zeros((len(listaHosts),len(listaHosts)))



    for s in itemlist:
        
        fila = listaHosts.index(s.getElementsByTagName("source")[0].firstChild.nodeValue)
        colm = listaHosts.index(s.getElementsByTagName("target")[0].firstChild.nodeValue)
        matriz[fila][colm]=s.getElementsByTagName("demandValue")[0].firstChild.nodeValue

    #Formateo los valores de demanda a enteros
    matriz=matriz.astype(int)

    writter_mode = "w+" if first_demand==True else "a"

    with open("config.JSON", mode="r") as flujoLectura, open ("configCustom.JSON", mode=writter_mode) as flujoEscritura:
        
        if first_demand:
            for linea in flujoLectura:
                flujoEscritura.write(linea)
                if '"TRAFFIC":' in linea:
                    break

        flujoEscritura.write("    [\n        ")    #Doy el formato de JSON para especificar el inicio de la matriz

        
        for k in matriz:  
            cont=0                        #Recorro la matriz
            flujoEscritura.write("[")
            for j in k:
                cont+=1
                if cont < len(listaHosts):
                    flujoEscritura.write(str(j)+",")    #Inserto la demanda con la ',' como separador
                else:
                    flujoEscritura.write(str(j))
            
            flujoEscritura.seek(-1, os.SEEK_END)       #Elimino los 10 últimos caracteres (última coma+formateo JSON)
            flujoEscritura.write("],\n        ")
        
        flujoEscritura.seek(-11, os.SEEK_END)       #Elimino los 10 últimos caracteres (última coma+formateo JSON)

        if last_demand:
            flujoEscritura.write("]\n")
        else:
            flujoEscritura.write("],\n")

        if last_demand:
            flujoEscritura.write("    ]\n}")




if __name__ == '__main__':


    with open("5h2s.py", mode="r") as flujoLectura, open (nombreArchivoDestino, mode="w") as flujoEscritura:
        for linea in flujoLectura:
            flujoEscritura.write(linea)
            if '#START_TOPO\n' in linea:
                break

        #Descargo el archivo XML desde la direccion de SDNlib en la carpeta actual para tratarlo
        response = requests.get(URL)
        with open(archivoXML, 'wb') as file:
            file.write(response.content)

        #Preparo el parser de XML a python para comezar el parsing
        doc = minidom.parse(archivoXML)

        #Preparo el campo que voy a recorrer, primero los hosts y los switch
        itemlist = doc.getElementsByTagName('node')
        print("[!] Se han detectado "+ str(len(itemlist))+" hosts en la red.")
        cont=0
        for s in itemlist:
         
            
            #Parsing de los switches del XML
            flujoEscritura.write("    s"+str(cont)+" = net.addSwitch('s"+str(cont)+"', ovsbr=OVSBridge,stp=True)   #Añado en switch "+str(cont)+", el host "+str(cont)+" y añado a las listas\n")
            #Parsing de los hosts del XML
            flujoEscritura.write("    h"+str(cont)+" = net.addHost('h"+str(cont)+"', cls=Host, mac='00:00:00:00:00:"+str(cont)+"',ip='10.0.0."+str(cont)+"/24', defaultRoute=None)\n")
            listaHosts.append(s.attributes['id'].value)

            flujoEscritura.write("    listaSwitches.append(s"+str(cont)+")\n")
            flujoEscritura.write("    listaHosts.append(h"+str(cont)+")\n")
            flujoEscritura.write("    listaNodos.append(s"+str(cont)+")\n")
            flujoEscritura.write("    listaNodos.append(h"+str(cont)+")\n\n")
            cont+=1  #Contador para asignar los nombres de los switches s1, s2, s3.... y insertar en las listas

        #Modificación del itemList para leer los enlaces
        itemlist = doc.getElementsByTagName('link')       
        print("[!] Se han detectado "+ str(len(itemlist))+" enlaces en la red.")
  
        cont=0
        for s in itemlist:
            
            sourceIndex = listaHosts.index(s.getElementsByTagName("source")[0].firstChild.nodeValue)
            targetIndex = listaHosts.index(s.getElementsByTagName("target")[0].firstChild.nodeValue)
            capacity = s.getElementsByTagName("capacity")[0].firstChild.nodeValue
            if capacity > 1000:
                capacity=float(capacity)/10
            flujoEscritura.write("\n    l"+str(cont)+"="+"net.addLink(s"+str(sourceIndex)+" , s"+str(targetIndex)+",ID = "+str(cont)+", bw = "+str(capacity)+", cls=TCLink)   #Añado enlace "+str(cont)+" y lo añado a las listas\n")
            flujoEscritura.write("    listaEnlaces.append(l"+str(cont)+")\n")
            flujoEscritura.write("    listabw.append("+str(capacity)+")\n")
            #flujoEscritura.write("    l"+str(cont)+".intf1.config(loss=0)\n")
            cont+=1

        #Conectatamos cada host con su switch
        flujoEscritura.write("    #Conexión de cada host con su switch, adición en la listaEnlaces y listabw para el procesado final\n")
        for h in range(0, len(listaHosts)):
            flujoEscritura.write("\n    l"+str(cont+h)+"="+"net.addLink(h"+str(listaHosts.index(listaHosts[h]))+" , s"+str(h)+",ID = "+str(cont+h)+", cls=TCLink)   #Añado enlace "+str(cont+h)+" y lo añado a las listas\n")
            flujoEscritura.write("    listaEnlaces.append(l"+str(cont+h)+")\n")
            flujoEscritura.write("    listabw.append("+str(1000)+")\n")
        #Escritura del resto del fichero genérico, se usa la bandera endtopo para detectar cuando se ha llegado a dicho punto del fichero
        endtopo=False
        for linea in flujoLectura:
            if '#END_TOPO\n' in linea:
                endtopo=True
            if endtopo:
                flujoEscritura.write(linea)



        #Generacion de las matrices de trafico
        matriz_trafico1(archivoXML, True, False)
        matriz_trafico1("./MatricesTrafico/00:00.xml", False, False)
        matriz_trafico1("./MatricesTrafico/00:05.xml", False, False)
        matriz_trafico1("./MatricesTrafico/00:10.xml", False, False)
        matriz_trafico1("./MatricesTrafico/00:20.xml", False, True)
    
    
