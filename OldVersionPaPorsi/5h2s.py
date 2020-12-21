#!/usr/bin/python
# coding=utf-8
from mininet.net import Mininet
from mininet.node import Controller, RemoteController, OVSController
from mininet.node import CPULimitedHost, Host, Node
from mininet.node import OVSKernelSwitch, UserSwitch, OVSBridge
from mininet.node import IVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink, Intf
from subprocess import call
from mininet.util import quietRun
from collections import defaultdict
from petl import fromcsv, look, cut, tocsv
import networkx as nx
import csv, operator
import json
import numpy as np
from time import sleep
import time
import datetime
import sys
import os
import random
import pandas as pd


#Listas que almacenan todos los hosts y switches de la topología customizada
listaHosts=[]
listaSwitches=[]
listaNodos=[]

listaEnlaces=[]
listabw=[]

#Variables globales relacionadas con los tiempos de ejecución
tiempo_ejecucion=20
intervalo_extraccion=1
intervalo_iperf_cliente=1
intervalo_iperf_servidor=1
duracion_iperf_cliente=20

#Variables globales relacionadas con la ejecución de iperf
protocol="-u"
port=5201

#Bandera ejecutadora de ping, si es TRUE se ejecutará la recolección de estadísticas de ping
ping=False

#Enlace aleatorio que sera modificado
link_withLoss=int(random.uniform(1,27))
assignedLoss=25

#Momento en el que se anulara el enlace
linkDeathTime=50

#Generación y acceso a la matriz de tráfico para iperf
class other:
    matriz=np.zeros((5,5))



#class colors: Controlo el color o formato de la salida por pantalla durante la ejecución
class colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    YELLOW = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    CYAN = '\033[96m'
    PURPLE = '\033[35m'

#class text: Clase contenedora de mensajes que se insertarán en algunos ficheros
class text:
    estado_puertos=          " ESTADO DE PUERTOS Y CAPACIDAD:\n =================================\n"
    estadisticas_puertos="\n\n ESTADISTICAS DE LOS PUERTOS:\n ===================================\n"
    entradas_flujo=      "\n\n ENTRADAS DE FLUJO:\n =============================================\n"
    flujos_agregados=    "\n\n ESTADISTICAS DE LOS flujos agregados:\n ==========================\n"


#class comand: Comandos en tipo string que serán lanzados en diferentes funciones por cmd
class command:

    tuberia_agraggateFlow=''' | awk '{print $4","$5","$6}' '''

    tuberia_dump_flow=''' | grep priority=65535,icmp | awk -F",|actions=output:" '{print $2","$4","$5","$6","$8","$9","$11","$15","$16","$20}' '''

    tuberia_dump_flowsrc=''' | grep priority=65535,icmp | awk -F",|actions=output:" '{print $15}' '''
    tuberia_dump_flowdst=''' | grep priority=65535,icmp | awk -F",|actions=output:" '{print $16}' '''
    tuberia_dump_flowaction=''' | grep priority=65535,icmp | awk -F",|actions=output:" '{print $20}' '''

    tuberia_tx=''' | grep tx | awk '{print $2 $3 $4 $5}' '''
    tuberia_rx=''' | grep rx | awk '{print $4 $5 $6 $7}' '''

    tuberia_ping=''' | grep packets | awk '{print $1","$4","$6","$10}' '''

    get_openFlow_Stats="sudo mv /home/idi/pox/stats_openflow.csv /home/idi/mininet/custom"
    get_openFlow_Delay="sudo mv /home/idi/pox/stats_delay_openflow.csv /home/idi/mininet/custom"


#class field: Cabeceras de información de los archivos csv
class field:
    estadisticas_flujo="duration(s), n_packets, n_bytes, idle_timeout, idle_age, priority,in_port,nw_src,nw_dst,action\n"
    flujo_agregado="duration(s),swtich,packet_count,byte_count,flow_count\n"
    port_stats="duration(s),tx_rx, port, swtich, pkts, bytes, drop,errs\n"
    ping_stats='duration(s),IPsrc, IPdst, transmitted, received, loss(%), time(s)\n'
    iperf_stats="date, IPclient, PORTclient, IPserver, PORTserver, nproccess, interval, transferred_bytes, bits/s\n"
    iperf_stats_servers="date, IPclient, PORTclient, IPserver, PORTserver, nproccess, interval, transferred_bytes, bits/s, jitter(ms), loss_datag, send_datag, loss, received_out_of_service\n"
    link_stats="date,%assignLoss,linkDeathTime,idLink,%loss,linkCharge\n"


