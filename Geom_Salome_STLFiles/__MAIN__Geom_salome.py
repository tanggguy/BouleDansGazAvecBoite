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

# --- D. FACES INTERNES DES BOXES (pour éviter le chevauchement avec les faces externes) ---
# Ces groupes contiennent toutes les faces des boxes SAUF les faces externes
# C'est nécessaire car sinon box_xmin.stl et external_box_xmin.stl contiennent les mêmes triangles
# IMPORTANT: On doit comparer les IDs des shapes, pas les objets GEOM eux-mêmes

# 1. Faces internes de box_xmin (toutes les faces sauf external_box_xmin)
# On récupère d'abord toutes les faces du volume box_xmin
all_faces_box_xmin = geompy.GetShapesOnShape(box_xmin, Geometry_Finale, geompy.ShapeType["FACE"], GEOM.ST_ONIN)
# On récupère les IDs des faces externes pour pouvoir les comparer
ids_ext_xmin_set = set(geompy.GetSubShapeID(Geometry_Finale, f) for f in ids_ext_xmin)
# On filtre les faces internes en comparant les IDs
ids_internal_xmin = [f for f in all_faces_box_xmin if geompy.GetSubShapeID(Geometry_Finale, f) not in ids_ext_xmin_set]
g_box_xmin_faces = geompy.CreateGroup(Geometry_Finale, geompy.ShapeType["FACE"])
geompy.UnionList(g_box_xmin_faces, ids_internal_xmin)
geompy.addToStudyInFather(Geometry_Finale, g_box_xmin_faces, 'box_xmin_faces')

# 2. Faces internes de box_xmax (toutes les faces sauf external_box_xmax)
all_faces_box_xmax = geompy.GetShapesOnShape(box_xmax, Geometry_Finale, geompy.ShapeType["FACE"], GEOM.ST_ONIN)
ids_ext_xmax_set = set(geompy.GetSubShapeID(Geometry_Finale, f) for f in ids_ext_xmax)
ids_internal_xmax = [f for f in all_faces_box_xmax if geompy.GetSubShapeID(Geometry_Finale, f) not in ids_ext_xmax_set]
g_box_xmax_faces = geompy.CreateGroup(Geometry_Finale, geompy.ShapeType["FACE"])
geompy.UnionList(g_box_xmax_faces, ids_internal_xmax)
geompy.addToStudyInFather(Geometry_Finale, g_box_xmax_faces, 'box_xmax_faces')

print(f"box_xmin: {len(all_faces_box_xmin)} faces totales, {len(ids_internal_xmin)} faces internes exportées (excluant {len(ids_ext_xmin)} face(s) externe(s))")
print(f"box_xmax: {len(all_faces_box_xmax)} faces totales, {len(ids_internal_xmax)} faces internes exportées (excluant {len(ids_ext_xmax)} face(s) externe(s))")

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

# IMPORTANT: On exporte les FACES internes des boxes (pas les volumes entiers)
# Cela évite que box_xmin.stl contienne les mêmes faces que external_box_xmin.stl
print("--- Export des Faces des Boxes (sans les faces externes) ---")
export_stl(g_box_xmin_faces, "box_xmin.stl")  # Faces internes uniquement
export_stl(g_box_xmax_faces, "box_xmax.stl")  # Faces internes uniquement

# 4. Export des FACES EXTERNES (Pour les Patches spécifiques)
# Ces faces sont exportées séparément pour avoir des conditions limites précises
print("--- Export des Faces Externes (Conditions aux limites) ---")
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
#  CONFIGURATION DU POST-TRAITEMENT
#  Copie et paramétrage des fichiers templates pour:
#  - Sondes (Probes) dans sphere et gas
#  - Profils de température le long de X (XGraph)
#  - Coupes 2D (Slices)
#  - Scripts Python de visualisation
###########################################################################################

import shutil

# Dossiers sources (templates)
graph_probes_ini = os.path.join(case_dir, "Geom_Salome_STLFiles", "Graph_et_Probes_INI")
scripts_ini = os.path.join(case_dir, "Geom_Salome_STLFiles", "Scripts_Plots_INI")

# Dossiers destinations
system_dir = os.path.join(case_dir, "system")
case_treatment_dir = os.path.join(case_dir, "case_treatment")

# Créer case_treatment s'il n'existe pas
if not os.path.exists(case_treatment_dir):
    os.makedirs(case_treatment_dir)

print("\\n" + "="*70)
print("CONFIGURATION DU POST-TRAITEMENT")
print("="*70)

# =========================================================================
# 1. SONDES DE TEMPERATURE (PROBES)
# =========================================================================
print("\\n--- 1. Configuration des Sondes (Probes) ---")

# Coordonnées Y et Z (centre de la géométrie)
YProbe = Center
ZProbe = Center

