# This file contains a function to create a time indexed backup of a given layer
from PyQt4.QtGui import QMessageBox

import os
import datetime
import zipfile
import Utils


def backup(layer):
    masterLayer = Utils.getLayerByName(layer.masterName)
    (filePath, fileName) = os.path.split(masterLayer.dataProvider().dataSourceUri())

    filePath = Utils.processTempFilePath(filePath)
    fileName = os.path.splitext(fileName)[0]  # Remove the file extension

    # Create a Backups folder if there isn't one, to store the zips
    bkupadd = filePath + "/Backups"
    print "Folder path for backups is", bkupadd
    if not os.path.exists(bkupadd):
        os.makedirs(bkupadd)

    timeStr = datetime.datetime.now().strftime('-%Y%m%d-%H%M')
    layer.zipName = fileName + timeStr + ".zip"  # Store this here so it can be accessed later on in UI population
    backupPath = os.path.join(bkupadd, layer.zipName)

    # Create the zip
    try:
        zf = zipfile.ZipFile(backupPath, 'w')
        for f in os.listdir(filePath):
            baseName = os.path.basename(f)
            name, ext = os.path.splitext(baseName)
            if name == fileName:
                path = os.path.join(filePath, baseName)
                zf.write(path, baseName)
        zf.close()
        return True
    except:
        QMessageBox.warning(layer.window, "Error", "Problems creating archive")
        return False
