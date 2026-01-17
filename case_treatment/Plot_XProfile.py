# -*-coding:Utf-8 -*
"""
Plot_XProfile.py - Profil de température le long de l'axe X
============================================================
Combine les données des 4 régions pour tracer T(X) complet

Sortie: postProcessing/Profile_T_X.png
"""
import sys
import os
import csv
from pathlib import Path
from matplotlib import pyplot as plt
import numpy as np

##############################################################################
# CONFIGURATION
##############################################################################

# Régions et leurs couleurs
REGIONS = {
    'box_xmin': {'color': '#E41A1C', 'label': 'Box Xmin (chaud)', 'marker': 's'},
    'gas': {'color': '#377EB8', 'label': 'Gaz', 'marker': 'o'},
    'sphere': {'color': '#4DAF4A', 'label': 'Sphère', 'marker': '^'},
    'box_xmax': {'color': '#984EA3', 'label': 'Box Xmax (froid)', 'marker': 'd'},
}

# Chemins des profils
PROFILE_PATHS = {
    'box_xmin': 'postProcessing/XGraph_BoxXmin/box_xmin',
    'gas': 'postProcessing/XGraph_Gas/gas',
    'sphere': 'postProcessing/XGraph_Sphere/sphere',
    'box_xmax': 'postProcessing/XGraph_BoxXmax/box_xmax',
}

##############################################################################
# FONCTIONS UTILITAIRES
##############################################################################

def find_latest_time_folder(base_path):
    """Trouve le dossier avec le temps le plus récent"""
    if not os.path.exists(base_path):
        return None
    folders = [f for f in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, f))]
    numeric_folders = []
    for f in folders:
        try:
            numeric_folders.append(float(f))
        except ValueError:
            pass
    if not numeric_folders:
        return None
    return str(int(max(numeric_folders))) if max(numeric_folders) == int(max(numeric_folders)) else str(max(numeric_folders))


def read_csv_profile(filepath):
    """Lit un fichier CSV de profil et retourne (x, T)"""
    x = []
    T = []
    
    with open(filepath, 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        header = next(reader)  # Skip header
        for row in reader:
            if len(row) >= 2:
                x.append(float(row[0]))
                T.append(float(row[1]))
    
    return np.array(x), np.array(T)


##############################################################################
# LECTURE DES DONNÉES
##############################################################################

print("=" * 60)
print("Plot_XProfile.py - Profil de température le long de X")
print("=" * 60)

all_data = {}

for region, path in PROFILE_PATHS.items():
    latest_time = find_latest_time_folder(path)
    
    if latest_time:
        # Chercher le fichier CSV (nom peut varier)
        time_folder = os.path.join(path, latest_time)
        csv_files = [f for f in os.listdir(time_folder) if f.endswith('.csv')]
        
        if csv_files:
            csv_path = os.path.join(time_folder, csv_files[0])
            print(f"\nLecture {region}: {csv_path}")
            try:
                x, T = read_csv_profile(csv_path)
                all_data[region] = {'x': x, 'T': T}
                print(f"  -> {len(x)} points lus, X=[{x.min():.4f}, {x.max():.4f}]")
            except Exception as e:
                print(f"  ERREUR: {e}")
        else:
            print(f"\nATTENTION: Pas de fichier CSV trouvé pour {region}")
    else:
        print(f"\nATTENTION: Dossier {path} non trouvé")

##############################################################################
# TRACÉ DU GRAPHIQUE
##############################################################################

if all_data:
    print(f"\nCréation du graphique...")
    
    fig, ax = plt.subplots(figsize=(14, 7))
    
    # Tracer chaque région
    for region, config in REGIONS.items():
        if region in all_data:
            data = all_data[region]
            ax.plot(data['x'], data['T'], 
                   color=config['color'], 
                   marker=config['marker'],
                   markersize=4,
                   label=config['label'],
                   linewidth=1.5)
    
    # Mise en forme
    ax.set_xlabel(r'Position X (m)', fontsize=12)
    ax.set_ylabel(r'Température T (K)', fontsize=12)
    ax.set_title('Profil de température le long de l\'axe X (Y=Z=Center)', fontsize=14)
    ax.grid(True, linestyle='--', alpha=0.7)
    ax.legend(loc='best', fontsize=10)
    
    # Ajouter des lignes verticales pour les interfaces
    # Ces valeurs seront ajustées par __MAIN__Geom_salome.py
    # ax.axvline(x=0, color='gray', linestyle=':', alpha=0.5, label='Interface box_xmin/gas')
    # ax.axvline(x=GasCote, color='gray', linestyle=':', alpha=0.5, label='Interface gas/box_xmax')
    
    plt.tight_layout()
    
    output_file = 'postProcessing/Profile_T_X.png'
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"  -> Graphique sauvegardé: {output_file}")
    
    plt.clf()
    plt.close()
else:
    print("\nERREUR: Aucune donnée de profil trouvée!")

print("\n" + "=" * 60)
print("That's All Folks!")
print("=" * 60)