"""
configJSON

Extrae la información del fichero JSON y lo asocia a las variables globales para le ejecución
"""
def configJSON():

    with open('configCustom.JSON') as JSON:

        #Extraigo los datos del fichero JSON en data
        data = json.load(JSON)


        #Extraigo configuración de tiempos del fichero JSON
        global tiempo_ejecucion
        tiempo_ejecucion = data["TIME"]['tiempo_ejecucion']
        global intervalo_extraccion
        intervalo_extraccion = data["TIME"]['intervalo_extraccion']
        global intervalo_iperf_cliente
        intervalo_iperf_cliente = data["TIME"]['intervalo_iperf_cliente']
        global intervalo_iperf_servidor
        intervalo_iperf_servidor = data["TIME"]['intervalo_iperf_servidor']
        global duracion_iperf_cliente
        duracion_iperf_cliente = data["TIME"]['duracion_iperf_cliente']
        #Extraigo configuración de iperf del fichero JSON
        global protocol
        protocol=data["IPERF"]['protocol']
        global port
        port=data["IPERF"]['port']
        #Extraigo bandera de ejecución de ping del fichero JSON
        global ping
        ping=data["PING"]['ejecutar_ping']

        print("\n")
        print(colors.BOLD+"*********************** Configuración de ejecución *************************************")
        print("[!] Ejecutando red durante  "+str(tiempo_ejecucion)+" segundos en intervalos de "+str(intervalo_extraccion)+" segundos")
        print("    · Intervalo clientes:   "+str(intervalo_iperf_cliente))
        print("    · Tiempo cliente:       "+str(duracion_iperf_cliente))
        print("    · Intervalo servidores: "+str(intervalo_iperf_servidor))
        print("    · Protocolo iperf:      "+str(protocol))
        print("    · Puerto iperf   :      "+str(port))
        print("    · Ping:                 "+str(ping))
        print("****************************************************************************************\n"+colors.ENDC)

        #Accedo al campo TRAFFIC del fichero JSON
        other.matriz=data['TRAFFIC']

        info(colors.BOLD+"[!] Matriz de tráfico extraída de config.JSON correctamente: \n"+colors.ENDC)

        for i in range(len(other.matriz)):
            for j in range(len(other.matriz[i])):
                info(" "+str(other.matriz[i][j])+"   ")
            info("\n")

    info("\n")



"""
volcado_estadisticas_puertos

Realiza una conexion a los swtiches openFlow para descargar el estado completo de sus puertos y capacidades
mediante ovs-ofctl show, despues obtiene las estadisticas de los puertoss asociados a los switches openFlow
ejecutando la instruccion ovs-ofctl dump-ports. El resultado de ambos mandatos se vuelvan en los ficheros de
texto correspondientes.
"""
def volcado_estadisticas_puertos(firs_time, start_time):

    info(colors.BOLD+'\n========================= Extraccion de estadisticas de los switches =================================\n\n'+colors.ENDC)
    writter_mode = "w+" if firs_time==True else "a"

    # Imprimimos las estadisticas de los puertos asociados a los switches openFlow
    with open("stats_ports.csv", mode=writter_mode) as fichero_stats_ports:

        if firs_time:
            fichero_stats_ports.write(field.port_stats) #Escribimos cabeceras de los campos

        #Extraigo estadisticas de los puertos recorriendo cada uno de ellos en cada swtich
        info(colors.OKBLUE +'[!] Capturando estadisticas de los puertos en stats_ports.csv ...\n'+colors.ENDC)

        for swtich in range(0, len(listaSwitches)):

            for port in range(0, len(listaSwitches[swtich].intfList())):

                #Procesamiento de estadísticas de TRANSMITIDOS TX
                string = listaSwitches[swtich].cmd("sudo ovs-ofctl dump-ports "+str(listaSwitches[swtich])+" "+str(port)+command.tuberia_tx)

                if string != "":
                    fichero_stats_ports.write(str(round(time.time()-start_time,3))+",TX,"+str(port)+","+str(listaSwitches[swtich])+",")
                    fichero_stats_ports.write(string.replace("pkts=","").replace("bytes=","").replace("drop=","").replace("errs=",""))

                #Procesamiento de estadísticas de RECIBIDOS RX
                string = listaSwitches[swtich].cmd("sudo ovs-ofctl dump-ports "+str(listaSwitches[swtich])+" "+str(port)+command.tuberia_rx)

                if string != "":
                    fichero_stats_ports.write(str(round(time.time()-start_time,3))+",RX,"+str(port)+","+str(listaSwitches[swtich])+",")
                    fichero_stats_ports.write(string.replace("pkts=","").replace("bytes=","").replace("drop=","").replace("errs=",""))