# --- Sondes dans la SPHERE (3 points) ---
# Sonde 1: Interface entrée (côté chaud)
X_probe_sphere_1 = Center - R_sphere + 0.001
# Sonde 2: Centre de la sphère
X_probe_sphere_2 = Center
# Sonde 3: Interface sortie (côté froid)
X_probe_sphere_3 = Center + R_sphere - 0.001

path_probes_sphere_ini = os.path.join(graph_probes_ini, "Probes_Sphere")
path_probes_sphere = os.path.join(system_dir, "Probes_Sphere")
shutil.copy(path_probes_sphere_ini, path_probes_sphere)

sed("X_PROBE_SPHERE_1", f"{X_probe_sphere_1:.5f}", path_probes_sphere)
sed("X_PROBE_SPHERE_2", f"{X_probe_sphere_2:.5f}", path_probes_sphere)
sed("X_PROBE_SPHERE_3", f"{X_probe_sphere_3:.5f}", path_probes_sphere)
sed("Y_PROBE_SPHERE", f"{YProbe:.5f}", path_probes_sphere)
sed("Z_PROBE_SPHERE", f"{ZProbe:.5f}", path_probes_sphere)
print(f"  -> Probes_Sphere: 3 sondes configurées")

# Visualisation dans Salome
Probe_Sphere_1 = geompy.MakeVertex(X_probe_sphere_1, YProbe, ZProbe)
geompy.addToStudy(Probe_Sphere_1, "Probe_Sphere_1_In")
Probe_Sphere_2 = geompy.MakeVertex(X_probe_sphere_2, YProbe, ZProbe)
geompy.addToStudy(Probe_Sphere_2, "Probe_Sphere_2_Center")
Probe_Sphere_3 = geompy.MakeVertex(X_probe_sphere_3, YProbe, ZProbe)
geompy.addToStudy(Probe_Sphere_3, "Probe_Sphere_3_Out")

# --- Sondes dans le GAZ (2 points) ---
# Sonde 1: Milieu du gaz côté chaud (entre box_xmin et sphère)
X_probe_gas_1 = (Center - R_sphere) / 2.0
# Sonde 2: Milieu du gaz côté froid (entre sphère et box_xmax)
X_probe_gas_2 = (Center + R_sphere) + (GasCote - (Center + R_sphere)) / 2.0

path_probes_gas_ini = os.path.join(graph_probes_ini, "Probes_Gas")
path_probes_gas = os.path.join(system_dir, "Probes_Gas")
shutil.copy(path_probes_gas_ini, path_probes_gas)

sed("X_PROBE_GAS_1", f"{X_probe_gas_1:.5f}", path_probes_gas)
sed("X_PROBE_GAS_2", f"{X_probe_gas_2:.5f}", path_probes_gas)
sed("Y_PROBE_GAS", f"{YProbe:.5f}", path_probes_gas)
sed("Z_PROBE_GAS", f"{ZProbe:.5f}", path_probes_gas)
print(f"  -> Probes_Gas: 2 sondes configurées")

# Visualisation dans Salome
Probe_Gas_1 = geompy.MakeVertex(X_probe_gas_1, YProbe, ZProbe)
geompy.addToStudy(Probe_Gas_1, "Probe_Gas_1_Hot")
Probe_Gas_2 = geompy.MakeVertex(X_probe_gas_2, YProbe, ZProbe)
geompy.addToStudy(Probe_Gas_2, "Probe_Gas_2_Cold")

# =========================================================================
# 2. PROFILS DE TEMPERATURE LE LONG DE X (XGraph)
# =========================================================================
print("\\n--- 2. Configuration des Profils T(X) ---")

# Coordonnées Y et Z du profil (centre)
Y_CENTER = Center
Z_CENTER = Center

# --- Profil dans BOX_XMIN ---
X_start_boxxmin = -EpaisseurBox + 0.0001
X_end_boxxmin = -0.0001

path_xgraph_boxxmin_ini = os.path.join(graph_probes_ini, "XGraph_BoxXmin")
path_xgraph_boxxmin = os.path.join(system_dir, "XGraph_BoxXmin")
shutil.copy(path_xgraph_boxxmin_ini, path_xgraph_boxxmin)

sed("X_START_BOXXMIN", f"{X_start_boxxmin:.5f}", path_xgraph_boxxmin)
sed("X_END_BOXXMIN", f"{X_end_boxxmin:.5f}", path_xgraph_boxxmin)
sed("Y_CENTER", f"{Y_CENTER:.5f}", path_xgraph_boxxmin)
sed("Z_CENTER", f"{Z_CENTER:.5f}", path_xgraph_boxxmin)
print(f"  -> XGraph_BoxXmin: X=[{X_start_boxxmin:.4f}, {X_end_boxxmin:.4f}]")

# --- Profil dans GAS ---
X_start_gas = 0.0001
X_end_gas = GasCote - 0.0001

path_xgraph_gas_ini = os.path.join(graph_probes_ini, "XGraph_Gas")
path_xgraph_gas = os.path.join(system_dir, "XGraph_Gas")
shutil.copy(path_xgraph_gas_ini, path_xgraph_gas)

