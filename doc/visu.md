# Guide de Visualisation des Résultats

Ce document décrit les différentes méthodes disponibles pour visualiser les résultats de la simulation OpenFOAM.

---

## 1. Visualisation avec ParaView

### 1.1 Lancement de ParaView

La méthode principale pour visualiser les résultats 3D est d'utiliser **ParaView** via la commande `paraFoam`.

```bash
# Depuis le répertoire du cas
paraFoam
```

Cette commande crée automatiquement les fichiers `.OpenFOAM` ou `.foam` nécessaires et lance ParaView.

#### Fichiers de visualisation disponibles

| Fichier | Description |
|---------|-------------|
| `BouleDansGazAvecBoite.foam` | Visualisation du cas complet |
| `BouleDansGazAvecBoite.blockMesh` | Visualisation du maillage de base (blockMesh) |
| `BouleDansGazAvecBoite{gas}.OpenFOAM` | Région fluide (gaz) |
| `BouleDansGazAvecBoite{sphere}.OpenFOAM` | Région solide (sphère) |
| `BouleDansGazAvecBoite{box_xmin}.OpenFOAM` | Région solide (boîte xmin) |
| `BouleDansGazAvecBoite{box_xmax}.OpenFOAM` | Région solide (boîte xmax) |

### 1.2 Commande touchAll

Pour créer tous les fichiers de visualisation sans lancer ParaView :

```bash
paraFoam -touchAll
```

> [!TIP]
> Utilisez `paraFoam -touchAll` dans le script `Allrun` pour préparer les fichiers de visualisation automatiquement après la simulation.

---

## 2. Scripts Python de Post-Traitement

### 2.1 Graphiques des Profils de Température (`Plot_Graph_CSV.py`)

**Emplacement :** `case_treatment/Plot_Graph_CSV.py`

Ce script génère des graphiques de profils de température le long de différentes lignes dans le domaine.

**Fonctionnalités :**
- Lecture des données CSV générées par les function objects `singleGraph`
- Tracé des profils de température (T) en fonction de la position (Z)
- Comparaison des températures entre régions solide et fluide

**Données sources :**
- `postProcessing/ZGraph_Centre_Solid/` - Profil central dans le solide
- `postProcessing/ZGraph_Centre_Water/` - Profil central dans le fluide
- `postProcessing/ZGraph_CentreTubeSortie_Solid/` - Centre tube sortie (solide)
- `postProcessing/ZGraph_CoteSortie_Solid/` - Côté sortie (solide)
- `postProcessing/ZGraph_CoteEntree_Solid/` - Côté entrée (solide)

**Sortie :** `postProcessing/Profils_T.pdf`

**Exécution :**
```bash
python3 case_treatment/Plot_Graph_CSV.py
```

---

### 2.2 Graphiques des Sondes (`Plot_Probes.py`)

**Emplacement :** `case_treatment/Plot_Probes.py`

Ce script trace l'évolution temporelle de la température aux points de sonde définis.

**Fonctionnalités :**
- Lecture des fichiers de sondes depuis `postProcessing/Probes_Solid/`
- Tracé de l'évolution temporelle T(t) pour chaque sonde
- Gestion automatique des légendes avec les coordonnées des sondes

**Sortie :** `postProcessing/Probes_T_degC.pdf`

**Exécution :**
```bash
python3 case_treatment/Plot_Probes.py
```

---

### 2.3 Graphiques des Résidus (`Plot_Residus.py`)

**Emplacement :** `case_treatment/Plot_Residus.py`

Ce script trace l'évolution des résidus de convergence de la simulation.

**Fonctionnalités :**
- Tracé des résidus pour la région solide (h - enthalpie)
- Tracé des résidus pour la région fluide (Ux, Uy, Uz, h, p_rgh)
- Échelle logarithmique pour une meilleure visualisation de la convergence

**Données sources :**
- `postProcessing/solid/solid_residuals/0/solverInfo.dat`
- `postProcessing/water/water_residuals/0/solverInfo.dat`

**Sorties :**
- `postProcessing/residuals_solid_plot.png`
- `postProcessing/residuals_water_plot.png`

**Exécution :**
```bash
python3 case_treatment/Plot_Residus.py
```

---

## 3. Function Objects (Post-Traitement OpenFOAM)

Les function objects sont définis dans `system/controlDict` et s'exécutent pendant ou après la simulation.

### 3.1 Sondes (Probes)

**Fichier de configuration :** `system/Probes_Solid`

Enregistre les valeurs de champs (T) aux points spécifiés dans la région solide.

```cpp
fields (T);
region solid;
writeControl    timeStep;
writeInterval   50;

probeLocations
(
    (X1 Y1 Z1)
    (X2 Y2 Z2)
    ...
);
```

