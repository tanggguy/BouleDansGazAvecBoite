# -*-coding:Utf-8 -*
"""
Plot_HeatFlux.py - Visualisation des flux de chaleur
=====================================================
Lit les données de flux de chaleur aux surfaces et trace l'évolution

Sortie: postProcessing/HeatFlux.png
"""
import sys
import os
from pathlib import Path
from matplotlib import pyplot as plt
import numpy as np

##############################################################################
# CONFIGURATION
##############################################################################

# Surfaces de flux et leurs configurations
FLUX_SURFACES = {
    'HeatFlux_box_xmin_external': {
        'color': '#E41A1C',
        'label': 'Entrée (box_xmin externe)',
        'linestyle': '-'
    },
    'HeatFlux_box_xmax_external': {
        'color': '#377EB8', 
        'label': 'Sortie (box_xmax externe)',
        'linestyle': '-'
    },
    'HeatFlux_gas_to_sphere': {
        'color': '#4DAF4A',
        'label': 'Interface gaz-sphère',
        'linestyle': '--'
    },
}

##############################################################################
# FONCTIONS UTILITAIRES
##############################################################################

def read_heat_flux_file(base_path):
    """
    Lit les fichiers de flux de chaleur OpenFOAM.
    Format: fichier surfaceFieldValue.dat
    """
    time = []
    flux = []
    area = None
    
    # Parcourir les dossiers de temps
    if not os.path.exists(base_path):
        return None, None, None
    
    time_folders = sorted([f for f in os.listdir(base_path) 
                          if os.path.isdir(os.path.join(base_path, f))],
                         key=lambda x: float(x) if x.replace('.', '').replace('-', '').isdigit() else 0)
    
    for tf in time_folders:
        dat_file = os.path.join(base_path, tf, "surfaceFieldValue.dat")
        if os.path.exists(dat_file):
            with open(dat_file, 'r') as f:
                for line in f:
                    if line.startswith('#'):
                        # Chercher l'aire dans le header
                        if 'Area' in line:
                            try:
                                area = float(line.split(':')[-1].strip())
                            except:
                                pass
                        continue
                    values = line.split()
                    if len(values) >= 2:
                        time.append(float(values[0]))
                        flux.append(float(values[1]))
    
    return np.array(time), np.array(flux), area


##############################################################################
# LECTURE DES DONNÉES
##############################################################################

print("=" * 60)
print("Plot_HeatFlux.py - Visualisation des flux de chaleur")
print("=" * 60)

all_flux_data = {}

for surface_name, config in FLUX_SURFACES.items():
    # Le chemin dépend de la région
    if 'box_xmin' in surface_name:
        path = f"postProcessing/{surface_name}/box_xmin"
    elif 'box_xmax' in surface_name:
        path = f"postProcessing/{surface_name}/box_xmax"
    elif 'gas_to_sphere' in surface_name:
        path = f"postProcessing/{surface_name}/gas"
    else:
        path = f"postProcessing/{surface_name}"
    
    print(f"\nRecherche de données: {path}")
    
    time, flux, area = read_heat_flux_file(path)
    
    if time is not None and len(time) > 0:
        all_flux_data[surface_name] = {
            'time': time,
            'flux': flux,
            'area': area,
            'config': config
        }
        print(f"  -> {len(time)} points lus")
        if area:
            print(f"     Aire: {area:.6f} m²")
        print(f"     Flux moyen: {np.mean(flux):.2f} W")
    else:
        print(f"  -> Aucune donnée trouvée")

##############################################################################
# TRACÉ DU GRAPHIQUE
##############################################################################

if all_flux_data:
    print(f"\nCréation du graphique...")
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    
    # --- Graphique 1: Flux vs Temps ---
    for surface_name, data in all_flux_data.items():
        ax1.plot(data['time'], data['flux'],
                color=data['config']['color'],
                linestyle=data['config']['linestyle'],
                label=data['config']['label'],
                linewidth=1.5)
    
    ax1.set_xlabel(r'Temps (s)', fontsize=12)
    ax1.set_ylabel(r'Flux de chaleur (W)', fontsize=12)
    ax1.set_title('Évolution temporelle du flux de chaleur', fontsize=14)
    ax1.grid(True, linestyle='--', alpha=0.7)
    ax1.legend(loc='best', fontsize=10)
    
    # --- Graphique 2: Bilan de flux (si entrée et sortie disponibles) ---
    if 'HeatFlux_box_xmin_external' in all_flux_data and 'HeatFlux_box_xmax_external' in all_flux_data:
        flux_in = all_flux_data['HeatFlux_box_xmin_external']
        flux_out = all_flux_data['HeatFlux_box_xmax_external']
        
        # Interpoler sur le même vecteur temps
        common_time = flux_in['time']
        
        ax2.plot(common_time, flux_in['flux'], 'r-', label='Flux entrant', linewidth=1.5)
        ax2.plot(common_time, -flux_out['flux'], 'b-', label='Flux sortant (inversé)', linewidth=1.5)
        
        # Bilan
        if len(flux_in['flux']) == len(flux_out['flux']):
            bilan = flux_in['flux'] + flux_out['flux']
            ax2.plot(common_time, bilan, 'g--', label='Bilan (entrée + sortie)', linewidth=1.5)
        
        ax2.set_xlabel(r'Temps (s)', fontsize=12)
        ax2.set_ylabel(r'Flux de chaleur (W)', fontsize=12)
        ax2.set_title('Bilan de flux thermique (conservation de l\'énergie)', fontsize=14)
        ax2.grid(True, linestyle='--', alpha=0.7)
        ax2.legend(loc='best', fontsize=10)
        ax2.axhline(y=0, color='k', linestyle='-', linewidth=0.5)
    else:
        ax2.text(0.5, 0.5, 'Données insuffisantes pour le bilan',
                ha='center', va='center', fontsize=14,
                transform=ax2.transAxes)
        ax2.set_axis_off()
    
    plt.tight_layout()
    
    output_file = 'postProcessing/HeatFlux.png'
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"  -> Graphique sauvegardé: {output_file}")
    
    # Afficher le résumé des flux
    print("\n" + "-" * 40)
    print("RÉSUMÉ DES FLUX (valeurs finales):")
    print("-" * 40)
    for surface_name, data in all_flux_data.items():
        if len(data['flux']) > 0:
            print(f"  {data['config']['label']}: {data['flux'][-1]:.2f} W")
    
    plt.clf()
    plt.close()
else:
    print("\nERREUR: Aucune donnée de flux trouvée!")

print("\n" + "=" * 60)
print("That's All Folks!")
print("=" * 60)