"""
volcado_estadisticas_flujo

Es invocado tras la creacion completa de la red, captura las entradas de flujo de los swtiches openFlow,
y ejecuta ovs-ofctl dump-flows en ambos swtiches. A continuacion, captura las estadisticas de los flujos
agregados mediante ovs-ofctl dump-aggregate en ambos swtiches.


 cookie=0x0, duration=3.393s, table=0, n_packets=1, n_bytes=98, idle_timeout=10, hard_timeout=30, idle_age=3,
      1              2            3         4            5             6                7              8
 priority=65535,icmp,in_port=1,vlan_tci=0x0000,dl_src=00:00:00:00:00:04,dl_dst=00:00:00:00:00:01,nw_src=10.0.0.4,
      9          10       11             12              13                         14                  15
 nw_dst=10.0.0.1,nw_tos=0,icmp_type=0,icmp_code=0 actions=output:3
      16             17         18         19             20

 duration=3.383s, n_packets=1, n_bytes=98, idle_timeout=10, idle_age=3, priority=65535,in_port=1,nw_src=10.0.0.1,nw_dst=10.0.0.2,2

#NXST_AGGREGATE reply (xid=0x4): packet_count=50 byte_count=4171 flow_count=74
#       1         2        3             4                5             6
#packet_count=50 byte_count=4171 flow_count=74

Ejecucion del comando aplicando grep con los resultados deseados, posteriormente se aplica awk para especificar
los separadores (-F) mediante comas o la acción a realizar, es necesario hacerlo así ya que la salida de la ejecución
de dump-flows es irregular y no existe un separador fijo que funcione para toda la línea.

"""

def volcado_estadisticas_flujo(firs_time, start_time):

    for swtich in range(0, len(listaSwitches)):
        writter_mode = "w+" if firs_time==True else "a"
        info(colors.BOLD+'\n========================= Extraccion de estadisticas del flujo =======================================\n\n'+colors.ENDC)

        info(colors.OKBLUE +'[!] Capturando entradas de flujo de switches en stats_flow.csv ...\n'+colors.ENDC)

       # Capturamos las entradas de flujo de los swtiches openFlow
        with open("stats_flow.csv", mode=writter_mode) as fichero_stats_flow:
            if firs_time:
                fichero_stats_flow.write(field.estadisticas_flujo)

            for swtich in range(0, len(listaSwitches)):
                string = listaSwitches[swtich].cmd("ovs-ofctl dump-flows "+str(listaSwitches[swtich])+command.tuberia_dump_flow)
                fichero_stats_flow.write(string.replace("duration=", "").replace(" n_packets=", "").replace(" n_bytes=", "").replace(
                    " idle_timeout=", "").replace(" idle_age=", "").replace(" priority=", "").replace("in_port=", "").replace("nw_src=", "").replace("nw_dst=", "").replace("s", ""))




    info(colors.OKBLUE +'[!] Capturando estadisticas de flujos agregados de switches en stats_aggregateFlow.csv ...\n'+colors.ENDC)

    # Capturamos las estadisticas de flujos agregados
    with open("stats_aggregateFlow.csv", mode=writter_mode) as fichero_aggregate_flow:
        if firs_time:
            fichero_aggregate_flow.write(field.flujo_agregado)

        for swtich in range(0, len(listaSwitches)):
            string=listaSwitches[swtich].cmd("ovs-ofctl dump-aggregate "+str(listaSwitches[swtich])+command.tuberia_agraggateFlow)
            fichero_aggregate_flow.write(str(round(time.time()-start_time,3))+","+str(listaSwitches[swtich])+",")
            fichero_aggregate_flow.write(string.replace("packet_count=","").replace("byte_count=","").replace("flow_count=",""))





