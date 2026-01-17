############################################################
# Script to generate STL geometry for OpenFOAM simulation  #
#                                           Jean-Luc Harion#
############################################################

import salome
import GEOM
from salome.geom import geomBuilder
geompy = geomBuilder.New()

import os
import sys

# Main_dir = os.getcwd()
# Def_Geometrie_dir = os.path.join( Main_dir, 'Parametres')
# sys.path.append( Def_Geometrie_dir )

path_parametres = "/home/tanguy/OpenFOAM/tanguy-v2506/run/BouleDansGazAvecBoite/Geom_Salome_STLFiles/Parametres"

# 2. On l'ajoute à la liste des chemins que Python connaît
if path_parametres not in sys.path:
    sys.path.append(path_parametres)
###########################
# Import parameters files #
###########################

# Import .py files which contain parameters #
from importlib import reload

from Parametres_geo_maillage import *
# GasCote = 0.1                     # [m]
# R_sphere = 0.03                     # [m]
# EpaisseurBox = 0.01                  # [m]

# Center = BoiteCote/2

from sed_function import sed

O = geompy.MakeVertex(0, 0, 0)
OX = geompy.MakeVectorDXDYDZ(1, 0, 0)
OY = geompy.MakeVectorDXDYDZ(0, 1, 0)
OZ = geompy.MakeVectorDXDYDZ(0, 0, 1)

#1. gas
gas = geompy.MakeBoxDXDYDZ(GasCote, GasCote, GasCote)

#2. sphere
sphere = geompy.MakeSphereR(R_sphere)
geompy.TranslateDXDYDZ(sphere, Center, Center, Center)

#3. box_xmax
box_xmax = geompy.MakeBoxDXDYDZ(EpaisseurBox, GasCote, GasCote)
geompy.TranslateDXDYDZ(box_xmax, GasCote, 0, 0)

#4. box_xmin
box_xmin = geompy.MakeBoxDXDYDZ(EpaisseurBox, GasCote, GasCote)
geompy.TranslateDXDYDZ(box_xmin, -EpaisseurBox, 0, 0)


## ------------------Partition-------------------------
objets_a_partitionner = [gas, sphere, box_xmax, box_xmin]
Geometry_Finale = geompy.MakePartition(objets_a_partitionner, [], [], [], geompy.ShapeType["SOLID"])

geompy.addToStudy(Geometry_Finale, 'DOMAINE_COMPLET')

## 5. CREATION DES GROUPES (Version Corrigée pour Salome 9+)
# =========================================================

# Petite tolérance
eps = 1e-6 

def get_shapes_in_box_coords(shape, x1, y1, z1, x2, y2, z2, shape_type):
    # Crée une boite temporaire pour la sélection
    p_min = geompy.MakeVertex(x1, y1, z1)
    p_max = geompy.MakeVertex(x2, y2, z2)
    box_sel = geompy.MakeBoxTwoPnt(p_min, p_max)
    
    # GetShapesOnShape(theCheckShape, theShape, theShapeType, theState)
    # Le premier argument (theCheckShape) est la boite de sélection, 
    # le deuxième (theShape) est la géométrie à parcourir
    ids = geompy.GetShapesOnShape(box_sel, shape, shape_type, GEOM.ST_ONIN)
    return ids

# --- A. LES VOLUMES (cellZones) ---

# 1. box_xmin (Mur Gauche)
g_box_xmin = geompy.CreateGroup(Geometry_Finale, geompy.ShapeType["SOLID"])
# Utilisation de la nouvelle fonction
ids_xmin = get_shapes_in_box_coords(Geometry_Finale, 
                                    -EpaisseurBox-eps, -eps, -eps, 
                                    eps, GasCote+eps, GasCote+eps, 
                                    geompy.ShapeType["SOLID"])
geompy.UnionList(g_box_xmin, ids_xmin)
geompy.addToStudyInFather(Geometry_Finale, g_box_xmin, 'box_xmin')