**Sortie :** `postProcessing/Probes_Solid/solid/<time>/T`

---

### 3.2 Graphiques linéaires (singleGraph)

**Fichiers de configuration :** `system/ZGraph_*`

Extrait les valeurs de champs le long d'une ligne définie par un point de départ et un point d'arrivée.

| Fichier | Région | Description |
|---------|--------|-------------|
| `ZGraph_Centre_Solid` | solid | Ligne centrale, région solide |
| `ZGraph_Centre_Water` | water | Ligne centrale, région fluide |
| `ZGraph_CentreTubeSortie_Solid` | solid | Centre tube sortie |
| `ZGraph_CoteSortie_Solid` | solid | Côté sortie |
| `ZGraph_CoteEntree_Solid` | solid | Côté entrée |

**Configuration type :**
```cpp
start   (X1 Y1 Z1);
end     (X2 Y2 Z2);
fields  (T);
region  solid;
setFormat   csv;
```

**Exécution post-simulation :**
```bash
chtMultiRegionFoam -postProcess -func ZGraph_Centre_Solid
```

**Sortie :** `postProcessing/<functionName>/<region>/<time>/line_T.csv`

---

### 3.3 Flux de Chaleur aux Parois (wallHeatFlux)

**Défini dans :** `system/controlDict`

Calcule le flux de chaleur aux interfaces entre régions.

```cpp
HeatFlux_water
{
    type            wallHeatFlux;
    libs            (fieldFunctionObjects);
    patches         (water_to_solid);
    region          water;
    qr              qr;
    executeControl  writeTime;
    writeControl    writeTime;
}
```

---

### 3.4 Valeurs Moyennes sur Surfaces (surfaceFieldValue)

**Fichiers :** `system/T_Average_inlet`, `system/T_Average_outlet`

Calcule la moyenne pondérée par l'aire d'un champ sur un patch.

```cpp
name    inlet;
region  water;
fields  (T);
operation areaAverage;
```

---

### 3.5 Export de Surfaces en VTK

**Fichier :** `system/Surface_outlet_VTK`

Exporte des surfaces (patches, coupes, iso-surfaces) au format VTK pour visualisation externe.

```cpp
fields       (U);
region water;

surfaces
(
    outlet
    {
        $patchSurface;
        patches     (outlet);
    }
);
```

**Exécution post-simulation :**
```bash
chtMultiRegionFoam -postProcess -func Surface_outlet_VTK
```

---

### 3.6 Résidus du Solveur (solverInfo)

**Défini dans :** `system/controlDict`

Enregistre les informations de convergence du solveur.

```cpp
water_residuals
{
    type            solverInfo;
    libs            (utilityFunctionObjects);
    fields          (".*");
    region          water;
}
```

**Sortie :** `postProcessing/<region>/<region>_residuals/0/solverInfo.dat`

---

## 4. Workflow de Visualisation Complet

Le script `Allrun` exécute automatiquement le workflow complet :

```bash
# 1. Simulation
runParallel chtMultiRegionFoam

# 2. Reconstruction du maillage et des champs
runApplication reconstructParMesh -allRegions -constant
runApplication reconstructPar -allRegions

# 3. Post-processing des graphiques
chtMultiRegionFoam -postProcess -func ZGraph_Centre_Water
chtMultiRegionFoam -postProcess -func ZGraph_Centre_Solid
# ... autres function objects

# 4. Génération des plots Python
python3 case_treatment/Plot_Residus.py
python3 case_treatment/Plot_Graph_CSV.py
python3 case_treatment/Plot_Probes.py

# 5. Préparation des fichiers ParaView
paraFoam -touchAll
```

---

## 5. Résumé des Fichiers de Sortie

| Type | Emplacement | Format |
|------|-------------|--------|
| Résidus solide | `postProcessing/residuals_solid_plot.png` | PNG |
| Résidus fluide | `postProcessing/residuals_water_plot.png` | PNG |
| Profils T | `postProcessing/Profils_T.pdf` | PDF |
| Sondes T | `postProcessing/Probes_T_degC.pdf` | PDF |
| Données CSV | `postProcessing/ZGraph_*/.../*.csv` | CSV |
| Données VTK | `postProcessing/Surface_outlet_VTK/.../*.vtk` | VTK |

---

## 6. Commandes Utiles

```bash
# Lancer ParaView avec toutes les régions
paraFoam -touchAll && paraview

# Post-traitement d'une fonction spécifique
chtMultiRegionFoam -postProcess -func <functionName>

# Lancer tous les scripts de visualisation
python3 case_treatment/Plot_Residus.py
python3 case_treatment/Plot_Graph_CSV.py
python3 case_treatment/Plot_Probes.py

# Conversion en VTK pour outils tiers
foamToVTK -allRegions
```
