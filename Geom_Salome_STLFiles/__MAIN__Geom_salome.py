############################################################
# Script to generate STL geometry for OpenFOAM simulation  #
#                                           Jean-Luc Harion#
############################################################

import salome

salome.salome_init()
from salome.geom import geomBuilder

geompy = geomBuilder.New()

import os
import sys

Main_dir = os.getcwd()
Def_Geometrie_dir = os.path.join( Main_dir, 'Parametres')
sys.path.append( Def_Geometrie_dir )


###########################
# Import parameters files #
###########################

# Import .py files which contain parameters #
from importlib import reload

from Parametres_geo_maillage import *
from sed_function import sed

O = geompy.MakeVertex(0, 0, 0)
OX = geompy.MakeVectorDXDYDZ(1, 0, 0)
OY = geompy.MakeVectorDXDYDZ(0, 1, 0)
OZ = geompy.MakeVectorDXDYDZ(0, 0, 1)

Boite = geompy.MakeBoxDXDYDZ(BoiteCote, BoiteCote, BoiteCote)
geomObj_1 = geompy.MakeMarker(0, 0, 0, 1, 0, 0, 0, 1, 0)
sk = geompy.Sketcher2D()
sk.addPoint(0.000000, 0.000000)
sk.addSegmentAbsolute(0.000000, TubeHDroit)
sk.addArcAbsolute(2*TubeRayonCourb, TubeHDroit)
sk.addSegmentAbsolute(2*TubeRayonCourb, 0.000000)
LigneExtrude = sk.wire(geomObj_1)

Cercle = geompy.MakeCircle(None, OY, TubeD/2)
SectionAExtruder = geompy.MakeFaceWires([Cercle], 1)

Tube = geompy.MakePipe(SectionAExtruder, LigneExtrude)

geompy.TranslateDXDYDZ(Tube, DX, 0, DY)

final = geompy.MakePartition([Boite], [Tube], [], [], geompy.ShapeType["SOLID"], 0, [], 0)
[solid,water] = geompy.ExtractShapes(final, geompy.ShapeType["SOLID"], True)
geompy.Rotate(final, OX, 90*math.pi/180.0)
geompy.TranslateDXDYDZ(final, 0, BoiteCote, 0)

[minXsolid,inletwater,water_to_solid_1,minYsolid,bottomsolid,water_to_solid_2,topsolid,maxYsolid,outletwater,water_to_solid_3,maxXsolid] = geompy.ExtractShapes(final, geompy.ShapeType["FACE"], True)

water_to_solid = geompy.MakeFuseList([water_to_solid_1, water_to_solid_2, water_to_solid_3], True, True)


geompy.ExportSTL(minXsolid, "../constant/triSurface/minXsolid.stl", True, 5e-05, True)
sed("solid", "solid minX", "./../constant/triSurface/minXsolid.stl") 

geompy.ExportSTL(maxXsolid, "../constant/triSurface/maxXsolid.stl", True, 5e-05, True)
sed("solid", "solid maxX", "./../constant/triSurface/maxXsolid.stl") 

geompy.ExportSTL(minYsolid, "../constant/triSurface/minYsolid.stl", True, 5e-05, True)
sed("solid", "solid minY", "./../constant/triSurface/minYsolid.stl") 

geompy.ExportSTL(maxYsolid, "../constant/triSurface/maxYsolid.stl", True, 5e-05, True)
sed("solid", "solid maxY", "./../constant/triSurface/maxYsolid.stl") 

geompy.ExportSTL(inletwater, "../constant/triSurface/inletwater.stl", True, 5e-05, True)
sed("solid", "solid inlet", "./../constant/triSurface/inletwater.stl") 

geompy.ExportSTL(outletwater, "../constant/triSurface/outletwater.stl", True, 5e-05, True)
sed("solid", "solid outlet", "./../constant/triSurface/outletwater.stl") 

geompy.ExportSTL(bottomsolid, "../constant/triSurface/bottomsolid.stl", True, 5e-05, True)
sed("solid", "solid bottom", "./../constant/triSurface/bottomsolid.stl") 

geompy.ExportSTL(topsolid, "../constant/triSurface/topsolid.stl", True, 5e-05, True)
sed("solid", "solid top", "./../constant/triSurface/topsolid.stl") 

geompy.ExportSTL(water_to_solid, "../constant/triSurface/water_to_solid.stl", True, 5e-05, True)
sed("solid", "solid water_to_solid", "./../constant/triSurface/water_to_solid.stl") 



geompy.addToStudy(Boite, "Boite")
geompy.addToStudy(LigneExtrude, "LigneExtrude")
geompy.addToStudy(SectionAExtruder, "SectionAExtruder")
geompy.addToStudy(Tube, "Tube")
geompy.addToStudy(final, "final")