# 2. box_xmax (Mur Droit)
g_box_xmax = geompy.CreateGroup(Geometry_Finale, geompy.ShapeType["SOLID"])
ids_xmax = get_shapes_in_box_coords(Geometry_Finale, 
                                    GasCote-eps, -eps, -eps, 
                                    GasCote+EpaisseurBox+eps, GasCote+eps, GasCote+eps, 
                                    geompy.ShapeType["SOLID"])
geompy.UnionList(g_box_xmax, ids_xmax)
geompy.addToStudyInFather(Geometry_Finale, g_box_xmax, 'box_xmax')

# 3. sphere (Reste inchangé car GetShapesOnSphere accepte encore les arguments)
g_sphere = geompy.CreateGroup(Geometry_Finale, geompy.ShapeType["SOLID"])
ids_sphere = geompy.GetShapesOnSphere(Geometry_Finale, geompy.ShapeType["SOLID"], geompy.MakeVertex(Center, Center, Center), R_sphere, GEOM.ST_ONIN)
geompy.UnionList(g_sphere, ids_sphere)
geompy.addToStudyInFather(Geometry_Finale, g_sphere, 'sphere')

# 4. gas
g_gas = geompy.CreateGroup(Geometry_Finale, geompy.ShapeType["SOLID"])
# On sélectionne tout le cube central
ids_central = get_shapes_in_box_coords(Geometry_Finale, 
                                       -eps, -eps, -eps, 
                                       GasCote+eps, GasCote+eps, GasCote+eps, 
                                       geompy.ShapeType["SOLID"])
# On retire la sphère
ids_gas = list(set(ids_central) - set(ids_sphere))
geompy.UnionList(g_gas, ids_gas)
geompy.addToStudyInFather(Geometry_Finale, g_gas, 'gas')


# --- B. LES INTERFACES (region1_to_region2) ---
# GetShapesOnShape fonctionne toujours normalement

# 1. Interface Gas <-> Sphere
g_int_gas_sphere = geompy.CreateGroup(Geometry_Finale, geompy.ShapeType["FACE"])
ids_int_GS = geompy.GetShapesOnShape(sphere, Geometry_Finale, geompy.ShapeType["FACE"], GEOM.ST_ON)
geompy.UnionList(g_int_gas_sphere, ids_int_GS)
geompy.addToStudyInFather(Geometry_Finale, g_int_gas_sphere, 'gas_to_sphere')

# 2. Interface box_xmin <-> Gas
g_int_xmin_gas = geompy.CreateGroup(Geometry_Finale, geompy.ShapeType["FACE"])
ids_int_XG = geompy.GetShapesOnPlaneWithLocation(Geometry_Finale, geompy.ShapeType["FACE"], geompy.MakeVectorDXDYDZ(1, 0, 0), geompy.MakeVertex(0, 0, 0), GEOM.ST_ON)
geompy.UnionList(g_int_xmin_gas, ids_int_XG)
geompy.addToStudyInFather(Geometry_Finale, g_int_xmin_gas, 'box_xmin_to_gas')

# 3. Interface Gas <-> box_xmax
g_int_xmax_gas = geompy.CreateGroup(Geometry_Finale, geompy.ShapeType["FACE"])
ids_int_GX = geompy.GetShapesOnPlaneWithLocation(Geometry_Finale, geompy.ShapeType["FACE"], geompy.MakeVectorDXDYDZ(1, 0, 0), geompy.MakeVertex(GasCote, 0, 0), GEOM.ST_ON)
geompy.UnionList(g_int_xmax_gas, ids_int_GX)
geompy.addToStudyInFather(Geometry_Finale, g_int_xmax_gas, 'gas_to_box_xmax')


# --- C. LES PAROIS EXTERNES ---

# 1. Extérieur Gauche
g_ext_xmin = geompy.CreateGroup(Geometry_Finale, geompy.ShapeType["FACE"])
ids_ext_xmin = geompy.GetShapesOnPlaneWithLocation(Geometry_Finale, geompy.ShapeType["FACE"], geompy.MakeVectorDXDYDZ(1, 0, 0), geompy.MakeVertex(-EpaisseurBox, 0, 0), GEOM.ST_ON)
geompy.UnionList(g_ext_xmin, ids_ext_xmin)
geompy.addToStudyInFather(Geometry_Finale, g_ext_xmin, 'external_box_xmin')