"""
pings

Se ejecutan pruebas de ping de todos los hosts a todos los hosts masivamente.
La informacion será volcada en un .csv filtrando de la siguiente manera:
1 packets transmitted, 1 received, 0% packet loss, time 0ms   ---------->  1,1,0%,0ms
"""
def pings(net, listaHosts, firs_time, host_serveriperf, start_time):

    writter_mode = "w+" if firs_time==True else "a"
    info(colors.BOLD+'\n========================= Ejecución de ping ==========================================================\n\n'+colors.ENDC)

    with open("pings.csv", mode=writter_mode) as fichero_trafficcsv:
        if firs_time:
            fichero_trafficcsv.write(field.ping_stats)

        for x in range(0, len(listaHosts)):
            info(colors.OKGREEN +'\n[!] Ejecutanto pruebas de ping desde '+ str(listaHosts[x])+' a  -> '+colors.ENDC)
            for y in range(0, len(listaHosts)):
                if listaHosts[x] != listaHosts[y]:
                    info(str(listaHosts[y])+" ")
                    string = listaHosts[x].cmd('''ping -c 1 ''' + listaHosts[y].IP()+command.tuberia_ping)
                    fichero_trafficcsv.write(str(round(time.time()-start_time,3))+","+listaHosts[x].IP()+","+listaHosts[y].IP()+",")
                    fichero_trafficcsv.write(string.replace("ms", "").replace("%","").replace("read failed: Connection refused", ""))

"""
extraccion_estadisticas
Función invocadora de las funciones que extraen estadísticas relacionadas con los puertos de los switches, flujos y pings.
Cada una de ellas se encarga de obtener la información, filtrarla y volcarla a su correspondiente archivo .CSV
"""
def extraccion_estadisticas(firs_time, start_time, net, server):
    volcado_estadisticas_puertos(firs_time, start_time)
    volcado_estadisticas_flujo(firs_time, start_time)
    if ping == "1":
        pings(net, listaHosts, firs_time, listaHosts[server], start_time)




