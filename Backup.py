# This file contains a function to create a time indexed backup of a given layer
import os
import datetime
import zipfile

def backup(layer):
    master = Utils.getLayerByName(layer.masterLayer)

    (filePath, fileName) = os.path.split(master.dataProvider().dataSourceUri())

    fileName = os.path.splitext(fileName)[0] # Remove the file extension

    # Create a Backups folder if there isn't one, to store the zips
    bkupadd = os.path.join(filePath, "Backups")
    if not os.path.exists(bkupadd):
        os.makedirs(bkupadd)

    timeStr = datetime.datetime.now().strftime('-%Y%m%d-%H%M')
    backupPath = os.path.join(bkupadd, fileName + timeStr + ".zip")

    # Create the zip
    try:
        zf = zipfile.ZipFile(backupPath, 'w')
        for file in os.listdir(filePath):
            baseName = os.path.basename(file)
            name, ext = os.path.splitext(baseName)
            if name == fileName:
                path = os.path.join(filePath, baseName)
                zf.write(path, baseName) # Compression will depend on if zlib is found or not
        zf.close()
    except:
        self.iface.messageBar().pushMessage("Error","Problems creating archive. Verify this is a file layer and not a database layer.", 2, duration=5)