# 2. Extérieur Droit
g_ext_xmax = geompy.CreateGroup(Geometry_Finale, geompy.ShapeType["FACE"])
ids_ext_xmax = geompy.GetShapesOnPlaneWithLocation(Geometry_Finale, geompy.ShapeType["FACE"], geompy.MakeVectorDXDYDZ(1, 0, 0), geompy.MakeVertex(GasCote+EpaisseurBox, 0, 0), GEOM.ST_ON)
geompy.UnionList(g_ext_xmax, ids_ext_xmax)
geompy.addToStudyInFather(Geometry_Finale, g_ext_xmax, 'external_box_xmax')

# Rafraîchir
if salome.sg.hasDesktop():
    salome.sg.updateObjBrowser()


# =========================================================
# 6. EXPORTATION STL POUR OPENFOAM (snappyHexMesh)
# =========================================================

# 1. Définition du chemin de sortie
# Utilisation du chemin absolu vers le cas OpenFOAM
case_dir = "/home/tanguy/OpenFOAM/tanguy-v2506/run/BouleDansGazAvecBoite"
output_dir = os.path.join(case_dir, "constant", "triSurface")

# Création du dossier s'il n'existe pas
if not os.path.exists(output_dir):
    try:
        os.makedirs(output_dir)
        print("Dossier créé :", output_dir)
    except OSError:
        print("Erreur : Impossible de créer le dossier. Vérifiez les droits ou le chemin.")
else:
    print("Export vers :", output_dir)

# 2. Fonction utilitaire pour exporter
def export_stl(geom_obj, filename):
    """
    Exporte un objet Salome en STL ASCII
    """
    filepath = os.path.join(output_dir, filename)
    # Le 'True' à la fin signifie format ASCII (plus lisible, souvent préféré par OpenFOAM)
    # Le 'False' ferait du Binaire (fichier plus petit)
    geompy.ExportSTL(geom_obj, filepath, True)
    print("  -> Fichier généré : " + filename)

# 3. Export des VOLUMES (Pour les cellZones / Regions)
# C'est ce qui permettra à snappyHexMesh de savoir où est le gaz et où est le solide
print("--- Export des Volumes (Regions) ---")
export_stl(g_gas, "gas.stl")
export_stl(g_sphere, "sphere.stl")
export_stl(g_box_xmin, "box_xmin.stl")
export_stl(g_box_xmax, "box_xmax.stl")

# 4. Export des FACES EXTERNES (Pour les Patches spécifiques)
# Utile pour forcer des conditions limites précises ou des raffinements locaux
print("--- Export des Faces (Patches) ---")
export_stl(g_ext_xmin, "external_box_xmin.stl")
export_stl(g_ext_xmax, "external_box_xmax.stl")

# Note : On n'exporte généralement pas les faces d'interfaces internes (gas_to_sphere)
# en STL séparé pour snappyHexMesh, car snappy les recrée automatiquement 
# là où les volumes gas.stl et sphere.stl se touchent.

print("--- Export terminé avec succès ---")



# geompy.addToStudy(Boite, "Boite")
# geompy.addToStudy(LigneExtrude, "LigneExtrude")
# geompy.addToStudy(SectionAExtruder, "SectionAExtruder")
# geompy.addToStudy(Tube, "Tube")
# geompy.addToStudy(final, "final")

# geompy.addToStudyInFather( final, minXsolid, 'minXsolid' )
# geompy.addToStudyInFather( final, maxXsolid, 'maxXsolid' )
# geompy.addToStudyInFather( final, minYsolid, 'minYsolid' )
# geompy.addToStudyInFather( final, maxYsolid, 'maxYsolid' )
# geompy.addToStudyInFather( final, inletwater, 'inletwater' )
# geompy.addToStudyInFather( final, outletwater, 'outletwater' )
# geompy.addToStudyInFather( final, bottomsolid, 'bottomsolid' )
# geompy.addToStudyInFather( final, topsolid, 'topsolid' )
# geompy.addToStudyInFather( final, water_to_solid_1, 'water_to_solid_1' )
# geompy.addToStudyInFather( final, water_to_solid_2, 'water_to_solid_2' )
# geompy.addToStudyInFather( final, water_to_solid_3, 'water_to_solid_3' )
# geompy.addToStudyInFather( final, water_to_solid, 'water_to_solid' )

