# This file contains a function to create a time indexed backup of a given layer
import os, datetime, zipfile, ctypes
import Utils

def backup(layer):
    print "backup"
    (filePath, fileName) = os.path.split(layer.dataProvider().dataSourceUri())

    filePath = Utils.processTempFilePath(filePath)
    fileName = os.path.splitext(fileName)[0] # Remove the file extension

    # Create a Backups folder if there isn't one, to store the zips
    bkupadd = filePath + "/Backups"
    print "Folder path for backups is", bkupadd
    if not os.path.exists(bkupadd):
        os.makedirs(bkupadd)

    timeStr = datetime.datetime.now().strftime('-%Y%m%d-%H%M')
    layer.zipName = fileName + timeStr + ".zip" # Store this here so it can be accessed later on in UI population
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
        ctypes.windll.user32.MessageBoxW(0, u"Problems creating archive", u"Error", 0x0 | 0x10)
        return False