sed("X_START_GAS", f"{X_start_gas:.5f}", path_xgraph_gas)
sed("X_END_GAS", f"{X_end_gas:.5f}", path_xgraph_gas)
sed("Y_CENTER", f"{Y_CENTER:.5f}", path_xgraph_gas)
sed("Z_CENTER", f"{Z_CENTER:.5f}", path_xgraph_gas)
print(f"  -> XGraph_Gas: X=[{X_start_gas:.4f}, {X_end_gas:.4f}]")

# --- Profil dans SPHERE ---
X_start_sphere = Center - R_sphere + 0.0001
X_end_sphere = Center + R_sphere - 0.0001

path_xgraph_sphere_ini = os.path.join(graph_probes_ini, "XGraph_Sphere")
path_xgraph_sphere = os.path.join(system_dir, "XGraph_Sphere")
shutil.copy(path_xgraph_sphere_ini, path_xgraph_sphere)

sed("X_START_SPHERE", f"{X_start_sphere:.5f}", path_xgraph_sphere)
sed("X_END_SPHERE", f"{X_end_sphere:.5f}", path_xgraph_sphere)
sed("Y_CENTER", f"{Y_CENTER:.5f}", path_xgraph_sphere)
sed("Z_CENTER", f"{Z_CENTER:.5f}", path_xgraph_sphere)
print(f"  -> XGraph_Sphere: X=[{X_start_sphere:.4f}, {X_end_sphere:.4f}]")

# --- Profil dans BOX_XMAX ---
X_start_boxxmax = GasCote + 0.0001
X_end_boxxmax = GasCote + EpaisseurBox - 0.0001

path_xgraph_boxxmax_ini = os.path.join(graph_probes_ini, "XGraph_BoxXmax")
path_xgraph_boxxmax = os.path.join(system_dir, "XGraph_BoxXmax")
shutil.copy(path_xgraph_boxxmax_ini, path_xgraph_boxxmax)

sed("X_START_BOXXMAX", f"{X_start_boxxmax:.5f}", path_xgraph_boxxmax)
sed("X_END_BOXXMAX", f"{X_end_boxxmax:.5f}", path_xgraph_boxxmax)
sed("Y_CENTER", f"{Y_CENTER:.5f}", path_xgraph_boxxmax)
sed("Z_CENTER", f"{Z_CENTER:.5f}", path_xgraph_boxxmax)
print(f"  -> XGraph_BoxXmax: X=[{X_start_boxxmax:.4f}, {X_end_boxxmax:.4f}]")

# Visualiser le profil dans Salome
P_start = geompy.MakeVertex(-EpaisseurBox, Y_CENTER, Z_CENTER)
P_end = geompy.MakeVertex(GasCote + EpaisseurBox, Y_CENTER, Z_CENTER)
XProfile_Line = geompy.MakeLineTwoPnt(P_start, P_end)
geompy.addToStudy(XProfile_Line, "XProfile_Line")

# =========================================================================
# 3. COUPES 2D (SLICES)
# =========================================================================
print("\\n--- 3. Configuration des Coupes 2D (Slices) ---")

# Slice Y = Center (pour la région gas uniquement)
path_slice_y_ini = os.path.join(graph_probes_ini, "Slice_YCenter")
path_slice_y = os.path.join(system_dir, "Slice_YCenter_Gas")
shutil.copy(path_slice_y_ini, path_slice_y)

sed("REGION_NAME", "gas", path_slice_y)
sed("Y_CENTER", f"{Y_CENTER:.5f}", path_slice_y)
print(f"  -> Slice_YCenter_Gas: Y={Y_CENTER:.4f}")

# Slice Z = Center (pour la région gas uniquement)
path_slice_z_ini = os.path.join(graph_probes_ini, "Slice_ZCenter")
path_slice_z = os.path.join(system_dir, "Slice_ZCenter_Gas")
shutil.copy(path_slice_z_ini, path_slice_z)

sed("REGION_NAME", "gas", path_slice_z)
sed("Z_CENTER", f"{Z_CENTER:.5f}", path_slice_z)
print(f"  -> Slice_ZCenter_Gas: Z={Z_CENTER:.4f}")

# =========================================================================
# 4. COPIE DES SCRIPTS PYTHON
# =========================================================================
print("\\n--- 4. Copie des Scripts Python de Visualisation ---")

scripts_to_copy = ["Plot_Probes.py", "Plot_XProfile.py", "Plot_HeatFlux.py", "Plot_Residus.py"]

for script in scripts_to_copy:
    src = os.path.join(scripts_ini, script)
    dst = os.path.join(case_treatment_dir, script)
    if os.path.exists(src):
        shutil.copy(src, dst)
        print(f"  -> {script} copié vers case_treatment/")
    else:
        print(f"  ATTENTION: {script} non trouvé dans Scripts_Plots_INI/")

print("\\n" + "="*70)
print("POST-TRAITEMENT CONFIGURÉ AVEC SUCCÈS")
print("="*70) 







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