###########################################################################################
import os

# =========================================================
# CONFIGURATION AUTOMATIQUE DE BLOCKMESH
# =========================================================

# 1. Paramètres (récupérés de votre script)
# Marge de sécurité pour que le maillage englobe bien tout (ex: 5mm)
# C'est important pour que snappyHexMesh ne crée pas de trous aux bords.
marge = 0.005 

# Rappel des dimensions de votre géométrie :
# X : de -EpaisseurBox à (GasCote + EpaisseurBox)
# Y et Z : de 0 à GasCote

# 2. Calcul des bornes pour le fichier blockMesh
# On injecte la marge ici
val_xMin = -EpaisseurBox - marge
val_xMax = GasCote + EpaisseurBox + marge

val_yMin = 0.0 - marge
val_yMax = GasCote + marge

val_zMin = 0.0 - marge
val_zMax = GasCote + marge

print("--- Bornes du maillage de fond (Background Mesh) ---")
print(f"X : [{val_xMin:.4f}, {val_xMax:.4f}]")
print(f"Y : [{val_yMin:.4f}, {val_yMax:.4f}]")

# 3. Modification du fichier blockMesh_INI
path_ini = os.path.join(case_dir, "Geom_Salome_STLFiles", "Files_INI", "blockMeshDict_INI")

if os.path.exists(path_ini):
    print(f"Configuration de {path_ini} ...")
    
    # A. Remplacer la variable BoiteCote (info)
    sed("BoiteCote XXX", f"BoiteCote {GasCote}", path_ini)

    # B. Remplacer les pas de maillage (lx, ly, lz)
    # ATTENTION : Ici on passe bien la TAILLE (0.005), pas le nombre !
    sed("lx PasMailleX", f"lx {PasMailleX}", path_ini)
    sed("ly PasMailleY", f"ly {PasMailleY}", path_ini)
    sed("lz PasMailleZ", f"lz {PasMailleZ}", path_ini)

    # C. Remplacer les bornes (Min/Max)
    # On remplace nos placeholders MIN_X, MAX_X, etc.
    # Si vous n'avez pas modifié le fichier et gardé "xMin -0.01", 
    # changez "MIN_X" ci-dessous par "xMin -0.01" dans la fonction sed.
    
    sed("MIN_X", f"{val_xMin:.5f}", path_ini)
    sed("MAX_X", f"{val_xMax:.5f}", path_ini)
    
    sed("MIN_Y", f"{val_yMin:.5f}", path_ini)
    sed("MAX_Y", f"{val_yMax:.5f}", path_ini)
    
    sed("MIN_Z", f"{val_zMin:.5f}", path_ini)
    sed("MAX_Z", f"{val_zMax:.5f}", path_ini)

    print("blockMesh_INI mis à jour.")
else:
    print(f"ERREUR : Fichier {path_ini} introuvable.")



###########################################################################################
#  Definition des sondes (PROBES)
#  Objectif : Mesurer le gradient thermique le long de l'axe X (traversant la sphère)
###########################################################################################

# On se place au milieu de la hauteur et de la profondeur pour taper dans la sphère
YProbe = Center
ZProbe = Center

# --- Sonde 1 : Milieu du Gaz coté CHAUD (Entre Mur Gauche et Sphère) ---
# Le mur est à X=0, la sphère commence à (Center - R_sphere)
XProbe = (Center - R_sphere) / 2.0
path_probes = os.path.join(case_dir, "system", "Probes_Solid")
sed("X1 Y1 Z1", str(round(XProbe,4))+" "+str(round(YProbe,4))+" "+str(round(ZProbe,4)), path_probes) 
Probe_1 = geompy.MakeVertex(XProbe, YProbe, ZProbe)
geompy.addToStudy(Probe_1, "Probe_1_Gas_Hot")

