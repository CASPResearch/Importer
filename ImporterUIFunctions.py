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
            "Laboratory":"SampleAnalyses",
            "PreferredAge":"RawExcel"
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

    # Check which of the three table types is being imported
    def getTableType(self, layer):
        for field in layer.fields():
            name = field.name()
            if name in self.tableTypeCheck:
                layer.tableType = self.tableTypeCheck[name]
                break

        if not hasattr(layer, "tableType"):
            ctypes.windll.user32.MessageBoxW(0, u"Your table must contain a field named LithologyCategory, SummaryAge, or Laboratory", u"Error", 0x0|0x10)

    def getLithologyCategory(self, layer):
        # Find the lithology category
        feature = layer.getFeatures().next()
        layer.cat = self.lithologyCheck[feature["LithologyCategory"]] # Store cat on the layer for later

        if not hasattr(layer, "cat"):
            ctypes.windll.user32.MessageBoxW(0, u"The import table did not contain or match a valid lithology", u"Error", 0x0|0x10)

    def run(self, layer):
        self.getTableType(layer)
        if not hasattr(layer, "tableType"):
            return

        uidResult = ""
        if layer.tableType == "Samples":
            self.getLithologyCategory(layer)
            if not hasattr(layer, "cat"):
                return

            layerName = getattr(self, layer.cat + "SamplesMaster")

            # Check the UIDs aren't duplicated
            uidResult = self.uidCheck(layer, layerName)
        else:
            # First, check both SamplesMasters to find a matching UID, and hence the lithology category
            feature = layer.getFeatures().next()
            id = feature["SampleId"]
            ign = self.igneousSamplesMaster
            sed = self.sedimentarySamplesMaster
            for layerName in {ign, sed}:
                master = QgsMapLayerRegistry.instance().mapLayersByName(layerName)
                for mFeature in master.getFeatures():
                    if mFeature["SampleId"] == id: # We have a match
                        layer.cat = self.lithologyCheck[mFeature["LithologyCategory"]]

            if not hasattr(layer, "cat"):
                ctypes.windll.user32.MessageBoxW(0, u"Attempted to import a subtable with UIDs not in a samples master", u"Error", 0x0|0x10)
                return

            # Now we know our category and our type, we can check we aren't duplicating an entry
            name = getattr(self, layer.cat + tableType + "Master")
            uidResult = self.uidCheck(layer, name)

        if not uidResult:
            return

        if not self.checkHeadings(layer):
            return

        self.fillFields(layer)

        self.show()

    def checkHeadings(self, layer):
        # Check the list of headings are all valid
        for field in layer.fields():
            name = field.name()
            allowedFields = getattr(self, layer.tableType + "Fields")
            if not name in allowedFields:
                msg = "Invalid column heading: " + name
                ctypes.windll.user32.MessageBoxW(0, msg, u"Error", 0x0|0x10)
                return False
        
        return True

    # Check that sample IDs don't already exist for importing tables
    def uidCheck(self, layer, checkLayerName):
        # Build an ID list from all appropriate layers
        idList = []
        print checkLayerName
        master = QgsMapLayerRegistry.instance().mapLayersByName(checkLayerName)
        print "Printing master"
        print master
        print hasattr(master, "getFeatures")
        print hasattr(master, "name")
        print dir(master)
        print dir(layer)
        if master:
            for feature in master.getFeatures():
                idList.append(feature["SampleId"])
        else:
            return False

        lines = layer.getFeatures()
        for line in lines:
            if line["SampleId"] in idList:
                msg = "A duplicate SampleId was found: " + line["SampleId"]
                ctypes.windll.user32.MessageBoxW(0, msg, u"Error", 0x0|0x10)
                return False

        # This gets tricky. For Samples and SampleAnalyses, which stand alone, master is also destination
        # For SummaryAges and RawExcel, this is the master updated, but not the destination fused feature class
        layer.masterLayer = checkLayerName
        return True

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
            dest = QgsMapLayerRegistry.instance().mapLayersByName(layer.masterLayer)
        else:
            destName = getattr(self, layer.cat + layer.tableType + "Destination")
            dest = QgsMapLayerRegistry.instance().mapLayersByName(destName)
            master = QgsMapLayerRegistry.instance().mapLayersByName(layer.masterLayer)

        self.fillLayerRow(dest, "destination")

        if master:
            self.fillLayerRow(master, "master")

        # Handle the destination path
        path = dest.dataProvider().dataSourceUri()
        self.ui.destiationPathField.setText(path)

        # Handle the destination preview
        self.ui.destinationLPreviewField.setText(dest.name() + "_Preview")

    # Fill a UI row with the layer name, and the feature count of that layer
    def fillLayerRow(self, layer, prefix):
        layerName = layer.name()
        uiField = getattr(self.ui, prefix + "LayerField")
        uiField.setText(layerName)

        count = layer.dataProvider().featureCount()
        uiCount = getattr(self.ui, prefix + "LayerCount")
        uiCount.setText(str(count))
