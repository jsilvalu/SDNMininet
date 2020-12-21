#!/bin/bash

#Ejecucion: sudo sh init.sh


#============================================== Simulacion 1 - Perdida 25 Desconexion 50 ==================================

#Ejecuto el controlador POX
gnome-terminal --execute sudo /home/idi/pox/pox.py opennetmon.startup forwarding.l2_learning openflow.discovery --eat-early-packets openflow.spanning_tree --no-flood --hold-down
sleep 1
#Ejecucuto la simulacion1
gnome-terminal --execute sudo /usr/bin/python SDNlibTopology.py 25 50

#Cierro el proceso POX
sleep 222
ps -ef | grep pox | grep -v grep | awk '{print $2}' | sudo xargs kill
sleep 1


#Renombro el archivo
mv thelast.csv LINKS_S1_2550.csv
sleep 1

sudo mv LINKS_S1_2550.csv /home/idi/mininet/custom/DATASETS


#============================================== Simulacion 2 - Perdida 25 Desconexion 100 ==================================
#Ejecuto el controlador POX
gnome-terminal --execute sudo /home/idi/pox/pox.py opennetmon.startup forwarding.l2_learning openflow.discovery --eat-early-packets openflow.spanning_tree --no-flood --hold-down
sleep 1
#Ejecucuto la simulacion1
gnome-terminal --execute sudo /usr/bin/python SDNlibTopology.py 25 100
sleep 222
#Cierro el proceso POX
ps -ef | grep pox | grep -v grep | awk '{print $2}' | sudo xargs kill
sleep 1

#Renombro el archivo
mv thelast.csv LINKS_S2_25100.csv
sleep 1

sudo mv LINKS_S2_25100.csv /home/idi/mininet/custom/DATASETS

#============================================== Simulacion 3 - Perdida 25 Desconexion 150 ==================================
#Ejecuto el controlador POX
gnome-terminal --execute sudo /home/idi/pox/pox.py opennetmon.startup forwarding.l2_learning openflow.discovery --eat-early-packets openflow.spanning_tree --no-flood --hold-down
sleep 1
#Ejecucuto la simulacion1
gnome-terminal --execute sudo /usr/bin/python SDNlibTopology.py 25 150
sleep 222
#Cierro el proceso POX
ps -ef | grep pox | grep -v grep | awk '{print $2}' | sudo xargs kill
sleep 1

#Renombro el archivo
mv thelast.csv LINKS_S3_25150.csv
sleep 1

sudo mv LINKS_S3_25150.csv /home/idi/mininet/custom/DATASETS


#============================================== Simulacion 4 - Perdida 50 Desconexion 50 ==================================
#Ejecuto el controlador POX
gnome-terminal --execute sudo /home/idi/pox/pox.py opennetmon.startup forwarding.l2_learning openflow.discovery --eat-early-packets openflow.spanning_tree --no-flood --hold-down
sleep 1
#Ejecucuto la simulacion1
gnome-terminal --execute sudo /usr/bin/python SDNlibTopology.py 50 50
sleep 222
#Cierro el proceso POX
ps -ef | grep pox | grep -v grep | awk '{print $2}' | sudo xargs kill
sleep 1

#Renombro el archivo
mv thelast.csv LINKS_S4_5050.csv
sleep 1

sudo mv LINKS_S4_5050.csv /home/idi/mininet/custom/DATASETS


#============================================== Simulacion 5 - Perdida 50 Desconexion 100 ==================================
#Ejecuto el controlador POX
gnome-terminal --execute sudo /home/idi/pox/pox.py opennetmon.startup forwarding.l2_learning openflow.discovery --eat-early-packets openflow.spanning_tree --no-flood --hold-down
sleep 1
#Ejecucuto la simulacion1
gnome-terminal --execute sudo /usr/bin/python SDNlibTopology.py 50 100
sleep 222
#Cierro el proceso POX
ps -ef | grep pox | grep -v grep | awk '{print $2}' | sudo xargs kill
sleep 1

#Renombro el archivo
mv thelast.csv LINKS_S5_50100.csv
sleep 1

sudo mv LINKS_S5_50100.csv /home/idi/mininet/custom/DATASETS



#============================================== Simulacion 6 - Perdida 50 Desconexion 150 ==================================
#Ejecuto el controlador POX
gnome-terminal --execute sudo /home/idi/pox/pox.py opennetmon.startup forwarding.l2_learning openflow.discovery --eat-early-packets openflow.spanning_tree --no-flood --hold-down
sleep 1
#Ejecucuto la simulacion1
gnome-terminal --execute sudo /usr/bin/python SDNlibTopology.py 50 150
sleep 222
#Cierro el proceso POX
ps -ef | grep pox | grep -v grep | awk '{print $2}' | sudo xargs kill
sleep 1

#Renombro el archivo
mv thelast.csv LINKS_S6_50150.csv
sleep 1

sudo mv LINKS_S6_50150.csv /home/idi/mininet/custom/DATASETS


#============================================== Simulacion 7 - Perdida 75 Desconexion 50 ==================================
#Ejecuto el controlador POX
gnome-terminal --execute sudo /home/idi/pox/pox.py opennetmon.startup forwarding.l2_learning openflow.discovery --eat-early-packets openflow.spanning_tree --no-flood --hold-down
sleep 1
#Ejecucuto la simulacion1
gnome-terminal --execute sudo /usr/bin/python SDNlibTopology.py 75 50
sleep 222
#Cierro el proceso POX
ps -ef | grep pox | grep -v grep | awk '{print $2}' | sudo xargs kill
sleep 1

#Renombro el archivo
mv thelast.csv LINKS_S7_7550.csv
sleep 1

sudo mv LINKS_S7_7550.csv /home/idi/mininet/custom/DATASETS


#============================================== Simulacion 8 - Perdida 75 Desconexion 100 ==================================
#Ejecuto el controlador POX
gnome-terminal --execute sudo /home/idi/pox/pox.py opennetmon.startup forwarding.l2_learning openflow.discovery --eat-early-packets openflow.spanning_tree --no-flood --hold-down
sleep 1
#Ejecucuto la simulacion1
gnome-terminal --execute sudo /usr/bin/python SDNlibTopology.py 75 100
sleep 222
#Cierro el proceso POX
ps -ef | grep pox | grep -v grep | awk '{print $2}' | sudo xargs kill
sleep 1

#Renombro el archivo
mv thelast.csv LINKS_S8_75100.csv
sleep 1

sudo mv LINKS_S8_75100.csv /home/idi/mininet/custom/DATASETS


#============================================== Simulacion 9 - Perdida 75 Desconexion 150 ==================================
#Ejecuto el controlador POX
gnome-terminal --execute sudo /home/idi/pox/pox.py opennetmon.startup forwarding.l2_learning openflow.discovery --eat-early-packets openflow.spanning_tree --no-flood --hold-down
sleep 1
#Ejecucuto la simulacion1
gnome-terminal --execute sudo /usr/bin/python SDNlibTopology.py 75 150
sleep 222
#Cierro el proceso POX
ps -ef | grep pox | grep -v grep | awk '{print $2}' | sudo xargs kill
sleep 1


#Renombro el archivo
mv thelast.csv LINKS_S9_75150.csv
sleep 1

sudo mv LINKS_S9_75150.csv /home/idi/mininet/custom/DATASETS