geompy.addToStudyInFather( final, minXsolid, 'minXsolid' )
geompy.addToStudyInFather( final, maxXsolid, 'maxXsolid' )
geompy.addToStudyInFather( final, minYsolid, 'minYsolid' )
geompy.addToStudyInFather( final, maxYsolid, 'maxYsolid' )
geompy.addToStudyInFather( final, inletwater, 'inletwater' )
geompy.addToStudyInFather( final, outletwater, 'outletwater' )
geompy.addToStudyInFather( final, bottomsolid, 'bottomsolid' )
geompy.addToStudyInFather( final, topsolid, 'topsolid' )
geompy.addToStudyInFather( final, water_to_solid_1, 'water_to_solid_1' )
geompy.addToStudyInFather( final, water_to_solid_2, 'water_to_solid_2' )
geompy.addToStudyInFather( final, water_to_solid_3, 'water_to_solid_3' )
geompy.addToStudyInFather( final, water_to_solid, 'water_to_solid' )

###########################################################################################
#  Ajustement des dimensions et Maillage dans blockMesh

sed("BoiteCote XXX", "BoiteCote " + str(round(BoiteCote,4)), "./../system/blockMeshDict") 

sed("lx PasMailleX", "lx " + str(round(PasMailleX,6)), "./../system/blockMeshDict") 
sed("ly PasMailleY", "ly " + str(round(PasMailleY,6)), "./../system/blockMeshDict") 
sed("lz PasMailleZ", "lz " + str(round(PasMailleZ,6)), "./../system/blockMeshDict") 



###########################################################################################
#  Defintion des sondes

XProbe = (BoiteCote/2 - TubeRayonCourb - TubeD/2)/2
YProbe = BoiteCote/2


ZProbe = 0.9 * BoiteCote
sed("X1 Y1 Z1", str(round(XProbe,2))+" "+str(round(YProbe,2))+" "+str(round(ZProbe,2)), "./../system/Probes_Solid") 
Probe_1 = geompy.MakeVertex(XProbe, YProbe, ZProbe)
geompy.addToStudy(Probe_1, "Probe_1")

ZProbe = 0.7 * BoiteCote
sed("X2 Y2 Z2", str(round(XProbe,2))+" "+str(round(YProbe,2))+" "+str(round(ZProbe,2)), "./../system/Probes_Solid") 
Probe_2 = geompy.MakeVertex(XProbe, YProbe, ZProbe)
geompy.addToStudy(Probe_2, "Probe_2")

ZProbe = 0.5 * BoiteCote
sed("X3 Y3 Z3", str(round(XProbe,2))+" "+str(round(YProbe,2))+" "+str(round(ZProbe,2)), "./../system/Probes_Solid") 
Probe_3 = geompy.MakeVertex(XProbe, YProbe, ZProbe)
geompy.addToStudy(Probe_3, "Probe_3")

ZProbe = 0.3 * BoiteCote
sed("X4 Y4 Z4", str(round(XProbe,2))+" "+str(round(YProbe,2))+" "+str(round(ZProbe,2)), "./../system/Probes_Solid") 
Probe_4 = geompy.MakeVertex(XProbe, YProbe, ZProbe)
geompy.addToStudy(Probe_4, "Probe_4")

ZProbe = 0.1 * BoiteCote
sed("X5 Y5 Z5", str(round(XProbe,2))+" "+str(round(YProbe,2))+" "+str(round(ZProbe,2)), "./../system/Probes_Solid") 
Probe_5 = geompy.MakeVertex(XProbe, YProbe, ZProbe)
geompy.addToStudy(Probe_5, "Probe_5")

###########################################################################################
#  Defintion de Graph_Centre

X1 = BoiteCote/2
Y1 = BoiteCote/2
Z1 = BoiteCote

X2 = BoiteCote/2
Y2 = BoiteCote/2
Z2 = 0.

sed("X1 Y1 Z1", str(round(X1,2))+" "+str(round(Y1,2))+" "+str(round(Z1,2)), "./../system/ZGraph_Centre_Solid") 
sed("X1 Y1 Z1", str(round(X1,2))+" "+str(round(Y1,2))+" "+str(round(Z1,2)), "./../system/ZGraph_Centre_Water") 

sed("X2 Y2 Z2", str(round(X2,2))+" "+str(round(Y2,2))+" "+str(round(Z2,2)), "./../system/ZGraph_Centre_Solid") 
sed("X2 Y2 Z2", str(round(X2,2))+" "+str(round(Y2,2))+" "+str(round(Z2,2)), "./../system/ZGraph_Centre_Water") 

P_1_ZGraph_Centre_Solid = geompy.MakeVertex(X1, Y1, Z1)
geompy.addToStudy(P_1_ZGraph_Centre_Solid, "P_1_ZGraph_Centre_Solid")
P_2_ZGraph_Centre_Solid = geompy.MakeVertex(X2, Y2, Z2)
geompy.addToStudy(P_2_ZGraph_Centre_Solid, "P_2_ZGraph_Centre_Solid")

Graph_Centre = geompy.MakeLineTwoPnt(P_1_ZGraph_Centre_Solid, P_2_ZGraph_Centre_Solid)
geompy.addToStudy(Graph_Centre, "Graph_Centre")