# --- Sonde 2 : Interface Entrée Sphère ---
# Juste un tout petit peu à l'intérieur de la sphère pour être sûr
XProbe = Center - R_sphere + 0.001 
sed("X2 Y2 Z2", str(round(XProbe,4))+" "+str(round(YProbe,4))+" "+str(round(ZProbe,4)), path_probes) 
Probe_2 = geompy.MakeVertex(XProbe, YProbe, ZProbe)
geompy.addToStudy(Probe_2, "Probe_2_Interface_In")

# --- Sonde 3 : Cœur de la Sphère (Centre) ---
XProbe = Center
sed("X3 Y3 Z3", str(round(XProbe,4))+" "+str(round(YProbe,4))+" "+str(round(ZProbe,4)), path_probes) 
Probe_3 = geompy.MakeVertex(XProbe, YProbe, ZProbe)
geompy.addToStudy(Probe_3, "Probe_3_Center")

# --- Sonde 4 : Interface Sortie Sphère ---
# Juste un tout petit peu à l'intérieur
XProbe = Center + R_sphere - 0.001
sed("X4 Y4 Z4", str(round(XProbe,4))+" "+str(round(YProbe,4))+" "+str(round(ZProbe,4)), path_probes) 
Probe_4 = geompy.MakeVertex(XProbe, YProbe, ZProbe)
geompy.addToStudy(Probe_4, "Probe_4_Interface_Out")

# --- Sonde 5 : Milieu du Gaz coté FROID (Entre Sphère et Mur Droit) ---
# La sphère finit à (Center + R_sphere), le gaz finit à GasCote
XProbe = (Center + R_sphere) + (GasCote - (Center + R_sphere)) / 2.0
sed("X5 Y5 Z5", str(round(XProbe,4))+" "+str(round(YProbe,4))+" "+str(round(ZProbe,4)), path_probes) 
Probe_5 = geompy.MakeVertex(XProbe, YProbe, ZProbe)
geompy.addToStudy(Probe_5, "Probe_5_Gas_Cold")

# (Optionnel) Une sonde "Témoin" loin de la sphère pour voir la convection libre ?
# Si vous voulez voir si la chaleur monte (Convection), vous pourriez en mettre une en haut du gaz :
# Probe_6 = geompy.MakeVertex(XProbe, GasCote*0.9, Center)
# ###########################################################################################
# #  Defintion de Graph_Centre

# X1 = BoiteCote/2
# Y1 = BoiteCote/2
# Z1 = BoiteCote

# X2 = BoiteCote/2
# Y2 = BoiteCote/2
# Z2 = 0.

# sed("X1 Y1 Z1", str(round(X1,2))+" "+str(round(Y1,2))+" "+str(round(Z1,2)), "./../system/ZGraph_Centre_Solid") 
# sed("X1 Y1 Z1", str(round(X1,2))+" "+str(round(Y1,2))+" "+str(round(Z1,2)), "./../system/ZGraph_Centre_Water") 

# sed("X2 Y2 Z2", str(round(X2,2))+" "+str(round(Y2,2))+" "+str(round(Z2,2)), "./../system/ZGraph_Centre_Solid") 
# sed("X2 Y2 Z2", str(round(X2,2))+" "+str(round(Y2,2))+" "+str(round(Z2,2)), "./../system/ZGraph_Centre_Water") 

# P_1_ZGraph_Centre_Solid = geompy.MakeVertex(X1, Y1, Z1)
# geompy.addToStudy(P_1_ZGraph_Centre_Solid, "P_1_ZGraph_Centre_Solid")
# P_2_ZGraph_Centre_Solid = geompy.MakeVertex(X2, Y2, Z2)
# geompy.addToStudy(P_2_ZGraph_Centre_Solid, "P_2_ZGraph_Centre_Solid")

# Graph_Centre = geompy.MakeLineTwoPnt(P_1_ZGraph_Centre_Solid, P_2_ZGraph_Centre_Solid)
# geompy.addToStudy(Graph_Centre, "Graph_Centre")

# ###########################################################################################
# #  Defintion de Graph_CentreTubeSortie

# X1 = BoiteCote/2 + TubeRayonCourb
# Y1 = BoiteCote/2
# Z1 = BoiteCote

