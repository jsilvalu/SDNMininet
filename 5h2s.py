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


def myNetwork(cname='controller', cargs='-v ptcp:'):

    net = Mininet( topo=None,build=False,ipBase='10.0.0.0/8')

    info( '[!] Introduciendo el controlador c0\n' )
    c0=net.addController(name='c0',controller=RemoteController,protocol='tcp',port=6633)

    info( '[!] Creando los switches s1 y s2\n')
    s1 = net.addSwitch('s1', cls=OVSKernelSwitch)
    s2 = net.addSwitch('s2', cls=OVSKernelSwitch)

    info( '[!] Creando los hosts h1 h2 h3 h4 h5\n')
    h1 = net.addHost('h1', cls=Host , mac='00:00:00:00:00:01', ip='10.0.0.1/24', defaultRoute=None)
    h2 = net.addHost('h2', cls=Host , mac='00:00:00:00:00:02', ip='10.0.0.2/24', defaultRoute=None)
    h3 = net.addHost('h3', cls=Host , mac='00:00:00:00:00:03', ip='10.0.0.3/24', defaultRoute=None)
    h4 = net.addHost('h4', cls=Host , mac='00:00:00:00:00:04', ip='10.0.0.4/24', defaultRoute=None)
    h5 = net.addHost('h5', cls=Host , mac='00:00:00:00:00:05', ip='10.0.0.5/24', defaultRoute=None)

    listaHosts=[h1,h2,h3,h4,h5]


    info( '[!] Creando enlaces\n')
    net.addLink(h1, s1)
    net.addLink(s1, h2)
    net.addLink(h3, s1)
    net.addLink(s2, h4)
    net.addLink(s2, h5)
    #Enlace entre ambos switches
    net.addLink(s1, s2)


    info( '*** Lanzando la red\n')
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

    info( '=====================================  NET TESTS  =====================================\n')
    sleep( 1 )
    #Pruebas de ping
    for x in range(0,len(listaHosts)):
      for y in range(0,len(listaHosts)):
        if listaHosts[x] !=  listaHosts[y]:
          info( '[!] Ejecutanto pruebas de ping')
          listaHosts[x].cmdPrint( 'ping -Q 0x64 -c 2 ' + listaHosts[y].IP() )
          #ping -c 10 s2 | grep packets | awk '{print $1","$6","$10}'
          info( '\n' )
    sleep( 1 )
    #Pruebas de pingall
    info( '[!] Ejecutando prueba de pingall' )
    net.pingAll()
    sleep( 1 )
    info( '\n' )
    #Pruebas de iperf
    info( '[!] Ejecutando prueba de iperf' )
    net.iperf()
    #iperf -c 127.0.0.1 -t 2 -i 0.5 -f m | tee log1
    #awk -F'[ -]+' '/sec/{print $3"-"$4" "$8}' log1
    sleep( 1 )
    info( '\n' )

    info( '[!] Ejecutando prueba de pingFull' )
    net.pingFull()
    sleep( 1 )
    info( '\n' )
    info( '===================================== FIN TESTS ======================================\n')

    
    
    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    myNetwork()
    info( '/////////////////////                                    ////////////////////////////' )
    info( '/////////////////////   EXIT. Limpiando la red con mn -c ////////////////////////////' )
    info( '/////////////////////                                    ////////////////////////////' )
    os.system("mn -c")
