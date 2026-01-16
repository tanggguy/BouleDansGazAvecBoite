# -*-coding:Utf-8 -*
import sys
import os
import os.path
import math
import csv
import datetime
from pathlib import Path
import shutil 
from matplotlib import pyplot as plt

##############################################################################
##############################################################################
##############################################################################
##############################################################################
#
#   Graphiques de données issues de Probes
#
#   L'utilisation de légendes et textes plus élaborés en mode LaTex
#   Text rendering With LaTeX
#   https://matplotlib.org/tutorials/text/usetex.html
#
##############################################################################
##############################################################################
##############################################################################
##############################################################################

TMaxCase = 873.15-273.15
TMinCase = 293.15-273.15

Time = []

ZSolid_CentreTubeSortie = []
TSolid_CentreTubeSortie = []
ZWater_CentreTubeSortie = []
TWater_CentreTubeSortie = []

ZSolid_CoteEntree = []
TSolid_CoteEntree = []

ZSolid_CoteSortie = []
TSolid_CoteSortie = []

FoldersRes = []
#############################################################################
#
#   Graphiques de données issues de Probe
#
##############################################################################


##############################################################################################
Time = []
LabelLegende = []

Probes = []
LigneProbes = []

GraphColor = ['b','g','r','c','m','y','b','g','r','c','m','y','b','g','r','c','m','y','b','g','r','c','m','y','b','g','r','c','m','y']


PathProbes = "postProcessing/Probes_Solid/solid"

DossiersRes = os.listdir(PathProbes)

FoldersRes = DossiersRes.sort()

IndicDossier = 0
NbreLignesDossier_i = []

for Dossier_i in DossiersRes:

    NomFichierProbes = "postProcessing/Probes_Solid/solid/"+str(Dossier_i)+"/T"

    NumLine = 0
    NbProbes = 0
    with open(NomFichierProbes, "r") as ProbesFile:
        for line in ProbesFile:
            NumLine += 1
            if "Probe" in line:
                NbProbes += 1
                LabelLegende.append(line[2:line.find(")")+1])
            
    NbreLignesDossier_i.append(NumLine-(NbProbes+1))
#print("LabelLegende", LabelLegende)
#print("NbProbes", NbProbes)
#print("NumLine-(NbProbes+1)", NumLine-(NbProbes+1))  

    ProbesFile.close()

#  Definition de la dimension des tables
NbreTotalLignesDossier = 0
for i in range(0, len(DossiersRes)):
    NbreTotalLignesDossier = NbreTotalLignesDossier + NbreLignesDossier_i[i]

TableProbes = [ [ 0 for j in range(NbProbes)] for i in range(NbreTotalLignesDossier)]
Time = [ 0 for i in range(NbreTotalLignesDossier)]


NumLineGlobal = 0
for i in range(0, len(DossiersRes)):

    NomFichierProbes = "postProcessing/Probes_Solid/solid/"+str(DossiersRes[i])+"/T"
    
    print(NomFichierProbes)
    
    NumLine = 0
    with open(NomFichierProbes, "r") as ProbesFile:
        for line in ProbesFile:
            NumLine += 1
            if NumLine > NbProbes+1:
                coords = line.split()
                Time[NumLineGlobal] = float(coords[0])
                for i in range(NbProbes):
                    TableProbes[NumLineGlobal][i] = float(coords[i+1]) - 273.15
                
                NumLineGlobal += 1         
                       
    ProbesFile.close()


plt.figure(figsize=(9, 6))

for i in range(NbProbes):        
    plt.plot(Time, [row[i] for row in TableProbes], c=GraphColor[i], label=LabelLegende[i],linewidth=1.0)
    
#, label=LabelLegende[i]
#plt.yscale('log')
plt.grid(True,which="both", linestyle='--',linewidth=0.5)

plt.ylabel(r'$T (°C)$', fontsize=12)  # Add an x-label to the axes, rotation=0 pour affichafe horizontal 
plt.xlabel(r'$Time$', fontsize=12)  # Add an x-label to the axes.


plt.legend(bbox_to_anchor=(1.05, 1.0), loc='upper left')
plt.tight_layout()

plt.title("Probes - Température",  loc='center')

plt.savefig('postProcessing/Probes_T_degC.pdf', bbox_inches='tight')

plt.clf()

print("That's All Folks !")





