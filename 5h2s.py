#!/usr/bin/python

from mininet.net import Mininet
from mininet.node import Controller, RemoteController, OVSController
from mininet.node import CPULimitedHost, Host, Node
from mininet.node import OVSKernelSwitch, UserSwitch
from mininet.node import IVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink, Intf
from subprocess import call
from mininet.util import quietRun
from time import sleep

import os

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
    PURPLE='\033[35m'


"""
volcado_estado_capacidad_puertos

Realiza una conexion a los swtiches openFlow para descargar el estado completo de sus puertos y capacidades
mediante ovs-ofctl show, despues obtiene las estadisticas de los puertoss asociados a los switches openFlow
ejecutando la instruccion ovs-ofctl dump-ports. El resultado de ambos mandatos se vuelvan en los ficheros de
texto correspondientes.
"""
def volcado_estado_capacidad_puertos(s1,s2,s1File,s2File):
    #Realizamos una conexion a los swtiches openflow y descargamos el estado de su puerto y capadidad
    with open(s1File, mode="w+") as fichero1, open(s2File, mode="w+") as fichero2:
        fichero1.write(" ESTADO DE PUERTOS Y CAPACIDAD:\n =========================================\n")
        fichero2.write(" ESTADO DE PUERTOS Y CAPACIDAD:\n =============================\n")

    info(colors.OKBLUE+'[!] Capturando informacion de puertos y capacidad de S1 en fichero '+s1File+'...\n'+colors.ENDC)
    s1.cmdPrint('ovs-ofctl show s1 >> '+s1File)
    info(colors.OKBLUE+'[!] Capturando informacion de puertos y capacidad de S2 en fichero '+s2File+'...\n'+colors.ENDC)
    s2.cmdPrint('ovs-ofctl show s2 >> '+s2File)


    #Imprimimos las estadisticas de los puertos asociados a los switches openFlow
    with open(s1File, mode="a") as fichero1, open(s2File, mode="a") as fichero2:
        fichero1.write("\n\n ESTADISTICAS DE LOS PUERTOS:\n =========================================n")
        fichero2.write("\n\n ESTADISTICAS DE LOS PUERTOS:\n =========================================n")

    info(colors.OKBLUE+'[!] Capturando estadisticas de los puertos en '+s1File+'...\n'+colors.ENDC)
    s1.cmdPrint('ovs-ofctl dump-ports s1 >> '+s1File)
    info(colors.OKBLUE+'[!] Capturando estadisticas de los puertos en'+s2File+'...\n'+colors.ENDC)
    s2.cmdPrint('ovs-ofctl dump-ports s2 >> '+s2File)



"""
volcado_estadisticas_flujo

Es invocado tras la creación completa de la red, captura las entradas de flujo de los swtiches openFlow,
y ejecuta ovs-ofctl dump-flows en ambos swtiches. A continuacion, captura las estadisticas de los flujos
agregados mediante ovs-ofctl dump-aggregate en ambos swtiches.
"""

def volcado_estadisticas_flujo(s1,s2,s1File,s2File):
    #Capturamos las entradas de flujo de los swtiches openFlow
    with open(s1File, mode="a") as fichero1, open(s2File, mode="a") as fichero2:
        fichero1.write("\n\n ENTRADAS DE FLUJO:\n =========================================n")
        fichero2.write("\n\n ENTRADAS DE FLUJO:\n =========================================n")


    info(colors.OKBLUE+'[!] Capturando entradas de flujo de s1 en '+s1File+'...\n'+colors.ENDC)
    s1.cmdPrint('ovs-ofctl dump-flows s1 >> '+s1File)
    info(colors.OKBLUE+'[!] Capturando entradas de flujo de s1 en '+s2File+'...\n'+colors.ENDC)
    s2.cmdPrint('ovs-ofctl dump-flows s2 >> '+s2File)


    #Capturamos las estadisticas de flujos agregados
    with open(s1File, mode="a") as fichero1, open(s2File, mode="a") as fichero2:
        fichero1.write("\n\n ESTADISTICAS DE LOS flujos agregados:\n =========================================n")
        fichero2.write("\n\n ESTADISTICAS DE LOS flujos agregados:\n =========================================n")


    info(colors.OKBLUE+'[!] Capturando estadisticas de flujos agregados de s1 en '+s1File+'...\n'+colors.ENDC)
    s1.cmdPrint('ovs-ofctl dump-aggregate s1 >> '+s1File)
    info(colors.OKBLUE+'[!] Capturando estadisticas de flujos agregados de s1 en'+s2File+'...\n'+colors.ENDC)
    s2.cmdPrint('ovs-ofctl dump-aggregate s2 >> '+s2File)





"""
volcado_pingTests

Es invocado tras la creación completa de la red, captura y vuelca informacion de diversas pruebas de ping e iperf
en la red en el fichero indicado en la funcion de apertura.
"""
def volcado_pingTests(net):
        
    with open("ping_stats.txt", mode="w") as fichero1:
        info(colors.PURPLE+'[!] Ejecutando prueba de iperf'+colors.ENDC )
        fichero1.write(str(net.iperf()))
        fichero1.write("\n")
        info(colors.PURPLE+'[!] Ejecutando prueba de pingFull'+colors.ENDC )
        fichero1.write(str(net.pingFull()))





