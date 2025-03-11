from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsProcessing, 
                       QgsProcessingAlgorithm, 
                       QgsProcessingParameterVectorLayer, 
                       QgsProcessingParameterField, 
                       QgsProcessingParameterString, 
                       QgsProcessingParameterFeatureSink, 
                       QgsField, 
                       QgsProject, 
                       QgsProcessingException,
                       QgsGraduatedSymbolRenderer, 
                       QgsSymbol, 
                       QgsRendererRange)
from PyQt5.QtCore import QVariant
from PyQt5.QtGui import QColor
from qgis import processing


class PopulationDensityTool(QgsProcessingAlgorithm):
    COMMUNES_LAYER = 'COMMUNES_LAYER'
    POPULATION_LAYER = 'POPULATION_LAYER'
    JOIN_FIELD_COMMUNES = 'JOIN_FIELD_COMMUNES'
    JOIN_FIELD_POPULATION = 'JOIN_FIELD_POPULATION'
    REGION = 'REGION'
    OUTPUT = 'OUTPUT'

    def name(self):
        return 'population_density_tool'  

    def displayName(self):
        return 'Population Density Tool'  

    def group(self):
        return 'Custom Tools' 

    def groupId(self):
        return 'custom_tools'  

    def shortHelpString(self):
        return "Calculez la densité de population pour une région donnée saisie manuellement."

    def createInstance(self):
        return PopulationDensityTool()

    def initAlgorithm(self, config=None):
        # un paramètre pour la couche des communes
        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.COMMUNES_LAYER,
                'Communes',
                [QgsProcessing.TypeVectorPolygon]
            )
        )
        
        # un paramètre pour la couche de population
        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.POPULATION_LAYER,
                'Population',
                [QgsProcessing.TypeVector]
            )
        )
        
        # ajouter les champs de jointure pour les deux couches
        self.addParameter(
            QgsProcessingParameterField(
                self.JOIN_FIELD_COMMUNES,
                'Champ de jointure (communes)',
                parentLayerParameterName=self.COMMUNES_LAYER
            )
        )
        self.addParameter(
            QgsProcessingParameterField(
                self.JOIN_FIELD_POPULATION,
                'Champ de jointure (population)',
                parentLayerParameterName=self.POPULATION_LAYER
            )
        )
        
        # ajouter un paramètre pour le nom de la région
        self.addParameter(
            QgsProcessingParameterString(
                self.REGION,
                'Region name (enter manually)'
            )
        )
        
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                'Output layer'
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        # récupérer les données saisies par l'utilisateur
        communes_layer = self.parameterAsVectorLayer(parameters, self.COMMUNES_LAYER, context)
        population_layer = self.parameterAsVectorLayer(parameters, self.POPULATION_LAYER, context)
        join_field_communes = self.parameterAsString(parameters, self.JOIN_FIELD_COMMUNES, context)
        join_field_population = self.parameterAsString(parameters, self.JOIN_FIELD_POPULATION, context)
        region_name = self.parameterAsString(parameters, self.REGION, context)

        # jointure des couches
        feedback.pushInfo("Joining communes and population layers...")
        joined_layer = processing.run("native:joinattributestable", {
            'INPUT': communes_layer,
            'FIELD': join_field_communes,
            'INPUT_2': population_layer,
            'FIELD_2': join_field_population,
            'FIELDS_TO_COPY': ['ptot'],
            'METHOD': 1,
            'DISCARD_NONMATCHING': True,
            'OUTPUT': 'memory:joined_layer'
        }, context=context, feedback=feedback)['OUTPUT']
        
        # filtrer les communes par région
        feedback.pushInfo(f"Filtering for region: {region_name}...")
        filtered_layer = processing.run("native:extractbyattribute", {
            'INPUT': joined_layer,
            'FIELD': 'region',
            'OPERATOR': 0,  # Equals
            'VALUE': region_name,
            'OUTPUT': 'memory:filtered_layer'
        }, context=context, feedback=feedback)['OUTPUT']
        
        # reprojection en EPSG:2154
        feedback.pushInfo("Reprojecting layer to EPSG:2154...")
        reprojected_layer = processing.run("native:reprojectlayer", {
            'INPUT': filtered_layer,
            'TARGET_CRS': 'EPSG:2154',
            'OUTPUT': 'memory:reprojected_layer'
        }, context=context, feedback=feedback)['OUTPUT']
        
        # calcul de la densité de population
        feedback.pushInfo("Calculating population density...")
        reprojected_layer.dataProvider().addAttributes([QgsField("density", QVariant.Double)])
        reprojected_layer.updateFields()

        for feature in reprojected_layer.getFeatures():
            population = feature["ptot"]  
            area = feature.geometry().area() / 1e6  
            density = population / area if area > 0 else 0  
            attrs = {reprojected_layer.fields().indexFromName("density"): density}
            reprojected_layer.dataProvider().changeAttributeValues({feature.id(): attrs})

        # une symbologie
        feedback.pushInfo("Applying graduated symbology...")
        ranges = [
            (0, 100, "Densité Faible", "#FFFF00"),  
            (100, 200, "Densité Moyenne", "#FFA500"),  
            (200, float('inf'), "Densité Forte", "#FF0000")  
        ]

        symbol_ranges = []
        for lower, upper, label, color in ranges:
            symbol = QgsSymbol.defaultSymbol(reprojected_layer.geometryType())
            symbol.setColor(QColor(color))
            range = QgsRendererRange(lower, upper, symbol, label)
            symbol_ranges.append(range)

        renderer = QgsGraduatedSymbolRenderer("density", symbol_ranges)
        renderer.setMode(QgsGraduatedSymbolRenderer.EqualInterval)
        reprojected_layer.setRenderer(renderer)

        QgsProject.instance().addMapLayer(reprojected_layer)

        # création des centroïdes
        centroids_layer = processing.run("native:centroids", {
            'INPUT': reprojected_layer,
            'ALL_PARTS': False,
            'OUTPUT': 'memory:centroids_layer'
        }, context=context, feedback=feedback)['OUTPUT']

        centroids_layer.dataProvider().addAttributes([QgsField("density", QVariant.Double)])
        centroids_layer.updateFields()

        for centroid, feature in zip(centroids_layer.getFeatures(), reprojected_layer.getFeatures()):
            attrs = {centroids_layer.fields().indexFromName("density"): feature["density"]}
            centroids_layer.dataProvider().changeAttributeValues({centroid.id(): attrs})

        # les centroïdes
        QgsProject.instance().addMapLayer(centroids_layer)
        
        return {self.OUTPUT: reprojected_layer}