# X2 = BoiteCote/2 + TubeRayonCourb
# Y2 = BoiteCote/2
# Z2 = 0.

# sed("X1 Y1 Z1", str(round(X1,2))+" "+str(round(Y1,2))+" "+str(round(Z1,2)), "./../system/ZGraph_CentreTubeSortie_Solid") 
# sed("X1 Y1 Z1", str(round(X1,2))+" "+str(round(Y1,2))+" "+str(round(Z1,2)), "./../system/ZGraph_CentreTubeSortie_Water") 

# sed("X2 Y2 Z2", str(round(X2,2))+" "+str(round(Y2,2))+" "+str(round(Z2,2)), "./../system/ZGraph_CentreTubeSortie_Solid") 
# sed("X2 Y2 Z2", str(round(X2,2))+" "+str(round(Y2,2))+" "+str(round(Z2,2)), "./../system/ZGraph_CentreTubeSortie_Water") 

# P_1_ZGraph_CentreTube = geompy.MakeVertex(X1, Y1, Z1)
# geompy.addToStudy(P_1_ZGraph_CentreTube, "P_1_ZGraph_CentreTube")
# P_2_ZGraph_CentreTube = geompy.MakeVertex(X2, Y2, Z2)
# geompy.addToStudy(P_2_ZGraph_CentreTube, "P_2_ZGraph_CentreTube")

# Graph_CentreTube = geompy.MakeLineTwoPnt(P_1_ZGraph_CentreTube, P_2_ZGraph_CentreTube)
# geompy.addToStudy(Graph_CentreTube, "Graph_CentreTube")


# ###########################################################################################
# #  Defintion de Graph_CoteSortie_Solid

# X1s = BoiteCote/2 - TubeRayonCourb - TubeD
# Y1 = BoiteCote/2
# Z1 = BoiteCote

# X2s = (BoiteCote/2 - TubeRayonCourb - TubeD/2)/2
# Y2 = BoiteCote/2
# Z2 = 0.

# sed("X1 Y1 Z1", str(round(X1s,2))+" "+str(round(Y1,2))+" "+str(round(Z1,2)), "./../system/ZGraph_CoteSortie_Solid") 

# sed("X2 Y2 Z2", str(round(X2s,2))+" "+str(round(Y2,2))+" "+str(round(Z2,2)), "./../system/ZGraph_CoteSortie_Solid") 


# P_1_ZGraph_CoteSortie = geompy.MakeVertex(X1s, Y1, Z1)
# geompy.addToStudy(P_1_ZGraph_CoteSortie, "P_1_ZGraph_CoteSortie")
# P_2_ZGraph_CoteSortie = geompy.MakeVertex(X2s, Y2, Z2)
# geompy.addToStudy(P_2_ZGraph_CoteSortie, "P_2_ZGraph_CoteSortie")

# Graph_CoteSortie = geompy.MakeLineTwoPnt(P_1_ZGraph_CoteSortie, P_2_ZGraph_CoteSortie)
# geompy.addToStudy(Graph_CoteSortie, "Graph_CoteSortie")


# ###########################################################################################
# #  Defintion de Graph_CoteEntree_Solid

# X1 = BoiteCote - X1s
# Y1 = BoiteCote/2
# Z1 = BoiteCote

# X2 = BoiteCote - X2s
# Y2 = BoiteCote/2
# Z2 = 0.

# sed("X1 Y1 Z1", str(round(X1,2))+" "+str(round(Y1,2))+" "+str(round(Z1,2)), "./../system/ZGraph_CoteEntree_Solid") 

# sed("X2 Y2 Z2", str(round(X2,2))+" "+str(round(Y2,2))+" "+str(round(Z2,2)), "./../system/ZGraph_CoteEntree_Solid") 


# P_1_ZGraph_CoteEntree = geompy.MakeVertex(X1, Y1, Z1)
# geompy.addToStudy(P_1_ZGraph_CoteEntree, "P_1_ZGraph_CoteEntree")
# P_2_ZGraph_CoteEntree = geompy.MakeVertex(X2, Y2, Z2)
# geompy.addToStudy(P_2_ZGraph_CoteEntree, "P_2_ZGraph_CoteEntree")

