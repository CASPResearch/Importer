from qgis.core import *
from ImporterUIFunctions import UIFunctions
from PyQt4.QtGui import *


class Importer:
    def __init__(self, iface):
        # Save reference to the QGIS interface
        self.iface = iface

        # Create the UI dialog
        self.dialog = UIFunctions(iface)

    # Called from QGIS on launch
    def initGui(self):
        # Create action that will start plugin configuration
        self.action = QAction(QIcon(":/plugins/DataImporter/icon.png"), "Data Importer", self.iface.mainWindow())
        self.action.setObjectName("DataImporter")
        self.action.setStatusTip("Opens the Data Importer tool window")

        # Connect to the button press signal
        self.action.triggered.connect(self.run)

        # Add toolbar button and menu item
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu("Data Importer", self.action)

    def unload(self):
        # Remove the plugin menu item and icon
        self.iface.removePluginMenu("Data Importer", self.action)
        self.iface.removeToolBarIcon(self.action)
        self.action.triggered.disconnect(self.run)

    def run(self):
        layer = self.iface.activeLayer()

        if layer.type() == QgsMapLayer.VectorLayer and layer.wkbType() == QGis.WKBPoint:
            self.dialog.run(layer)
        else:
            QMessageBox.warning(self.iface.mainWindow(), "Wrong Layer Type", "Import layer must be a Point Geometry Vector Layer")
