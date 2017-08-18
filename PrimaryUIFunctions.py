# This module is called from ImporterMain at __init__
# It deals with all the functions available to be called from the UI

from PyQt4 import QtGui
from PyQt4.QtGui import QMessageBox
from PrimaryUI import Ui_Dialog
from qgis.core import *
from LayerNames import layerNames
from Backup import backup

import os
import Utils
import subprocess

class UIFunctions(QtGui.QDialog):
    def __init__(self, iface):
        QtGui.QDialog.__init__(self)

        self.iface = iface

        # Get the main project directory
        self.saveDir = os.getcwd()

        # Create the main UI at launch. It hides itself as part of the creation process
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

    def run(self, layer):
        self.layer = layer  # Save this so button functions can pick it up and pass it forwards

        # Determine which table is being imported, out of sample, age, analysis, and excel
        if not Utils.getTableVariety(layer):
            return

        # Determine the lithology category of the layer, from igneous or sedimentary
        if not Utils.getLithologyCategory(layer):
            return

        # Now we know our category and our type, we can check we aren't duplicating an entry
        name = layerNames[layer.cat + layer.tableVariety]
        if Utils.checkUID(layer, name):
            QMessageBox.warning(layer.window, "UID duplication detected", "UID already imported: %s" % layer.uidMatch)
            return

        layer.masterName = name # We're not duplicating, so now store this for future reference

        # Check that our column headings are all valid
        if not Utils.checkHeadings(layer):
            return

        # Create a copy of our layer's target in a zip file, indexed by date and time
        master = Utils.getLayerByName(layer.masterName)
        if not backup(master):
            return

        # Create a temporary layer which is the result of merging the source and target
        # The user can check this over for mistakes before committing
        if not Utils.mergeLayersIntoTemp(layer):
            return

        # Show that temporary layer's content table
        temp = Utils.getLayerByName('Merged')
        if temp:
            self.iface.showAttributeTable(temp)
            self.temp = temp
        else:
            return

        # Populate the UI with appropriate data, and show it
        self.fillFields(layer)
        self.show()

    def fillFields(self, layer):
        # Display Lithology and layer type
        lith = getattr(self.ui, "radioButton" + layer.cat)
        lith.setChecked(True)

        lType = getattr(self.ui, "radioButton" + layer.tableVariety)
        lType.setChecked(True)

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
        self.fillLayerRow(self.temp, "temp")

        # Handle the backup path
        self.ui.backupPathField.setText(self.saveDir + r"\Backups")

        # Handle the backup filename
        self.ui.backupNameField.setText(dest.zipName)

        self.setupButtonFunctions()

    def setupButtonFunctions(self):
        self.ui.pushButtonProceed.clicked.connect(self.proceedButtonFunction)
        self.ui.pushButtonSavePath.clicked.connect(self.savePathButtonFunction)
        self.ui.pushButtonBackupPath.clicked.connect(self.backupPathButtonFunction)

    def proceedButtonFunction(self):
        Utils.updateDestination(self.layer)
        self.handleClose()

    def savePathButtonFunction(self):
        subprocess.Popen('explorer "{0}"'.format(self.saveDir))

    def backupPathButtonFunction(self):
        subprocess.Popen('explorer "{0}"'.format(self.saveDir + r"\Backups"))

    # Fill a UI row with the layer name, and the feature count of that layer
    def fillLayerRow(self, layer, prefix):
        uiField = getattr(self.ui, prefix + "Field")
        layerName = layer.name()
        uiField.setText(layerName)

        count = layer.dataProvider().featureCount()
        uiCount = getattr(self.ui, prefix + "Count")
        uiCount.setText(str(count))

    def handleClose(self):
        # Cleanup the temp layer
        if self.temp:
            tempID = self.temp.id()
            QgsMapLayerRegistry.instance().removeMapLayers([tempID])

        self.close()