"""
myNetwork

Diseño y creacion de la topologia customizada en MININET.
"""
def myNetwork(cname='controller', cargs='-v ptcp:'):

    net = Mininet( topo=None,build=False,ipBase='10.0.0.0/8')

    info( colors.YELLOW +'[!] Introduciendo el controlador c0\n'+ colors.ENDC )
    c0=net.addController(name='c0',controller=RemoteController,protocol='tcp',port=6633)

    info(colors.YELLOW +'[!] Creando los switches s1 y s2\n'+ colors.ENDC)
    s1 = net.addSwitch('s1', cls=OVSKernelSwitch)
    s2 = net.addSwitch('s2', cls=OVSKernelSwitch)

    info(colors.YELLOW + '[!] Creando los hosts h1 h2 h3 h4 h5\n'+colors.ENDC)
    h1 = net.addHost('h1', cls=Host , mac='00:00:00:00:00:01', ip='10.0.0.1/24', defaultRoute=None)
    h2 = net.addHost('h2', cls=Host , mac='00:00:00:00:00:02', ip='10.0.0.2/24', defaultRoute=None)
    h3 = net.addHost('h3', cls=Host , mac='00:00:00:00:00:03', ip='10.0.0.3/24', defaultRoute=None)
    h4 = net.addHost('h4', cls=Host , mac='00:00:00:00:00:04', ip='10.0.0.4/24', defaultRoute=None)
    h5 = net.addHost('h5', cls=Host , mac='00:00:00:00:00:05', ip='10.0.0.5/24', defaultRoute=None)

    listaHosts=[h1,h2,h3,h4,h5]


    info(colors.YELLOW +'[!] Creando enlaces\n'+colors.ENDC)
    # h1s1 = {'loss':50} #Definicion de probabilidad de perdida en enlace h1 - s1
   
    # net.addLink(h1, s1, pl=h1s1['loss'], cls=TCLink, **h1s1)
    net.addLink(h1, s1)
    net.addLink(s1, h2)
    net.addLink(h3, s1)
    net.addLink(s2, h4)
    net.addLink(s2, h5)
    
    #Enlace entre ambos switches
    net.addLink(s1, s2)


    info( '\n*** Lanzando la red\n')
    net.build()

    info( '*** Lanzando el controlador\n')
    c0.cmd( cname + ' ' + cargs + '&' )  

    info( '*** Lanzando los switches\n')
    net.get('s1').start([c0])
    net.get('s2').start([c0])
   
    info( '*** Esperando controlador' )

    while 'is_connected' not in quietRun( 'ovs-vsctl show' ):
        sleep( 1 )
        info( '.' )

    info( '\n' )

    info( colors.BOLD+'=====================================  NET TESTS  =====================================\n'+colors.ENDC)
    # sleep( 1 )
    # #Pruebas de ping
    # for x in range(0,len(listaHosts)):
    #   for y in range(0,len(listaHosts)):
    #     if listaHosts[x] !=  listaHosts[y]:
    #       info( '[!] Ejecutanto pruebas de ping')
    #       listaHosts[x].cmdPrint( 'ping -Q 0x64 -c 2 ' + listaHosts[y].IP() )
    #       #ping -c 10 s2 | grep packets | awk '{print $1","$6","$10}'
    #       info( '\n' )
    # sleep( 1 )
    #Pruebas de pingall
    # info( '[!] Ejecutando prueba de pingall' )
    # net.pingAll()
    # sleep( 1 )
    # info( '\n' )
    # #Pruebas de iperf
    # info( '[!] Ejecutando prueba de iperf' )
    # net.iperf()
    # #iperf -c 127.0.0.1 -t 2 -i 0.5 -f m | tee log1
    # #awk -F'[ -]+' '/sec/{print $3"-"$4" "$8}' log1
    # sleep( 1 )
    # info( '\n' )
    # info(colors.PURPLE+'[!] Ejecutando prueba de pingFull'+colors.ENDC )
    # net.pingFull()

    volcado_pingTests(net)

    info( colors.BOLD+'\n========================= Extraccion de estadisticas de los switches =================================\n\n'+colors.ENDC)

    s1File="swtichS1_stats.txt"
    s2File="switchS2_stats.txt"
    
    volcado_estado_capacidad_puertos(s1, s2, s1File, s2File)
    volcado_estadisticas_flujo(s1,s2,s1File,s2File)


  
    
    CLI(net)
    net.stop()




if __name__ == '__main__':
    setLogLevel( 'info' )
    myNetwork()
    info(colors.FAIL)
    info( '/////////////////////                                    ////////////////////////////\n' )
    info( '/////////////////////   EXIT. Limpiando la red con mn -c ////////////////////////////\n' )
    info( '/////////////////////                                    ////////////////////////////\n' )
    info(colors.ENDC)
    os.system("mn -c")
