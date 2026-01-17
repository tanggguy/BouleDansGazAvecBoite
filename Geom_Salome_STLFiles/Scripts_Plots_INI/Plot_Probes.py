# -*-coding:Utf-8 -*
"""
Plot_Probes.py - Visualisation des sondes de température
=========================================================
Lit les données des sondes (Probes_Sphere et Probes_Gas) et trace T(t)

Sortie: postProcessing/Probes_T.png
"""
import sys
import os
import math
from pathlib import Path
from matplotlib import pyplot as plt

##############################################################################
# CONFIGURATION
##############################################################################

# Couleurs pour les différentes sondes
COLORS_SPHERE = ['#E41A1C', '#377EB8', '#4DAF4A']  # Rouge, Bleu, Vert
COLORS_GAS = ['#FF7F00', '#984EA3']  # Orange, Violet

##############################################################################
# FONCTIONS UTILITAIRES
##############################################################################

def read_probe_file(filepath):
    """
    Lit un fichier de sondes OpenFOAM et retourne les données.
    Retourne: (time, data, labels) où data[i] = liste des valeurs pour sonde i
    """
    time = []
    data = []
    labels = []
    
    with open(filepath, 'r') as f:
        lines = f.readlines()
    
    # Trouver le nombre de sondes et leurs labels
    nb_probes = 0
    header_lines = 0
    for line in lines:
        if line.startswith('#'):
            header_lines += 1
            if 'Probe' in line:
                nb_probes += 1
                # Extraire le label (ex: "Probe 0 (0.02 0.05 0.05)")
                label = line.strip()[2:]  # Enlever "# "
                labels.append(label)
        else:
            break
    
    # Initialiser les listes de données
    data = [[] for _ in range(nb_probes)]
    
    # Lire les données
    for line in lines[header_lines:]:
        if line.strip() and not line.startswith('#'):
            values = line.split()
            time.append(float(values[0]))
            for i in range(nb_probes):
                data[i].append(float(values[i + 1]))
    
    return time, data, labels


def find_latest_time_folder(base_path):
    """Trouve le dossier avec le temps le plus récent"""
    folders = [f for f in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, f))]
    numeric_folders = []
    for f in folders:
        try:
            numeric_folders.append(float(f))
        except ValueError:
            pass
    if not numeric_folders:
        return None
    return str(max(numeric_folders))


##############################################################################
# LECTURE DES DONNÉES
##############################################################################

print("=" * 60)
print("Plot_Probes.py - Visualisation des sondes de température")
print("=" * 60)

# Chemins des fichiers de sondes
path_probes_sphere = "postProcessing/Probes_Sphere/sphere"
path_probes_gas = "postProcessing/Probes_Gas/gas"

all_time = []
all_data = []
all_labels = []
all_colors = []

# Lecture des sondes de la sphère
if os.path.exists(path_probes_sphere):
    print(f"\nLecture des sondes sphère: {path_probes_sphere}")
    # Les données peuvent être réparties sur plusieurs dossiers de temps
    time_folders = sorted([f for f in os.listdir(path_probes_sphere) 
                          if os.path.isdir(os.path.join(path_probes_sphere, f))],
                         key=lambda x: float(x) if x.replace('.', '').replace('-', '').isdigit() else 0)
    
    for tf in time_folders:
        probe_file = os.path.join(path_probes_sphere, tf, "T")
        if os.path.exists(probe_file):
            time, data, labels = read_probe_file(probe_file)
            if not all_time:
                all_time = time
                all_data = data
                all_labels = ["Sphere: " + l for l in labels]
                all_colors = COLORS_SPHERE[:len(labels)]
            else:
                # Concaténer les temps
                all_time.extend(time)
                for i in range(len(data)):
                    all_data[i].extend(data[i])
    print(f"  -> {len(all_labels)} sondes trouvées")
else:
    print(f"ATTENTION: Dossier {path_probes_sphere} non trouvé")

# Lecture des sondes du gaz
if os.path.exists(path_probes_gas):
    print(f"\nLecture des sondes gaz: {path_probes_gas}")
    time_folders = sorted([f for f in os.listdir(path_probes_gas) 
                          if os.path.isdir(os.path.join(path_probes_gas, f))],
                         key=lambda x: float(x) if x.replace('.', '').replace('-', '').isdigit() else 0)
    
    gas_time = []
    gas_data = []
    gas_labels = []
    
    for tf in time_folders:
        probe_file = os.path.join(path_probes_gas, tf, "T")
        if os.path.exists(probe_file):
            time, data, labels = read_probe_file(probe_file)
            if not gas_time:
                gas_time = time
                gas_data = data
                gas_labels = ["Gas: " + l for l in labels]
            else:
                gas_time.extend(time)
                for i in range(len(data)):
                    gas_data[i].extend(data[i])
    
    # Ajouter aux données globales
    if gas_data:
        all_data.extend(gas_data)
        all_labels.extend(gas_labels)
        all_colors.extend(COLORS_GAS[:len(gas_labels)])
    print(f"  -> {len(gas_labels)} sondes trouvées")
else:
    print(f"ATTENTION: Dossier {path_probes_gas} non trouvé")

##############################################################################
# TRACÉ DU GRAPHIQUE
##############################################################################

if all_data:
    print(f"\nCréation du graphique...")
    
    plt.figure(figsize=(12, 7))
    
    for i, (data, label, color) in enumerate(zip(all_data, all_labels, all_colors)):
        # Utiliser le temps approprié (sphere ou gas)
        t = all_time if i < len(COLORS_SPHERE) else gas_time
        if len(t) == len(data):
            plt.plot(t, data, c=color, label=label, linewidth=1.5)
        else:
            print(f"  ATTENTION: Longueurs incompatibles pour {label}")
    
    plt.grid(True, which="both", linestyle='--', linewidth=0.5)
    plt.ylabel(r'$T$ (K)', fontsize=12)
    plt.xlabel(r'Temps (s)', fontsize=12)
    plt.legend(bbox_to_anchor=(1.05, 1.0), loc='upper left')
    plt.title("Évolution temporelle de la température aux sondes", loc='center')
    plt.tight_layout()
    
    output_file = 'postProcessing/Probes_T.png'
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"  -> Graphique sauvegardé: {output_file}")
    
    plt.clf()
    plt.close()
else:
    print("\nERREUR: Aucune donnée de sonde trouvée!")

print("\n" + "=" * 60)
print("That's All Folks!")
print("=" * 60)
