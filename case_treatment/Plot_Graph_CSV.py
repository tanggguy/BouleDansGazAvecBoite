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
#   Graphiques de données issues de singleGraph
#
#   L'utilisation de légendes et textes plus élaborés en mode LaTex
#   Text rendering With LaTeX
#   https://matplotlib.org/tutorials/text/usetex.html
#
##############################################################################
##############################################################################
##############################################################################
##############################################################################
PathGraphs = "postProcessing/ZGraph_Centre_Solid/solid"

DossiersGraph = os.listdir(PathGraphs)

NumNomDossiers = []

for Dossier_i in DossiersGraph:
    NumNomDossiers.append(int(Dossier_i))
    

LastWriteTime = max(NumNomDossiers)

print("Dossier traité : ", LastWriteTime)

BoiteCote = 0.1  # m, définit par la géométrie

TMaxCase = 873.15-273.15
TMinCase = 293.15-273.15


ZSolid_Centre = []
TSolid_Centre = []
ZWater_Centre = []
TWater_Centre = []

ZSolid_CentreTubeSortie = []
TSolid_CentreTubeSortie = []
ZWater_CentreTubeSortie = []
TWater_CentreTubeSortie = []


ZSolid_CoteEntree = []
TSolid_CoteEntree = []

ZSolid_CoteSortie = []
TSolid_CoteSortie = []



#############################################################################
#
#   Graphiques de donénes issues de singleGraph
#
##############################################################################


##############################################################################################
# Lecture Ligne Centrale Solid
NomFichierCentralSolid = "postProcessing/ZGraph_Centre_Solid/solid/"+str(LastWriteTime)+"/line_T.csv"
LignesCentralSolid = [] 
# reading csv file 
with open(NomFichierCentralSolid, newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for ligne in reader: 
        LignesCentralSolid.append(ligne) 
        NbLignesCentralSolid = reader.line_num
        
csvfile.close()


for i in range(1,NbLignesCentralSolid-1):
    ZSolid_Centre.append(float(LignesCentralSolid[i][0]))
    TSolid_Centre.append(float(LignesCentralSolid[i][1])-273.15)


##############################################################################################
# Lecture Ligne Centrale Water
NomFichierCentralWater = "postProcessing/ZGraph_Centre_Water/water/"+str(LastWriteTime)+"/line_T_p_U.csv"
LignesCentralWater = [] 
# reading csv file 
with open(NomFichierCentralWater, newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for ligne in reader: 
        LignesCentralWater.append(ligne) 
        NbLignesCentralWater = reader.line_num
        
csvfile.close()


for i in range(1,NbLignesCentralWater-1):
    ZWater_Centre.append(float(LignesCentralWater[i][0]))
    TWater_Centre.append(float(LignesCentralWater[i][1])-273.15)


##############################################################################################
# Lecture Ligne CentreTubeSortie Solid
NomFichierCentreTubeSortieSolid = "postProcessing/ZGraph_CentreTubeSortie_Solid/solid/"+str(LastWriteTime)+"/line_T.csv"
LignesCentreTubeSortieSolid = [] 
# reading csv file 
with open(NomFichierCentreTubeSortieSolid, newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for ligne in reader: 
        LignesCentreTubeSortieSolid.append(ligne) 
        NbLignesCentreTubeSortieSolid = reader.line_num
        
csvfile.close()

for i in range(1,NbLignesCentreTubeSortieSolid-1):
    ZSolid_CentreTubeSortie.append(float(LignesCentreTubeSortieSolid[i][0]))
    TSolid_CentreTubeSortie.append(float(LignesCentreTubeSortieSolid[i][1])-273.15)

##############################################################################################
# Lecture Ligne CentreTubeSortie Water
NomFichierCentreTubeSortieWater = "postProcessing/ZGraph_CentreTubeSortie_Water/water/"+str(LastWriteTime)+"/line_T_p_U.csv"
LignesCentreTubeSortieWater = [] 
# reading csv file 
with open(NomFichierCentreTubeSortieWater, newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for ligne in reader: 
        LignesCentreTubeSortieWater.append(ligne) 
        NbLignesCentreTubeSortieWater = reader.line_num
        
csvfile.close()

for i in range(1,NbLignesCentreTubeSortieWater-1):
    ZWater_CentreTubeSortie.append(float(LignesCentreTubeSortieWater[i][0]))
    TWater_CentreTubeSortie.append(float(LignesCentreTubeSortieWater[i][1])-273.15)



##############################################################################################
# Lecture Ligne Cote Sortie Solid
NomFichierCoteSortieSolid = "postProcessing/ZGraph_CoteSortie_Solid/solid/"+str(LastWriteTime)+"/line_T.csv"
LignesCoteSortieSolid = [] 
# reading csv file 
with open(NomFichierCoteSortieSolid, newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for ligne in reader: 
        LignesCoteSortieSolid.append(ligne) 
        NbLignesCoteSortieSolid = reader.line_num
        
csvfile.close()

for i in range(1,NbLignesCoteSortieSolid-1):
    ZSolid_CoteSortie.append(float(LignesCoteSortieSolid[i][0]))
    TSolid_CoteSortie.append(float(LignesCoteSortieSolid[i][1])-273.15)

##############################################################################################
# Lecture Ligne Cote Entree Solid
NomFichierCoteEntreeSolid = "postProcessing/ZGraph_CoteEntree_Solid/solid/"+str(LastWriteTime)+"/line_T.csv"
LignesCoteEntreeSolid = [] 
# reading csv file 
with open(NomFichierCoteEntreeSolid, newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for ligne in reader: 
        LignesCoteEntreeSolid.append(ligne) 
        NbLignesCoteEntreeSolid = reader.line_num
        
csvfile.close()

for i in range(1,NbLignesCoteEntreeSolid-1):
    ZSolid_CoteEntree.append(float(LignesCoteEntreeSolid[i][0]))
    TSolid_CoteEntree.append(float(LignesCoteEntreeSolid[i][1])-273.15)

##############################################################################################
##############################################################################################
##############################################################################################
# Graphique

Zmin = 0
Zmax = BoiteCote
Tmin = TMinCase-10
Tmax = TMaxCase+10



plt.figure(figsize=(9, 6))
plt.xlim(Zmin, Zmax)
plt.ylim(Tmin, Tmax)

plt.ylabel(r'$T (°C)$', fontsize=12)  # Add an x-label to the axes, rotation=0 pour affichafe horizontal 
plt.xlabel(r'$Z (m)$', fontsize=12)  # Add an x-label to the axes.

plt.plot(ZSolid_Centre, TSolid_Centre, 'b*', label='Centre Solid')
plt.plot(ZWater_Centre, TWater_Centre, 'b--', label='Centre Water')

plt.plot(ZSolid_CentreTubeSortie, TSolid_CentreTubeSortie, 'g*', label='Centre Tube Sortie Solid')
plt.plot(ZWater_CentreTubeSortie, TWater_CentreTubeSortie, 'g--', label='Centre Tube Sortie Water')

plt.plot(ZSolid_CoteSortie, TSolid_CoteSortie, 'm-.', label='Cote Sortie Solid')

plt.plot(ZSolid_CoteEntree, TSolid_CoteEntree, 'c-.', label='Cote Entree Solid')


plt.legend(loc=2)

plt.savefig('postProcessing/Profils_T.pdf', bbox_inches='tight')

plt.clf()




#plt.show()





print("That's All Folks !")





