from qgis.core import QgsMapLayerRegistry, QgsMapLayer

import ctypes
import CheckLists

def getLayerByName(name):
    return QgsMapLayerRegistry.instance().mapLayersByName(name)[0]

# Check which of the three table types is being imported
def getTableType(layer):
    list = CheckLists.tableTypeCheck
    for field in layer.fields():
        name = field.name()
        if name in list:
            layer.tableType = list[name]
            return True

    ctypes.windll.user32.MessageBoxW(0, u"Your table must contain a field named LithologyCategory, SummaryAge, Laboratory, or RawExcel", u"Error", 0x0|0x10)
    return False

# Check that our LithologyCategory is a valid entry
def getLithologyCategory(layer):
    feature = layer.getFeatures().next()
    if feature["LithologyCategory"] in CheckLists.lithologyCheck:
        layer.cat = CheckLists.lithologyCheck[feature["LithologyCategory"]]
        return True

    ctypes.windll.user32.MessageBoxW(0, u"The import table did not contain or match a valid lithology", u"Error", 0x0|0x10)
    return False

# Check the list of headings are all valid
def checkHeadings(layer):
    allowedFields = getattr(CheckLists, layer.tableType + "Fields")
    for field in layer.fields():
        name = field.name()
        if not name in allowedFields:
            msg = "Invalid column heading: " + name
            ctypes.windll.user32.MessageBoxW(0, msg, u"Error", 0x0|0x10)
            return False
        
    return True


# Check that sample IDs don't already exist for importing tables
def uidCheck(layer, checkLayerName):
    # Build an ID list from all appropriate layers
    idList = []
    master = getLayerByName(checkLayerName)
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
