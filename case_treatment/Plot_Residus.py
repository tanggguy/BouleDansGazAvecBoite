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

#############################################################################
#
#   Graphiques Résidus 
#
##############################################################################

GraphColor = ['b','g','r','c','m','y','b','g','r','c','m','y','b','g','r','c','m','y','b','g','r','c','m','y','b','g','r','c','m','y']


Time = []
Res_h_initial = []
Res_h_final = []




NomFichierResiduals = "postProcessing/solid/solid_residuals/0/solverInfo.dat"

NumLine = 0
with open(NomFichierResiduals, "r") as ResFile:
    for line in ResFile:
        NumLine += 1
        
        if NumLine > 4:
            coords = line.split()
            Time.append(float(coords[0]))
            Res_h_initial.append(float(coords[2]))
            Res_h_final.append(float(coords[3]))

ResFile.close()




plt.figure(figsize=(9, 6))

#plt.plot(Time, Res_h_initial, c=GraphColor[0], label='h_initial - chtMultiRegionFoam',linewidth=1.0)
plt.plot(Time, Res_h_final, c=GraphColor[1], label='h_final - chtMultiRegionFoam',linewidth=1.0)




plt.yscale('log')
plt.grid(True,which="both", linestyle='--',linewidth=0.5)

plt.ylabel(r'$Residuals$', fontsize=12)  # Add an x-label to the axes, rotation=0 pour affichafe horizontal 
plt.xlabel(r'$Time$', fontsize=12)  # Add an x-label to the axes.


plt.legend()   #  plt.legend(loc=2) Pour positonner la légende à gauche

plt.title("Resisuals - solid - chtMultiRegionFoam",  loc='center')

plt.savefig('postProcessing/residuals_solid_plot.png', bbox_inches='tight')
#plt.savefig('postProcessing/residuals_plot.pdf', bbox_inches='tight')

plt.clf()



#plt.show()


Time = []
Res_Ux_final = []
Res_Uy_final = []
Res_Uz_final = []
Res_h_final = []
Res_p_rgh_final = []




NomFichierResiduals = "postProcessing/water/water_residuals/0/solverInfo.dat"

NumLine = 0
with open(NomFichierResiduals, "r") as ResFile:
    for line in ResFile:
        NumLine += 1
        
        if NumLine > 4:
            coords = line.split()
            Time.append(float(coords[0]))
            Res_Ux_final.append(float(coords[3]))
            Res_Uy_final.append(float(coords[6]))
            Res_Uz_final.append(float(coords[9]))
            Res_h_final.append(float(coords[14]))
            Res_p_rgh_final.append(float(coords[19]))

ResFile.close()




plt.figure(figsize=(9, 6))

plt.plot(Time, Res_Ux_final, c=GraphColor[0], label='Ux - chtMultiRegionFoam',linewidth=1.0)
plt.plot(Time, Res_Uy_final, c=GraphColor[1], label='Uy - chtMultiRegionFoam',linewidth=1.0)
plt.plot(Time, Res_Uz_final, c=GraphColor[2], label='Uz - chtMultiRegionFoam',linewidth=1.0)
plt.plot(Time, Res_h_final, c=GraphColor[3], label='h - chtMultiRegionFoam',linewidth=1.0)
plt.plot(Time, Res_p_rgh_final, c=GraphColor[4], label='p_rgh - chtMultiRegionFoam',linewidth=1.0)




plt.yscale('log')
plt.grid(True,which="both", linestyle='--',linewidth=0.5)

plt.ylabel(r'$Residuals$', fontsize=12)  # Add an x-label to the axes, rotation=0 pour affichafe horizontal 
plt.xlabel(r'$Time$', fontsize=12)  # Add an x-label to the axes.


plt.legend()   #  plt.legend(loc=2) Pour positonner la légende à gauche

plt.title("Resisuals - water - chtMultiRegionFoam",  loc='center')

plt.savefig('postProcessing/residuals_water_plot.png', bbox_inches='tight')
#plt.savefig('postProcessing/residuals_plot.pdf', bbox_inches='tight')

plt.clf()



#plt.show()





print("That's All Folks !")