# Graph_CoteEntree = geompy.MakeLineTwoPnt(P_1_ZGraph_CoteEntree, P_2_ZGraph_CoteEntree)
# geompy.addToStudy(Graph_CoteEntree, "Graph_CoteEntree")


# ###########################################################################################
# #  Defintion des bornes de l'axe abscisses pour le graphique des profils T

# sed("BoiteCote = XXXX", "BoiteCote = " + str(round(BoiteCote,4)), "./../case_treatment/Plot_Graph_CSV.py") 







if salome.sg.hasDesktop():
  salome.sg.updateObjBrowser()

# 8. CONFIGURATION SNAPPYHEXMESH (LocationsInMesh)
# =========================================================
# Il faut donner un point (x,y,z) INSIDE chaque zone pour que snappyHexMesh
# sache comment attribuer les mailles (cellZones).

# A. Calcul des coordonnées
# Sphere : Au centre
loc_sphere_x = Center
loc_sphere_y = Center
loc_sphere_z = Center

# Box XMIN (Mur Gauche) : Au milieu de l'épaisseur du mur
# X entre -Epaisseur et 0
loc_xmin_x = -EpaisseurBox * 0.5 - 0.001  # Légèrement décalé pour éviter les faces de cellules
loc_xmin_y = Center
loc_xmin_z = Center

# Box XMAX (Mur Droit) : Au milieu de l'épaisseur du mur
# X entre GasCote et GasCote+Epaisseur
loc_xmax_x = GasCote + (EpaisseurBox * 0.5) + 0.001  # Légèrement décalé pour éviter les faces de cellules
loc_xmax_y = Center
loc_xmax_z = Center

# Gas : C'est le piège ! Si on prend le centre, on est dans la sphère.
# Il faut un point dans le gaz, mais hors de la sphère.
# On se met "dans le coin" du cube de gaz.
# (Exemple: 10% de la taille de la boite)
loc_gas_x = GasCote * 0.1
loc_gas_y = GasCote * 0.1
loc_gas_z = GasCote * 0.1

print("--- Points de référence (LocationInMesh) ---")
print(f"Sphere : {loc_sphere_x:.4f} {loc_sphere_y:.4f} {loc_sphere_z:.4f}")
print(f"Gas    : {loc_gas_x:.4f} {loc_gas_y:.4f} {loc_gas_z:.4f}")

# B. Remplacement dans snappyHexMeshDict_INI
path_snappy = os.path.join(case_dir, "Geom_Salome_STLFiles", "Files_INI", "snappyHexMeshDict_INI")

if os.path.exists(path_snappy):
    print(f"Mise à jour de {path_snappy} ...")
    
    # Remplacement Sphere
    sed("LOC_X_SPHERE", f"{loc_sphere_x:.5f}", path_snappy)
    sed("LOC_Y_SPHERE", f"{loc_sphere_y:.5f}", path_snappy)
    sed("LOC_Z_SPHERE", f"{loc_sphere_z:.5f}", path_snappy)

    # Remplacement Gas
    sed("LOC_X_GAS", f"{loc_gas_x:.5f}", path_snappy)
    sed("LOC_Y_GAS", f"{loc_gas_y:.5f}", path_snappy)
    sed("LOC_Z_GAS", f"{loc_gas_z:.5f}", path_snappy)
    
    # Remplacement Box Xmin
    sed("LOC_X_XMIN", f"{loc_xmin_x:.5f}", path_snappy)
    sed("LOC_Y_XMIN", f"{loc_xmin_y:.5f}", path_snappy)
    sed("LOC_Z_XMIN", f"{loc_xmin_z:.5f}", path_snappy)

    # Remplacement Box Xmax
    sed("LOC_X_XMAX", f"{loc_xmax_x:.5f}", path_snappy)
    sed("LOC_Y_XMAX", f"{loc_xmax_y:.5f}", path_snappy)
    sed("LOC_Z_XMAX", f"{loc_xmax_z:.5f}", path_snappy)
    
    print("snappyHexMeshDict_INI prêt.")
else:
    print(f"ERREUR : {path_snappy} introuvable.")



print("That's All Folks !")