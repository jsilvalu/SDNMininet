from os import listdir
from os.path import isfile, isdir
import os
import csv, operator
import pandas as pd



def ls1(path):    
    return [obj for obj in listdir(path) if isfile(path + obj)]


def mod_datasetscsv(path):
    for datasetcsv in path:
        if datasetcsv != "toMachineLearning.py":
            print(datasetcsv)
            reader = pd.read_csv(datasetcsv)
            itercsv(reader, datasetcsv)



def itercsv(reader, datasetcsv):

    f = open(datasetcsv)
    csv_f = csv.reader(f)
    #Creo dos listas para almacenar el valor de las columnas seleccionadas
    linkChargeList=[]
    pLossList=[]

    for row in csv_f:
        linkChargeList.append(row[5])
        pLossList.append(row[4])
        deathTime = row[2]


    f.close()

    with open("./DatasetsJSON/"+datasetcsv+".json", mode="w+") as link_stats:
    
        #Formato JSON estandar
        link_stats.write("{\n")
        link_stats.write('  "ml_x": [\n')

        #Volcado de datos
        for x in range(2, len(linkChargeList)):
            link_stats.write("            [ "+linkChargeList[x]+","+pLossList[x]+","+linkChargeList[x-1]+","+pLossList[x-1]+" ],\n")

        link_stats.seek(-2, os.SEEK_END)
        link_stats.write('  ],\n')

        link_stats.write('  "ml_y": [\n')
        link_stats.write("            [ ")

        cont_salto=0
        true_deathTime=int(deathTime)-1
        for x in range(2, len(linkChargeList)):
            cont_salto+=1
            if cont_salto == 50:
                link_stats.write("\n")
                link_stats.write("              ")
                cont_salto=0
            
            link_stats.write(str(true_deathTime)+",")


        link_stats.seek(-1, os.SEEK_END)
        link_stats.write('  ]\n')
        link_stats.write('  ]\n')
        link_stats.write("}\n")




if __name__ == '__main__':
    path=ls1("/home/idi/mininet/custom/DATASETS/")
    print("Datasets existentes en el directorio: ")
    mod_datasetscsv(path)

