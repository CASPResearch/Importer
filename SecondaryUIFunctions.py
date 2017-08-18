from PrimaryUIFunctions import UIFunctions
from SecondaryUI import Ui_Dialog
from PyQt4 import QtGui
from LayerNames import layerNames
from Backup import backup

import os
import Utils

class UIFunctions2(UIFunctions):
    # We need to duplicate the __init__ so it uses this file's Ui_Dialog import, not the original's
    def __init__(self, iface):
        QtGui.QDialog.__init__(self)

        self.iface = iface

        # Get the main project directory
        self.saveDir = os.getcwd()

        # Create the main UI at launch. It hides itself as part of the creation process
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

    def run(self, layer):
        # First, check if we really want to be run
        layer.finalLayer, layer.sampleLayer = Utils.mergeNeeded(layer)
        if not layer.finalLayer or not layer.sampleLayer:
            return

        self.layer = layer  # Save this so button functions can pick it up and pass it forwards
        layer.masterName = layerNames[layer.cat + layer.tableVariety]

        # Create a copy of our layer's target in a zip file, indexed by date and time
        if not backup(layer.finalLayer):
            return

        # Create a temporary layer which is the result of merging the source and target
        # The user can check this over for mistakes before committing
        #if not Utils.mergeLayersIntoTemp(layer):
            #return

        # Show that temporary layer's content table
        #temp = Utils.getLayerByName('Merged')
        #if temp:
            #self.iface.showAttributeTable(temp)
            #self.temp = temp
        #else:
            #return

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

        # Handle the master layer
        self.fillLayerRow(layer, "master")

        # Handle the samples layer
        self.fillLayerRow(layer.sampleLayer, "samples")

        # Handle destination layer
        self.fillLayerRow(layer.finalLayer, "destination")

        # Handle the destination file name
        (path, name) = os.path.split(layer.finalLayer.dataProvider().dataSourceUri())
        name = name[:name.index("|")]
        self.ui.destinationFilenameField.setText(name)

        # Handle the temporary layer
        self.fillLayerRow(self.temp, "temp")

        # Handle the backup path
        self.ui.backupPathField.setText(self.saveDir + r"\Backups")

        # Handle the backup filename
        self.ui.backupNameField.setText(layer.finalLayer.zipName)

        self.setupButtonFunctions()

    def proceedButtonFunction(self):
        #Utils.updateDestination(self.layer)
        self.handleClose()