"""
myNetwork

Disenno y creacion de la topologia customizada en MININET.
"""
def myNetwork(cname='controller', cargs='-v ptcp:'):

    net = Mininet(topo=None, build=False, ipBase='10.0.0.0/8', host=CPULimitedHost, link=TCLink)

    info(colors.YELLOW + '[!] Introduciendo el controlador c0\n' + colors.ENDC)
    c0 = net.addController(name='c0', controller=RemoteController, protocol='tcp', port=6633)

    #START_TOPO

    info(colors.YELLOW + '[!] Creando los switches s1 y s2\n' + colors.ENDC)
    s1 = net.addSwitch('s1', cls=OVSKernelSwitch)
    listaNodos.append(s1)
    listaSwitches.append(s1)
    s2 = net.addSwitch('s2' ,cls=OVSKernelSwitch)
    listaNodos.append(s2)
    listaSwitches.append(s2)


    s3 = net.addSwitch('s3', cls=OVSKernelSwitch)
    listaSwitches.append(s3)

    info(colors.YELLOW + '[!] Creando los hosts h1 h2 h3 h4 h5\n'+colors.ENDC)
    h1 = net.addHost('h1', cls=Host, mac='00:00:00:00:00:01',ip='10.0.0.1/24', defaultRoute=None)
    listaHosts.append(h1)
    listaNodos.append(h1)
    h2 = net.addHost('h2', cls=Host, mac='00:00:00:00:00:02',ip='10.0.0.2/24', defaultRoute=None)
    listaHosts.append(h2)
    listaNodos.append(h2)
    h3 = net.addHost('h3', cls=Host, mac='00:00:00:00:00:03',ip='10.0.0.3/24', defaultRoute=None)
    listaHosts.append(h3)
    listaNodos.append(h3)
    h4 = net.addHost('h4', cls=Host, mac='00:00:00:00:00:04',ip='10.0.0.4/24', defaultRoute=None)
    listaHosts.append(h4)
    listaNodos.append(h4)
    h5 = net.addHost('h5', cls=Host, mac='00:00:00:00:00:05',ip='10.0.0.5/24', defaultRoute=None)
    listaHosts.append(h5)
    listaNodos.append(h5)


    info(colors.YELLOW + '[!] Creando enlaces\n'+colors.ENDC)

    l1=net.addLink(h1, s1, ID=0, bw=300)
    #l1.intf1.config(loss=50)
    listaEnlaces.append(l1)
    listabw.append(300)
    l2=net.addLink(h2, s1, ID=1, bw=300)
    listaEnlaces.append(l2)
    listabw.append(300)
    l3=net.addLink(h3, s1, ID=2, bw=300)
    listaEnlaces.append(l3)
    listabw.append(300)
    l4=net.addLink(s2, h4, ID=3, bw=300)
    listaEnlaces.append(l4)
    listabw.append(300)
    l5=net.addLink(s2, h5, ID=4, bw=300)
    listaEnlaces.append(l5)
    listabw.append(300)

    # Enlace entre ambos switches
    l6=net.addLink(s1, s2, ID=5, bw=300)
    listaEnlaces.append(l6)
    listabw.append(300)

    net.addLink(s1,s3)
    net.addLink(s3,s2)

    #END_TOPO


    #Modificacion del enlace aleatorio asignandole la probabilidad de perdida seleccionada para la ejecucion
    modificarEnlaceAleatorio(net)

    for link in range(0, len(listaEnlaces)):
        if link == link_withLoss:
            print(colors.FAIL+"   Modificado enlace con ID "+str(listaEnlaces[link].ID)+" | Origen "+str(listaEnlaces[link].intf1.node)+"   Destino "+str(listaEnlaces[link].intf2.node) +"  -  "+str(listaEnlaces[link])+colors.ENDC)
        else:
            print("   Añadido enlace con ID "+str(listaEnlaces[link].ID)+" | Origen "+str(listaEnlaces[link].intf1.node)+"   Destino "+str(listaEnlaces[link].intf2.node) +"  -  "+str(listaEnlaces[link]))

    #Lanzamiento de componentes de la red: red, controlador, swtiches...
    info(colors.YELLOW + '\n*** Lanzando la red\n')
    net.build()

    info('*** Lanzando el controlador\n')
    c0.cmd(cname + ' ' + cargs + '&')

    info('*** Lanzando los switches\n')
    for swtich in range(0, len(listaSwitches)):
        net.get("s"+str(swtich)).start([c0])


    info('*** Esperando controlador')

    while 'is_connected' not in quietRun('ovs-vsctl show'):
        sleep(1)
        info('.')

    info('\n'+colors.ENDC)

    start_time = time.time()

    firs_time = True

    #Lanzamiento del trafico masivo entre todos los hosts a partir de la matriz de trafico extraida del fichero de configuracion
    with open("iperfClients.csv", mode="w+") as iperf_c_csv, open ("iperfServers.csv", mode="w+") as iperf_s_csv:
        if firs_time:
            iperf_c_csv.write(field.iperf_stats)
            iperf_s_csv.write(field.iperf_stats_servers)

        info(colors.OKGREEN+'\n========================= Extraccion de estadisticas de iperf =================================\n\n'+colors.ENDC)


        for server in range(0,len(listaHosts)):
            info(colors.OKGREEN+" [!] Ejecutando iperf "+ str(listaHosts[server]) +" como servidor\n "+colors.ENDC)
            listaHosts[server].cmdPrint("iperf -s -p 5201 "+protocol+" -i 1 -y C >> iperfServers.csv &")

            for client in range(0, len(listaHosts)):
                if listaHosts[client] != listaHosts[server]:
                    info(colors.OKGREEN+" · [!] Ejecutando iperf "+ str(listaHosts[client]) +" como cliente\n "+colors.ENDC)
                    # listaHosts[client].cmdPrint("iperf -c "+ listaHosts[server].IP() +" -p 5201 "+protocol+" -b "+str(other.matriz[server][client])+"m -t "+str(duracion_iperf_cliente)+" -i 1 -y C >> iperfClients.csv &")
                    iperfCliente ="iperf -c "
                    iperfCliente +=listaHosts[server].IP()
                    iperfCliente +=" -p "+str(port)+" "
                    iperfCliente +=protocol
                    iperfCliente +=" -b "+str(other.matriz[server][client]/10)
                    iperfCliente +=" -t "+str(duracion_iperf_cliente)
                    iperfCliente +=" -i "+str(intervalo_iperf_cliente)
                    iperfCliente +=" -y C"
                    iperfCliente +=" >> iperfClients.csv &"
                    listaHosts[client].cmdPrint(iperfCliente)

    #Cálculo del tiempo de finalización que determina el tiempo de ejecución
    finish = datetime.datetime.now() + datetime.timedelta(seconds=int(tiempo_ejecucion))
    
    while datetime.datetime.now() < finish:
    #Ejecucion de las funciones recopiladoras de informacion
        #extraccion_estadisticas(firs_time, start_time, net, server)
        firs_time=False
        info("\n                                     ===============\n")
        info("                                          "+str(round(time.time()-start_time,2)))
        info("\n                                     ===============\n")
        #Cuando el cronometro anterior alcance los "linkDeathTime" segundos, el enlace "link_withLoss" dejara de funcionar por completo
        if round(time.time()-start_time,2) > float(linkDeathTime):
            net.configLinkStatus(str(listaEnlaces[link_withLoss].intf1.node), str(listaEnlaces[link_withLoss-1].intf2.node), 'down')
            info("\n\n")
            info(colors.FAIL+" [!] El enlace con ID "+str(listaEnlaces[link_withLoss].ID)+" se ha caído !!! \n"+colors.ENDC)
            info("\n\n")

        sleep(int(intervalo_extraccion))


    #Finalizamos las tareas en las que cada host asume el rol de SERVIDOR para ejecutar iperf
    for server in range(0,len(listaHosts)):
        info(colors.BOLD+' [!] Ejecutando kill %iperf \n'+listaHosts[server].cmd('kill %iperf')+colors.ENDC)

    net.stop()




