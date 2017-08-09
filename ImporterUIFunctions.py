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

        # Set strings to be used as layer names indexes
        self.igneousSamplesMaster = "Igneous and metamorphic samples"
        self.sedimentarySamplesMaster = "Sedimentary Samples"
        self.igneousSummaryAgesMaster = "IgneousMetamorphicSummaryAges"
        self.igneousSampleAnalysesMaster = "IgenousMetamorphicAnalysisData"
        self.sedimentarySummaryAgesMaster = "SedimentarySummaryAges"
        self.sedimentarySampleAnalysesMaster = "SedimentaryAnalysisData"
        self.igneousSummaryAgesDestination = "Igneous & metamorphic UPb summary ages"
        self.igneousRawExcelDestination = "Igneous & metamorphic UPb raw data"
        self.sedimentarySummaryAgesDestination = "Sedimentary UPb summary ages"
        self.sedimentaryRawExcelDestination = "Sedimentary UPb raw data"

    def setupChecks(self):
        self.tableTypeCheck = {
            "LithologyCategory":"Samples",
            "SummaryAge":"SummaryAges",
            "Laboratory":"SampleAnalyses"
        }
        self.lithologyCheck = {
            "Meta-igneous":"igneous",
            "Igneous":"igneous",
            "Metamorphic":"igneous",
            "Meta-sedimentary":"sedimentary",
            "Sedimenary":"sedimentary"
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
        self.SampleAnalysesFields = {
            "AnalysisKey":True,
            "SampleId":True,
            "AnalysisNo":True,
            "Mineral":True,
            "Method_1":True,
            "Method_2":True,
            "NoOfGrains":True,
            "PbcCorr":True,
            "PbcCorrMethod":True,
            "PbcCorrOther":True,
            "Laboratory":True,
            "PrimaryStd":True,
            "ReferenceId":True,
            "Comments":True,
            "FirstReport":True
        }
        self.SummaryAgesFields = {
            "SampleIdAge":True,
            "SampleId":True,
            "SummaryAge":True,
            "SumAgeErrorMinus":True,
            "SumAgeErrorPlus":True,
            "AgeYearsMin":True,
            "AgeYearsMax":True,
            "Mineral":True,
            "SumAgeMethod":True,
            "NoOfGrainsUsed":True,
            "MSWD":True,
            "Probability":True,
            "Interpretation":True,
            "Comments":True,
            "AnalysisNo1":True,
            "AnalysisNo2":True,
            "AnalysisNo3":True,
            "FirstReport":True
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

        self.uidCheck(layer, tableType)

        # Check the list of headings are all valid
        for field in layer.fields():
            name = field.name()
            handler = getattr(self, '{}'.format(tableType + "Fields"))
            if not name in handler:
                print "Invalid column heading detected"
                msg = "Invalid column heading: " + name
                ctypes.windll.user32.MessageBoxW(0, msg, u"Error", 0x0|0x10)
                return

        # Check if the layer is sedimentary or igneous
        tableLithology = ""
        feature = layer.getFeatures().next()
        if tableType == "Samples":
            cat = feature["LithologyCategory"]
            tableLithology = self.lithologyCheck[cat]
        else:
            id = feature["SampleId"]

            # Try the Igneous master
            master = QgsMapLayerRegistry.instance().mapLayersByName(self.igneousSamples)
            for mFeature in master.getFeatures():
                if mFeature["SampleId"] == id: # We have a match
                    cat = mFeature["LithologyCategory"]
                    tableLithology = self.lithologyCheck[cat]
            
            # Try the Sedimentary master
            if tableLithology == "":
                master = QgsMapLayerRegistry.instance().mapLayersByName(self.sedimentarySamples)
                for mFeature in master.getFeatures():
                    if mFeature["SampleId"] == id:
                        cat = mFeature["LithologyCategory"]
                        tableLithology = self.lithologyCheck[cat]

        if tableLithology == "":
            print "Attempted to import a table with no lithology match"
            ctypes.windll.user32.MessageBoxW(0, u"The import table did not contain or match a valid lithology", u"Error", 0x0|0x10)
            return

        self.fillFields(layer)

        self.show()

    # Check that sample IDs exist for importing subtables
    def uidCheck(self, layer, tableType):
        if tableType == "SummaryAges" or tableType == "SampleAnalyses":
            # Build an id list from both master samples tables
            idList = []

            master = QgsMapLayerRegistry.instance().mapLayersByName(self.igneousSamples)
            if master:
                for feature in master.getFeatures():
                    idList.append(feature["SampleId"])

            master = QgsMapLayerRegistry.instance().mapLayersByName(self.sedimentarySamples)
            if master:
                for feature in master.getFeatures():
                    idList.append(feature["SampleId"])

            # Iterate over features there to make a list
            lines = layer.getFeatures()
            for line in lines:
                if line["SampleId"] in idList:
                    print "Attempted to import a duplicate sample"
                    msg = "A duplicate SampleId was found: " + line["SampleId"]
                    ctypes.windll.user32.MessageBoxW(0, msg, u"Error", 0x0|0x10)
                    return

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
