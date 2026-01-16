# Guide Professionnel des Scripts Shell (`#!/bin/sh`)

Ce document sert de référence pour la création, la gestion et les bonnes pratiques concernant les scripts shell, en particulier ceux utilisant l'interpréteur standard `/bin/sh`.

## 1. Introduction

Un script shell est un fichier texte contenant une série de commandes que le shell (l'interpréteur de commandes) exécute séquentiellement. C'est un outil puissant pour l'automatisation de tâches, l'administration système et le déploiement.

## 2. Le Shebang (`#!`)

La première ligne d'un script shell doit toujours être le **shebang**.

```sh
#!/bin/sh
```

*   **`#!`** : Indique au système d'exploitation que ce fichier est un script et spécifie l'interpréteur à utiliser.
*   **`/bin/sh`** : Le chemin absolu vers l'interpréteur. `/bin/sh` est généralement un lien symbolique vers le shell par défaut du système (souvent `bash` ou `dash` sur Linux). Utiliser `/bin/sh` vise généralement une compatibilité POSIX maximale.

> **Note** : Si vous avez besoin de fonctionnalités spécifiques à Bash (tableaux, substitutions avancées), utilisez `#!/bin/bash`. Pour une portabilité maximale, restez sur `#!/bin/sh`.

## 3. Création et Exécution

### 3.1 Création
Créez un fichier avec l'extension `.sh` (conventionnelle, mais pas obligatoire).

```bash
touch mon_script.sh
```

### 3.2 Permissions
Pour qu'un script soit exécutable, il doit avoir les permissions appropriées.

```bash
chmod +x mon_script.sh
```
*   `+x` ajoute le droit d'exécution pour l'utilisateur, le groupe et les autres (selon l'umask).
*   Pour restreindre à l'utilisateur propriétaire uniquement : `chmod u+x mon_script.sh`.

### 3.3 Exécution
Pour lancer le script depuis le dossier courant :

```bash
./mon_script.sh
```

Si le dossier du script est dans votre variable `$PATH`, vous pouvez l'appeler directement par son nom.

## 4. Syntaxe et Concepts Clés

### 4.1 Commentaires
Tout ce qui suit un `#` est ignoré par l'interpréteur (sauf le shebang).

```sh
# Ceci est un commentaire
echo "Bonjour" # Ceci est aussi un commentaire
```

### 4.2 Variables
*   **Définition** : Pas d'espaces autour du `=`.
*   **Utilisation** : Préfixer avec `$`. Il est recommandé d'entourer les variables de `{}` et de guillemets `""` pour éviter les problèmes d'espaces.

```sh
NOM="MonProjet"
echo "Bienvenue dans ${NOM}"
```

### 4.3 Arguments du Script
Les scripts peuvent recevoir des arguments lors de l'appel.

*   `$0` : Nom du script.
*   `$1` à `$9` : Premier au neuvième argument.
*   `$#` : Nombre total d'arguments passés.
*   `$@` : Tous les arguments (liste).
*   `$?` : Code de retour de la dernière commande exécutée (0 = succès, autre = erreur).

## 5. Structures de Contrôle

### 5.1 Conditions (`if`)
Attention aux espaces à l'intérieur des crochets `[ ... ]`.

```sh
if [ "$1" = "start" ]; then
    echo "Démarrage..."
elif [ "$1" = "stop" ]; then
    echo "Arrêt..."
else
    echo "Usage: $0 {start|stop}"
    exit 1
fi
```

### 5.2 Boucles (`for`)

```sh
# Parcourir tous les fichiers .txt
for fichier in *.txt; do
    echo "Traitement de $fichier"
done
```

## 6. Bonnes Pratiques Professionnelles

1.  **Gestion des Erreurs (`set -e`)** :
    Ajoutez `set -e` au début de vos scripts. Cela force l'arrêt immédiat du script si une commande échoue (renvoie un code non nul).
    ```sh
    #!/bin/sh
    set -e
    ```

2.  **Mode "Unset" (`set -u`)** :
    `set -u` provoque une erreur si vous essayez d'utiliser une variable non définie. Cela évite des comportements imprévisibles (ex: `rm -rf /$DOSSIER_VIDE`).

3.  **Citations (Quoting)** :
    Mettez toujours vos variables entre guillemets doubles `"$VAR"` pour gérer correctement les espaces et les caractères spéciaux dans les noms de fichiers ou les chaînes.

4.  **Fonctions** :
    Utilisez des fonctions pour organiser le code et éviter la répétition.

    ```sh
    log_info() {
        echo "[INFO] $(date '+%Y-%m-%d %H:%M:%S') - $1"
    }

    log_info "Script démarré"
    ```

5.  **Indentation** :
    Indentez votre code (généralement 2 ou 4 espaces) pour la lisibilité, comme dans tout autre langage de programmation.

6.  **En-tête de fichier** :
    Incluez un en-tête décrivant le but du script, l'auteur et la date.

    ```sh
    #!/bin/sh
    #
    # Nom: backup.sh
    # Description: Sauvegarde le dossier projet vers /tmp
    # Auteur: Tanguy
    # Date: 2026-01-16
    #
    ```

## 7. Exemple Complet

```sh
#!/bin/sh
set -eu

# Configuration
BACKUP_DIR="/tmp/backup"
SOURCE_DIR="./data"

# Fonction d'aide
usage() {
    echo "Usage: $0 [nom_archive]"
    exit 1
}

# Vérification des arguments
if [ "$#" -ne 1 ]; then
    usage
fi

ARCHIVE_NAME="$1"

echo "Début de la sauvegarde de $SOURCE_DIR vers $BACKUP_DIR/$ARCHIVE_NAME.tar.gz"

# Création du dossier si inexistant
mkdir -p "$BACKUP_DIR"

# Archivage
tar -czf "$BACKUP_DIR/$ARCHIVE_NAME.tar.gz" "$SOURCE_DIR"

echo "Sauvegarde terminée avec succès."
```