def modificarEnlaceAleatorio(net):
    #Generacion del enlace aleatorio que tendra una perdida asociada

    for link in range(0, len(listaEnlaces)):
        if listaEnlaces[link].ID == link_withLoss:
            info(colors.FAIL+"\n\nSe ha elegido de forma aleatoria el enlace con ID "+str(link_withLoss)+"   asignandole la nueva probabilidad de perdida..."+"\n")
            info("      ID "+str(listaEnlaces[link].ID)+"\n")
            l_loss = net.addLink(listaEnlaces[link].intf1.node, listaEnlaces[link].intf2.node, ID = link_withLoss,loss =assignedLoss)   #Añado enlace 27 y lo añado a las listas
            listaEnlaces.insert(link_withLoss, l_loss)
            listaEnlaces.pop(link_withLoss)
            info("Enlace modificado:  ENLACE  con ID "+str(listaEnlaces[link].ID)+" | Origen "+str(listaEnlaces[link].intf1.node)+"   Destino "+str(listaEnlaces[link].intf2.node) +"  -  "+str(listaEnlaces[link])+"\n")
            info(colors.ENDC)
            break


'''
linkstats
Genera el dataset link_stats.csv a partir de los datos obtenidos del tráfico de los servidores durante la ejecucion de iperf

'''
def linkstats():

    #Creación de un Grafo para gestionar el datapath de tráfico de los archivos CSV
    Grafo=nx.Graph()
    #Creación de los nodos y enlaces del Grafo
    for node in range(0,len(listaNodos)):
        Grafo.add_node(str(listaNodos[node]))
    for link in range(0,len(listaEnlaces)):
        Grafo.add_edge(str(listaEnlaces[link].intf1.node), str(listaEnlaces[link].intf2.node), ID=str(listaEnlaces[link].ID))


    print("\nTrafico con perdidas detectadas \n\n")
    with open("links_stats.csv", mode="w+") as link_stats:

        link_stats.write(field.link_stats)

        archivo = open("iperfServers.csv")
        reader = csv.DictReader(archivo,delimiter=',')
        for linea in reader:
            time=linea['date']
            src=linea[' IPclient']
            dst=linea[' IPserver']
            loss=linea[' loss']
            transferred=linea[' transferred_bytes']
            for s in range(0, len(listaHosts)):
                for d in range(0, len(listaHosts)):
                    if listaHosts[s].IP()==src and listaHosts[d].IP()==dst:
                        total, path = nx.single_source_dijkstra(Grafo, source=str(listaHosts[s]), target=str(listaHosts[d]))
                        #print("Origen "+src+"   Destino "+dst+"   loss csv: "+loss+ "    loss repartida: "+str(float(loss)/total))
                        for l in range(0, len(path)-1):
                            for x in range(0, len(listaEnlaces)):
                                if ((str(listaEnlaces[x].intf1.node.name)==path[l] and str(listaEnlaces[x].intf2.node.name)==path[l+1]) or (str(listaEnlaces[x].intf2.node.name)==path[l] and str(listaEnlaces[x].intf1.node.name)==path[l+1]) and loss!="-nan"):

                                    string=str(time)+","
                                    if listaEnlaces[x].ID==link_withLoss:
                                        string+=str(assignedLoss)+","
                                    else:
                                        string+="0,"
                                    string+=str(linkDeathTime)+","
                                    string+=str(listaEnlaces[x].ID)+","
                                    if listaEnlaces[x].ID==link_withLoss:
                                        string+=str(round(float(loss)*float(assignedLoss/10)/total,4))+","
                                    else:
                                        string+=str(round(float(loss)/total,4))+","
                                    string+=str(round(float(float(transferred)*0.000008)/listabw[x],5))
                                    link_stats.write(string+"\n")

        archivo.close()

   

    df = pd.read_csv('links_stats.csv')

    #Ordeno los valores  por la fecha del experimento y, a igual fecha por el ID de cada enlace
    df = df.sort_values(by=['date','idLink'], axis=0, ascending=True)
    #Agrup los datos repetidos realizando un sumatorio de los valores del % de perdida y la ccarga del enlace
    groupBy = df.groupby(['date', '%assignLoss', 'linkDeathTime', 'idLink']).agg({'%loss': 'mean', 'linkCharge':'sum'}).reset_index()

    #Los campos del dataset cuyos valores de perdida sean superiores al 100%, se definirán como 100%
    groupBy.loc[groupBy['%loss'] > 100, "%loss"] = 100
    #Vuelco el resultado en theLast.csv
    groupBy.to_csv("thelast.csv", index=False)

    # "date, %assignLoss, linkDeathTime, idLink, %loss, linkCharge\n"

if __name__ == '__main__':

    setLogLevel('info')
    configJSON()
    myNetwork()
    linkstats()

    info(colors.FAIL)
    info('/////////////////////                                    ////////////////////////////\n')
    info('/////////////////////   EXIT. Limpiando la red con mn -c ////////////////////////////\n')
    info('/////////////////////                                    ////////////////////////////\n')
    info(colors.ENDC)
    os.system("mn -c")

    #Copia de estadísticas de OpenNetMon Monitoring
    info(colors.HEADER+'\n [!] Obteniendo datatasets de estadisticas de OpenNetMon.........................\n\n'+colors.ENDC)
    os.system(command.get_openFlow_Stats)
    os.system(command.get_openFlow_Delay)
