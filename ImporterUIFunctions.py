# This module is called from ImporterMain at __init__
# It deals with all the functions available to be called from the UI

from PyQt4 import QtCore, QtGui
from ImporterUI import Ui_Dialog
from qgis.core import QgsMapLayerRegistry, QgsMapLayer

import os, ctypes

class UIFunctions(QtGui.QDialog):
    def __init__(self, iface):
        QtGui.QDialog.__init__(self)

        self.iface = iface

        # Create the main UI at launch. It hides itself as part of the creation process
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.setupChecks()

    def setupChecks(self):
        self.tableTypeCheck = {
            "LithologyCategory":"Samples",
            "SummaryAge":"SummaryAges",
            "Laboratory":"SampleAnalyses"
        }
        self.SamplesFields = {
            "SampleId":True,
            "SampleNo":True,
            "Latitude":True,
            "Longitude":True,
            "Accuracy":True,
            "SurfaceSample":True,
            "BoreName":True,
            "DepthMin_m":True,
            "Country":True,
            "GeologicalElement":True,
            "SpecificFeature":True,
            "Group_":True,
            "Formation":True,
            "Member":True,
            "Unit":True,
            "LithologyCategory":True,
            "LithologySubcategory":True,
            "Lithology":True,
            "LithologyDescription":True,
            "ReferenceId":True,
            "YearsMin":True,
            "YearsMax":True,
            "AgeMin":True,
            "AgeMax":True,
            "AgeDefinitionBasis":True,
            "UPbAgeData":True,
            "LuHfData":True,
            "OtherData":True,
            "Comments":True,
            "RelationToReservoir":True,
            "SummaryInterpretation":True,
            "RelevanceToYoungerUnits":True,
            "FirstReport":True,
            "ZirconAgeComments":True,
            "ZirconAgeMethod":True,
            "LocalityName":True,
            "NatureOfEvent":True,
            "LithologicalDescription":True,
            "CASP_Sample":True,
            "Collector":True,
            "Project":True
        }

    def run(self, layer):
        print "Run called in UIFunctions"

        # Check which of the three table types is being imported
        tableType = ""
        for field in layer.fields():
            name = field.name()
            if name in self.tableTypeCheck:
                tableType = self.tableTypeCheck[name]
                break

        if tableType == "":
            print "Attempted to import an invalid table"
            ctypes.windll.user32.MessageBoxW(0, u"Your table must contain a field named LithologyCategory, SummaryAge, or Laboratory", u"Error", 0x0|0x10)
            return

        # Check that sample IDs exist for importing subtables
        if tableType == "SummaryAges" or tableType == "SampleAnalyses":
            # Get the master table
            # iterate over features there to make a list
            lines = layer.getFeatures()
            for line in lines:
                if line["SampleId"] in #master table list:
                    #Throw error, we have a duplication

        # Here is where we should check the list of headings
        for field in layer.fields()
            name = field.name()
            if not name in self[tableType + "Fields"]
                #WARN and exit

        # Check if a subtable is sedimentary or igneous

        self.fillFields(layer)

        self.show()

    def fillFields(self, layer):
        print "fillFields called in UIFunctions"

        # Set the checkboxes at the top to 'Master' to begin with
        self.ui.radioButtonLive.setChecked(True)

        # Get the layer name
        layerName = layer.name()
        self.ui.tableNameField.setText(layerName)

        # Get the count of entries
        count = layer.dataProvider().featureCount()
        self.ui.tableNameCount.setText(str(count))

        # Get the working directory
        dir = os.getcwd()
        print "We found a path"
        print dir
        self.ui.masterPathField.setText(dir)
    
    # Called by the run function in ImporterMain to populate comboboxes with a list of relevent layers
    def initLayerCombobox(self, combobox, default):
         combobox.clear()

         # Get the list of initialized map layers
         reg = QgsMapLayerRegistry.instance()

         # Loop over the map layers in the list and add each to the combobox
         for (key, layer) in reg.mapLayers().iteritems():
             if layer.type() == QgsMapLayer.RasterLayer or layer.type() == QgsMapLayer.VectorLayer: #This doesn't work in QGIS2.0. Can I do without?: and ( layer.usesProvider() and layer.providerKey() == 'gdal' ):
                 combobox.addItem(layer.name(), key)
         
         # Check the box has entries, and select the default one
         idx = combobox.findData(default)
         if idx != -1:
             combobox.setCurrentIndex(idx) 
             
    # Returns the value of the currently selected layer
    def layerFromComboBox(self, combobox):
        layerID = str(combobox.itemData(combobox.currentIndex()))
        return QgsMapLayerRegistry.instance().mapLayer(layerID)
