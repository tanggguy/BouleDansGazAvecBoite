# -*-coding:Utf-8 -*
"""
Plot_Residus.py - Visualisation des résidus multi-régions
==========================================================
Lit les résidus des 4 régions (gas, sphere, box_xmin, box_xmax)

Sortie: postProcessing/Residuals_*.png (un par région)
"""
import sys
import os
from pathlib import Path
from matplotlib import pyplot as plt
import numpy as np

##############################################################################
# CONFIGURATION
##############################################################################

# Régions et leurs configurations
REGIONS = {
    'gas': {
        'path': 'postProcessing/gas/gas_residuals',
        'title': 'Résidus - Région Gas (fluide)',
        'fields': ['Ux', 'Uy', 'Uz', 'h', 'p_rgh'],  # Champs attendus pour un fluide
        'solid': False
    },
    'sphere': {
        'path': 'postProcessing/sphere/sphere_residuals',
        'title': 'Résidus - Région Sphere (solide)',
        'fields': ['h'],  # Champs attendus pour un solide
        'solid': True
    },
    'box_xmin': {
        'path': 'postProcessing/box_xmin/box_xmin_residuals',
        'title': 'Résidus - Région Box Xmin (solide)',
        'fields': ['h'],
        'solid': True
    },
    'box_xmax': {
        'path': 'postProcessing/box_xmax/box_xmax_residuals',
        'title': 'Résidus - Région Box Xmax (solide)',
        'fields': ['h'],
        'solid': True
    },
}

COLORS = ['b', 'g', 'r', 'c', 'm', 'y', 'k', 'orange', 'purple', 'brown']

##############################################################################
# FONCTIONS UTILITAIRES
##############################################################################

def read_solver_info(base_path):
    """
    Lit les fichiers solverInfo.dat d'OpenFOAM.
    Retourne: dict avec time et les résidus de chaque champ
    """
    data = {'time': []}
    
    if not os.path.exists(base_path):
        return None
    
    # Trouver le dossier 0 (ou le premier dossier temps)
    time_folders = sorted([f for f in os.listdir(base_path) 
                          if os.path.isdir(os.path.join(base_path, f))],
                         key=lambda x: float(x) if x.replace('.', '').replace('-', '').isdigit() else 0)
    
    for tf in time_folders:
        solver_file = os.path.join(base_path, tf, "solverInfo.dat")
        if os.path.exists(solver_file):
            with open(solver_file, 'r') as f:
                header = None
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    
                    # Ligne de header avec les noms de colonnes
                    if line.startswith('# Time'):
                        # Parser le header pour obtenir les noms de champs
                        header = line[2:].split()  # Enlever "# "
                        for col in header[1:]:  # Skip 'Time'
                            if col not in data:
                                data[col] = []
                        continue
                    
                    if line.startswith('#'):
                        continue
                    
                    values = line.split()
                    if len(values) >= 2:
                        data['time'].append(float(values[0]))
                        # Remplir les colonnes
                        if header:
                            for i, col in enumerate(header[1:], 1):
                                if i < len(values) and col in data:
                                    try:
                                        data[col].append(float(values[i]))
                                    except ValueError:
                                        data[col].append(0)
    
    # Convertir en arrays numpy
    for key in data:
        data[key] = np.array(data[key])
    
    return data if len(data['time']) > 0 else None


##############################################################################
# LECTURE ET TRACÉ DES RÉSIDUS
##############################################################################

print("=" * 60)
print("Plot_Residus.py - Visualisation des résidus multi-régions")
print("=" * 60)

os.makedirs('postProcessing', exist_ok=True)

for region_name, config in REGIONS.items():
    print(f"\n--- Région: {region_name} ---")
    print(f"Chemin: {config['path']}")
    
    data = read_solver_info(config['path'])
    
    if data is None:
        print(f"  -> Aucune donnée trouvée")
        continue
    
    print(f"  -> {len(data['time'])} pas de temps lus")
    
    # Créer le graphique
    fig, ax = plt.subplots(figsize=(10, 6))
    
    color_idx = 0
    plotted = False
    
    # Chercher les colonnes de résidus finaux
    for col in data:
        if col == 'time':
            continue
        # On cherche les résidus finaux (colonnes se terminant souvent par _0 ou similaire)
        if 'initial' in col.lower():
            continue  # Skip les résidus initiaux
        if len(data[col]) == len(data['time']) and len(data[col]) > 0:
            ax.plot(data['time'], data[col], 
                   c=COLORS[color_idx % len(COLORS)],
                   label=col,
                   linewidth=1.0)
            color_idx += 1
            plotted = True
    
    if plotted:
        ax.set_yscale('log')
        ax.grid(True, which="both", linestyle='--', linewidth=0.5)
        ax.set_ylabel(r'Résidus', fontsize=12)
        ax.set_xlabel(r'Temps (s)', fontsize=12)
        ax.legend(bbox_to_anchor=(1.05, 1.0), loc='upper left', fontsize=8)
        ax.set_title(config['title'], fontsize=14)
        
        plt.tight_layout()
        
        output_file = f'postProcessing/Residuals_{region_name}.png'
        plt.savefig(output_file, dpi=150, bbox_inches='tight')
        print(f"  -> Graphique sauvegardé: {output_file}")
    else:
        print(f"  -> Aucune donnée à tracer")
    
    plt.clf()
    plt.close()

##############################################################################
# GRAPHIQUE COMBINÉ (tous les résidus h)
##############################################################################

print("\n--- Création du graphique combiné (résidus h) ---")

fig, ax = plt.subplots(figsize=(12, 7))
regions_plotted = []

for i, (region_name, config) in enumerate(REGIONS.items()):
    data = read_solver_info(config['path'])
    if data is None:
        continue
    
    # Chercher le résidu h final
    for col in data:
        if 'h' in col.lower() and 'initial' not in col.lower():
            if len(data[col]) == len(data['time']):
                ax.plot(data['time'], data[col],
                       c=COLORS[i],
                       label=f'{region_name}: {col}',
                       linewidth=1.5)
                regions_plotted.append(region_name)
                break

if regions_plotted:
    ax.set_yscale('log')
    ax.grid(True, which="both", linestyle='--', linewidth=0.5)
    ax.set_ylabel(r'Résidus (h)', fontsize=12)
    ax.set_xlabel(r'Temps (s)', fontsize=12)
    ax.legend(loc='best', fontsize=10)
    ax.set_title('Convergence thermique - Toutes les régions', fontsize=14)
    
    plt.tight_layout()
    
    output_file = 'postProcessing/Residuals_all_regions.png'
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"  -> Graphique sauvegardé: {output_file}")

plt.clf()
plt.close()

print("\n" + "=" * 60)
print("That's All Folks!")
print("=" * 60)
