<h1 align="center">Outil de géotraitement pour QGIS<br>Calcul de la densité de population</h1>

Ce projet présente le développement d’un **outil de géotraitement personnalisé sous forme de plugin Python pour QGIS**, conçu pour **calculer et visualiser la densité de population** à partir de données géographiques. Cet outil a été intégré à la **Boîte à outils de traitement (Processing Toolbox)** de QGIS et permet d’automatiser l’analyse démographique à l’échelle régionale.  

L’exemple présenté repose sur des **données de population et de communes en France**, mais l’outil peut être adapté à tout autre territoire disposant de données similaires.  

<br>

**Installation et ajout de l’outil dans QGIS**

1️⃣ Ajouter le script à QGIS
1. Télécharger [`PopulationDensityTool.py`](PopulationDensityTool.py)  
2. Copier le fichier dans le dossier des scripts Processing de QGIS :  
   - Windows : `C:\Users\TonNom\AppData\Roaming\QGIS\QGIS3\profiles\default\processing\scripts\`  
   - Linux/macOS : `~/.local/share/QGIS/QGIS3/profiles/default/processing/scripts/`

<br>

2️⃣ Charger l’outil dans la Boîte à outils de traitement
1. Ouvrir QGIS  
2. Aller dans "Traitement" → "Boîte à outils" (Ctrl + Alt + T)  
3. Faire un clic droit sur "Scripts" → "Recharger les scripts"  
4. L’outil **"Population Density Tool"** apparaîtra dans la liste des outils personnalisés  

<br>

3️⃣ Exécuter l’outil
1. Sélectionner les paramètres d’entrée :  
   - La couche des communes (vecteur polygonal)  
   - La couche de population 
   - Le champ de jointure entre les deux couches
   - Le nom de la région à analyser  
2. Lancer l’analyse et observer la carte générée  

<br>

Résultats et visualisation dans QGIS
L’outil applique automatiquement une **classification par densité de population** avec la palette suivante :  
- Densité faible (0-100 hab/km²) → 🟡 Jaune  
- Densité moyenne (100-200 hab/km²) → 🟠 Orange  
- Densité forte (>200 hab/km²) → 🔴 Rouge  

<div align="center">
    <img src="https://github.com/DariaPodlovchenko/Outil-de-g-otraitement-Plugin-QGIS/raw/main/pluginqgis.jpg" width="600">
</div>
