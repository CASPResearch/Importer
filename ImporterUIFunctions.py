# This module is called from ImporterMain at __init__
# It deals with all the functions available to be called from the UI

from PyQt4 import QtCore, QtGui
from ImporterUI import Ui_Dialog
from qgis.core import QgsMapLayerRegistry, QgsMapLayer
from LayerNames import layerNames
from Backup import backup

import os, ctypes
import Utils
import CheckLists

class UIFunctions(QtGui.QDialog):
    def __init__(self, iface):
        QtGui.QDialog.__init__(self)

        self.iface = iface

        # Create the main UI at launch. It hides itself as part of the creation process
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

    def run(self, layer):
        if not Utils.getTableType(layer):
            return

        uidResult = ""
        if layer.tableType == "Samples":
            if not Utils.getLithologyCategory(layer):
                return
        else:
            # First, check both SamplesMasters to find a matching UID, and hence the lithology category
            id = layer.getFeatures().next()["SampleId"]
            ign = layerNames.igneousSamplesMaster
            sed = layerNames.sedimentarySamplesMaster
            cat = False
            for layerName in {ign, sed}:
                master = Utils.getLayerByName(layerName)
                for mFeature in master.getFeatures():
                    if mFeature["SampleId"] == id: # We have a match
                        layer.cat = CheckLists.lithologyCheck[mFeature["LithologyCategory"]]
                        cat = True
                        break

            if not cat:
                ctypes.windll.user32.MessageBoxW(0, u"Attempted to import a subtable with UIDs not in a samples master", u"Error", 0x0|0x10)
                return

        # Now we know our category and our type, we can check we aren't duplicating an entry
        name = layerNames[layer.cat + layer.tableType + "Master"]
        if not Utils.uidCheck(layer, name):
            return

        if not Utils.checkHeadings(layer):
            return

        self.fillFields(layer)
        self.show()

        backup(layer)

    def fillFields(self, layer):
        # Display Lithology and layer type
        lith = getattr(self.ui, "radioButton" + layer.cat)
        lith.setChecked(True)

        lType = getattr(self.ui, "radioButton" + layer.tableType)
        lType.setChecked(True)

        # Get the project directory
        dir = os.getcwd()
        self.ui.projectPathField.setText(dir)

        # Handle the input layer
        self.fillLayerRow(layer, "input")

        # Handle destination layers
        dest = ""
        master = ""
        if layer.tableType == "Samples" or layer.tableType == "SampleAnalyses":
            dest = Utils.getLayerByName(layer.masterLayer)
        else:
            destName = layerNames[layer.cat + layer.tableType + "Destination"]
            dest = Utils.getLayerByName(destName)
            master = Utils.getLayerByName(layer.masterLayer)

        self.fillLayerRow(dest, "destination")

        if master:
            self.fillLayerRow(master, "master")

        # Handle the destination path
        (path, name) = os.path.split(dest.dataProvider().dataSourceUri())
        name = os.path.splitext(name)[0]
        self.ui.destinationPathField.insertPlainText(path + "/" + name)

        # Handle the destination preview
        self.ui.destinationPreviewField.setText(dest.name() + "_Preview")

    # Fill a UI row with the layer name, and the feature count of that layer
    def fillLayerRow(self, layer, prefix):
        layerName = layer.name()
        uiField = getattr(self.ui, prefix + "LayerField")
        uiField.setText(layerName)

        count = layer.dataProvider().featureCount()
        uiCount = getattr(self.ui, prefix + "LayerCount")
        uiCount.setText(str(count))
