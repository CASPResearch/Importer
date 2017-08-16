from qgis.core import *
from processing.core.Processing import Processing

import CheckLists
import processing.tools
import ctypes

def getLayerByName(name):
    layers = QgsMapLayerRegistry.instance().mapLayersByName(name)
    if layers:
        return layers[0]

    msg = "No layers of requested name: " + name
    ctypes.windll.user32.MessageBoxW(0, msg, u"Error", 0x0|0x10)
    return False

# Check which table type is being imported
def getTableVariety(layer):
    list = CheckLists.tableVariety
    for field in layer.fields():
        name = field.name()
        if name in list:
            layer.tableType = list[name]
            return True

    QMessageBox.warning(layer.window, "Wrong Layer Type", "Your table must contain a field named LithologyCategory, SummaryAge, Laboratory, or RawExcel")
    return False

# Check that our LithologyCategory is a valid entry
def getLithologyCategory(layer):
    # First find which sample layer our UID appears in, or use ourself if we're a sample layer
    idLayer = ""
    if layer.tableType == "samples": # We contain the actual lithology category
        idLayer = layer
    else:
        idLayer = checkUID(layer, layerNames.igneoussample) or checkUID(layer, layerNames.sedimentarysample)
        if not idLayer:
            QMessageBox.warning(layer.window, "No sample table", "No UID match found in sample tables. Please import the appropriate samples")
            return False

    # Now check if the sample layer identified has a lithologycategory, and what it is
    feature = idLayer.getFeatures().next()
    cat = feature["lithologycategory"]
    if cat:
        if cat in CheckLists.lithologyCheck:
            layer.cat = CheckLists.lithologyCheck[feature["lithologycategory"]]
            return True
        else:
            QMessageBox.warning(layer.window, "Invalid lithology", "The import table did not contain or match a valid lithology")
    else:
        QMessageBox.warning(layer.window, "Error", "A sample table was found, but it doesn't have a lithologycategory field! Please investigate")

    return False

# Check the list of headings are all valid
def checkHeadings(layer):
    remaining = list(getattr(CheckLists, layer.tableVariety + "Fields"))
    unexpected = []

    for field in layer.fields():
        if field in remaining:
            remaining.remove(field)
        else:
            unexpected.append(field)

    if len(unexpected) > 0 or len(remaining) > 0:
        QMessageBox.warning(layer.window, "Error", "Invalid headings found: %s. Required headings not found: %s" % (unexpected, remaining))
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

    rows = layer.getFeatures()
    for row in rows:
        if row["sampleid"] in ids:
            return checkLayer

    return False

def processTempFilePath(path):
    if "dbname='" in path:
        print "Cutting rubbish off the front of fileName"
        return path[8:]
    return path

def mergeLayersIntoTemp(importLayer):
    masterLayer = getLayerByName(importLayer.masterName)
    if not masterLayer:
        return False

    Processing.initialize()
    processing.runandload("qgis:mergevectorlayers", [importLayer] + [masterLayer], None)
    return True
