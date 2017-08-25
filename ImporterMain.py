from PrimaryUIFunctions import UIFunctions
from SecondaryUIFunctions import UIFunctions2
from PyQt4.QtGui import *
from qgis.core import QgsMapLayer, QGis

import Utils

# initialize Qt resources from file resources.py. This makes the button icon show up
import resources

class Importer:
    def __init__(self, iface):
        # Save reference to the QGIS interface
        self.iface = iface

        # Create the UI dialog
        self.primaryDialog = UIFunctions(iface)
        self.secondaryDialog = UIFunctions2(iface)

        Utils.setGlobals(self)

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
        wkb = layer.wkbType() # 1 == Point, 100 == No Geometry

        if layer.type() == QgsMapLayer.VectorLayer and (wkb == 1 or wkb == 100):
            self.primaryDialog.run(layer)
        else:
            QMessageBox.warning(self.iface.mainWindow(), "Wrong Layer Type",
                                "Import layer must be a Point Geometry or No Geometry Vector Layer")

    def runSecondaryUI(self, master):
        print "runsecondaryui"
        # Refresh the map view
        if self.iface.mapCanvas().isCachingEnabled():
            master.setCacheImage(None)
        else:
            self.iface.mapCanvas().refresh()

        self.secondaryDialog.run(master)
