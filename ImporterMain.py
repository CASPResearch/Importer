from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from ImporterUIFunctions import UIFunctions

# initialize Qt resources from file resources.py
import resources
import ctypes

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
        self.action.setWhatsThis("Configuration for test plugin")
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
        # Create and show a configuration dialog or something similar
        print "ImporterMain.py: run called!"

        layer = self.iface.activeLayer()
        
        # Checking wkbType == 100 is "Layer is a data-only layer"
        if layer.type() == QgsMapLayer.VectorLayer and layer.wkbType() == 100:
            self.dialog.run(layer)
        else:
            print "Wrong layer type"
            ctypes.windll.user32.MessageBoxW(0, u"Layer must be a Data-Only Vector Layer", u"Error", 0x0|0x10)