###########################################################################################
#  Defintion de Graph_CentreTubeSortie

X1 = BoiteCote/2 + TubeRayonCourb
Y1 = BoiteCote/2
Z1 = BoiteCote

X2 = BoiteCote/2 + TubeRayonCourb
Y2 = BoiteCote/2
Z2 = 0.

sed("X1 Y1 Z1", str(round(X1,2))+" "+str(round(Y1,2))+" "+str(round(Z1,2)), "./../system/ZGraph_CentreTubeSortie_Solid") 
sed("X1 Y1 Z1", str(round(X1,2))+" "+str(round(Y1,2))+" "+str(round(Z1,2)), "./../system/ZGraph_CentreTubeSortie_Water") 

sed("X2 Y2 Z2", str(round(X2,2))+" "+str(round(Y2,2))+" "+str(round(Z2,2)), "./../system/ZGraph_CentreTubeSortie_Solid") 
sed("X2 Y2 Z2", str(round(X2,2))+" "+str(round(Y2,2))+" "+str(round(Z2,2)), "./../system/ZGraph_CentreTubeSortie_Water") 

P_1_ZGraph_CentreTube = geompy.MakeVertex(X1, Y1, Z1)
geompy.addToStudy(P_1_ZGraph_CentreTube, "P_1_ZGraph_CentreTube")
P_2_ZGraph_CentreTube = geompy.MakeVertex(X2, Y2, Z2)
geompy.addToStudy(P_2_ZGraph_CentreTube, "P_2_ZGraph_CentreTube")

Graph_CentreTube = geompy.MakeLineTwoPnt(P_1_ZGraph_CentreTube, P_2_ZGraph_CentreTube)
geompy.addToStudy(Graph_CentreTube, "Graph_CentreTube")


###########################################################################################
#  Defintion de Graph_CoteSortie_Solid

X1s = BoiteCote/2 - TubeRayonCourb - TubeD
Y1 = BoiteCote/2
Z1 = BoiteCote

X2s = (BoiteCote/2 - TubeRayonCourb - TubeD/2)/2
Y2 = BoiteCote/2
Z2 = 0.

sed("X1 Y1 Z1", str(round(X1s,2))+" "+str(round(Y1,2))+" "+str(round(Z1,2)), "./../system/ZGraph_CoteSortie_Solid") 

sed("X2 Y2 Z2", str(round(X2s,2))+" "+str(round(Y2,2))+" "+str(round(Z2,2)), "./../system/ZGraph_CoteSortie_Solid") 


P_1_ZGraph_CoteSortie = geompy.MakeVertex(X1s, Y1, Z1)
geompy.addToStudy(P_1_ZGraph_CoteSortie, "P_1_ZGraph_CoteSortie")
P_2_ZGraph_CoteSortie = geompy.MakeVertex(X2s, Y2, Z2)
geompy.addToStudy(P_2_ZGraph_CoteSortie, "P_2_ZGraph_CoteSortie")

Graph_CoteSortie = geompy.MakeLineTwoPnt(P_1_ZGraph_CoteSortie, P_2_ZGraph_CoteSortie)
geompy.addToStudy(Graph_CoteSortie, "Graph_CoteSortie")


###########################################################################################
#  Defintion de Graph_CoteEntree_Solid

X1 = BoiteCote - X1s
Y1 = BoiteCote/2
Z1 = BoiteCote

X2 = BoiteCote - X2s
Y2 = BoiteCote/2
Z2 = 0.

sed("X1 Y1 Z1", str(round(X1,2))+" "+str(round(Y1,2))+" "+str(round(Z1,2)), "./../system/ZGraph_CoteEntree_Solid") 

sed("X2 Y2 Z2", str(round(X2,2))+" "+str(round(Y2,2))+" "+str(round(Z2,2)), "./../system/ZGraph_CoteEntree_Solid") 


P_1_ZGraph_CoteEntree = geompy.MakeVertex(X1, Y1, Z1)
geompy.addToStudy(P_1_ZGraph_CoteEntree, "P_1_ZGraph_CoteEntree")
P_2_ZGraph_CoteEntree = geompy.MakeVertex(X2, Y2, Z2)
geompy.addToStudy(P_2_ZGraph_CoteEntree, "P_2_ZGraph_CoteEntree")

Graph_CoteEntree = geompy.MakeLineTwoPnt(P_1_ZGraph_CoteEntree, P_2_ZGraph_CoteEntree)
geompy.addToStudy(Graph_CoteEntree, "Graph_CoteEntree")


###########################################################################################
#  Defintion des bornes de l'axe abscisses pour le graphique des profils T

sed("BoiteCote = XXXX", "BoiteCote = " + str(round(BoiteCote,4)), "./../case_treatment/Plot_Graph_CSV.py") 


print("That's All Folks !")





if salome.sg.hasDesktop():
  salome.sg.updateObjBrowser()

