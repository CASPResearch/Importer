from qgis.core import *
from processing.core.Processing import Processing
from LayerNames import layerNames
from PyQt4.QtGui import QMessageBox

import CheckLists
import processing.tools
import os

Importer = None
Window = None

# This is called from ImporterMain.py's Importer class __init__ on program launch
def setGlobals(importer):
    global Importer
    Importer = importer
    global Window
    Window = importer.iface.mainWindow()

def getLayerByName(name):
    layers = QgsMapLayerRegistry.instance().mapLayersByName(name)
    if layers:
        return layers[0]

    QMessageBox.warning(Window, "Error", "No layers of requested name: {}".format(name))
    return False

# Check which table type is being imported
def getTableVariety(layer):
    l = CheckLists.tableVariety
    for field in layer.fields():
        name = field.name()
        if name in l:
            layer.tableVariety = l[name]
            return True

    QMessageBox.warning(Window, "Wrong Layer Type", "Your table must contain a field named lithologycategory, "
                                                    "summaryage, laboratory, or preferredage")
    return False

# Check that our LithologyCategory is a valid entry
def getLithologyCategory(layer):
    # First find which sample layer our UID appears in, or use this layer if it's a sample layer
    if layer.tableVariety == "sample":  # We contain the actual lithology category
        idLayer = layer
    else:
        idLayer = checkUID(layer, layerNames["ignmetasample"]) or checkUID(layer, layerNames["sedimentarysample"])
        if not idLayer:
            QMessageBox.warning(Window, "No sample table", "No UID match found in sample tables. Please import the "
                                                           "appropriate samples")
            return False

    # Now check if the sample layer identified has a lithologycategory, and what it is
    feature = idLayer.getFeatures().next()
    cat = feature["lithologycategory"]
    if cat:
        if cat in CheckLists.lithologyCheck:
            layer.cat = CheckLists.lithologyCheck[feature["lithologycategory"]]
            return True
        else:
            QMessageBox.warning(Window, "Invalid lithology", "The import table did not contain or match a "
                                                             "valid lithology")
    else:
        QMessageBox.warning(Window, "Error", "A sample table was found, but it doesn't have a lithologycategory field! "
                                             "Please investigate")

    return False

# Check the list of headings are all valid
def checkHeadings(layer):
    remaining = list(getattr(CheckLists, layer.tableVariety + "Fields"))
    unexpected = []

    for field in layer.fields():
        name = field.name()
        if name in remaining:
            remaining.remove(name)
        else:
            unexpected.append(name)

    if len(unexpected) > 0 or len(remaining) > 0:
        QMessageBox.warning(Window, "Error", "Invalid headings found: %s. "
                                             "Required headings not found: %s" % (unexpected, remaining))
        return False

    return True

# Check if a sample ID from one layer is found in another
def checkUID(layer, checkLayerName):
    # Build an ID list from all appropriate layers
    ids = []
    checkLayer = getLayerByName(checkLayerName)
    if not checkLayer:
        return False

    for feature in checkLayer.getFeatures():
        ids.append(feature["sampleid"])

    # TODO - Return a list of all matches instead of just the first
    rows = layer.getFeatures()
    for row in rows:
        if row["sampleid"] in ids:
            layer.uidMatch = row["sampleid"]
            return checkLayer

    return False

def processTempFilePath(path):
    if "dbname='" in path:
        print "Cutting rubbish off the front of fileName"
        return path[8:]
    return path

def mergeLayersIntoTemp(importLayer):
    print "mergelayersintotemp"
    print importLayer.name()
    masterLayer = getLayerByName(importLayer.masterName)
    print masterLayer.name()
    if not masterLayer:
        return False

    print importLayer.wkbType()
    print masterLayer.wkbType()

    Processing.initialize()
    processing.runandload("qgis:mergevectorlayers", [importLayer] + [masterLayer], None)

    return getLayerByName('Merged')

# This function is where we actually append each new row to the master spatialite file
def updateDestination(layer):
    print "updatedestination"
    masterLayer = getLayerByName(layer.masterName)
    provider = masterLayer.dataProvider()

    #TODO - Find a way to speed this up, and create a UI progress bar
    for feature in layer.getFeatures():
        provider.addFeatures([feature])

    masterLayer.cat = layer.cat
    masterLayer.tableVariety = layer.tableVariety

    Importer.runSecondaryUI(masterLayer)

def mergeNeeded(master):
    print "mergeneeded"
    # If master name was igneousage, igneousexcel, sedimentaryage, sedimentaryexcel, we want to do a second merge
    # Moving on, we need master that's just been added to, the 'sample' of our cat, and the final merged name
    var = master.tableVariety
    print var

    if var != "age" and var != "raw":
        print "returning false 1"
        return False, False

    finalLayerName = layerNames[master.cat + "sample" + var + "merge"]
    sampleLayerName = layerNames[master.cat + "sample"]
    master.masterName = finalLayerName

    finalLayer = getLayerByName(finalLayerName)
    sampleLayer = getLayerByName(sampleLayerName)

    if not finalLayer or not sampleLayer:
        print "returning false 2"
        return False, False

    return finalLayer, sampleLayer

# Returns the path to a layer's file location, minus the filename and extension
# If full is used, returns the path with the filename and extension, but without any extra database locales
def getLayerPath(layer, full):
    (path, name) = os.path.split(layer.dataProvider().dataSourceUri())

    # Strip junk off the front of a temporary layer
    if "dbname='" in path:
        path =  path[8:]

    if not full:
        return path

    name = getLayerFilename(layer, True)
    return path + name

# Returns a layer's filename, with or without an extension depending on the ext argument
def getLayerFilename(layer, ext):
    print "getLayerFilename"
    name = os.path.split(layer.dataProvider().dataSourceUri())[1]

    # Send back the non-extension version
    if not ext:
        return os.path.splitext(name)[0]

    # Strip junk off the end of this thing
    if "\'" in name:
        name = name[:name.index("\'")]

    if "|" in name:
        name = name[:name.index("|")]

    if type(name) == 'tuple':
        name = "".join(name)

    return name

def mergeSQLs(layer1, layer2):
    print "mergesqls"
    Processing.initialize()
    processing.runandload("qgis:joinattributestable", [layer1], [layer2], "sampleid", "sampleid", None)
    return getLayerByName('Merged')
