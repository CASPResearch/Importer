# This module is called from ImporterMain at __init__
# It deals with all the functions available to be called from the UI

from PyQt4 import *
from ImporterUI import Ui_Dialog
from qgis.core import *
from LayerNames import layerNames
from Backup import backup
from processing.core.Processing import Processing
from PyQt4.QtSql import QSqlDatabase
from osgeo import ogr

import os, ctypes
import Utils
import CheckLists
import processing.tools
import subprocess

class UIFunctions(QtGui.QDialog):
    def __init__(self, iface):
        QtGui.QDialog.__init__(self)

        self.iface = iface

        # Create the main UI at launch. It hides itself as part of the creation process
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

    def run(self, layer):
        self.layer = layer # Save this so button functions can pick it up and pass it forwards
        layer.window = self.iface.mainWindow() # So that util functions can print errors to the window

        # Determine which table is being imported, out of sample, age, analysis, and excel
        if not Utils.getTableVariety(layer):
            return

        # Determine the lithology category of the layer, from igneous or sedimentary
        if not Utils.getLithologyCategory(layer):
            return

        # Now we know our category and our type, we can check we aren't duplicating an entry
        name = layerNames[layer.cat + layer.tableVariety]
        if Utils.uidCheck(layer, name):
            return

        # Check that our column headings are all valid
        if not Utils.checkHeadings(layer):
            return

        # Create a copy of our layer's target in a zip file, indexed by date and time
        if not backup(layer):
            return

        # Create a temporary layer which is the result of merging the source and target
        # The user can check this over for mistakes before committing
        if not Utils.mergeLayersIntoTemp(layer):
            return

        # Show that temporary layer's content table
        temp = Utils.getLayerByName('Merged')
        if temp:
            self.iface.showAttributeTable(temp)
        else:
            return

        # Populate the UI with appropriate data, and show it
        self.fillFields(layer, temp)
        self.show()

    def fillFields(self, layer, tempLayer):
        # Display Lithology and layer type
        lith = getattr(self.ui, "radioButton" + layer.cat)
        lith.setChecked(True)

        lType = getattr(self.ui, "radioButton" + layer.tableVariety)
        lType.setChecked(True)

        # Get the main project directory
        self.saveDir = os.getcwd()
        self.ui.projectPathField.setText(self.saveDir)

        # Handle the input layer
        self.fillLayerRow(layer, "input")

        # Handle destination layer
        dest = Utils.getLayerByName(layer.masterName)
        if dest:
            self.fillLayerRow(dest, "destination")
        else:
            return

        # Handle the destination file name
        (path, name) = os.path.split(dest.dataProvider().dataSourceUri())
        name = name[:name.index("|")]
        self.ui.destinationFilenameField.setText(name)

        # Handle the temporary layer
        self.fillLayerRow(tempLayer, "temp")

        # Handle the backup path
        self.ui.backupPathField.setText(self.saveDir + "/Backups")

        # Handle the backup filename
        self.ui.backupFilenameField.setText(layer.zipName)

        self.setupButtonFunctions()

    def setupButtonFunctions(self):
        self.ui.pushButtonProceed.clicked.connect(self.proceedButtonFunction)
        self.ui.pushButtonSavePath.clicked.connect(self.savePathButtonFunction)
        self.ui.pushButtonBackupPath.clicked.connect(self.backupPathButtonFunction)

    def proceedButtonFunction(self):
        self.updateDestination(self.layer)
        self.close()

    def savePathButtonFunction(self):
        subprocess.Popen('explorer "{0}"'.format(self.saveDir))

    def backupPathButtonFunction(self):
        subprocess.Popen('explorer "{0}"'.format(self.saveDir + "/Backups"))

    # Fill a UI row with the layer name, and the feature count of that layer
    def fillLayerRow(self, layer, prefix):
        uiField = getattr(self.ui, prefix + "Field")
        layerName = layer.name()
        uiField.setText(layerName)

        count = layer.dataProvider().featureCount()
        uiCount = getattr(self.ui, prefix + "Count")
        uiCount.setText(str(count))        

    def updateDestination(self, layer):
        masterLayer = Utils.getLayerByName(layer.masterName)

        for feature in layer.getFeatures():
            masterLayer.dataProvider().addFeatures([feature])

        if iface.mapCanvas().isCachingEnabled():
            masterLayer.setCacheImage(None)
        else:
            self.iface.mapCanvas().refresh()

        temp = Utils.getLayerByName('Merged')
        if temp:
            tempID = temp.id()
            QgsMapLayerRegistry.instance().removeMapLayers([tempID])
        else:
            return
