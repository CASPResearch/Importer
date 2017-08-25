from PrimaryUIFunctions import UIFunctions
from SecondaryUI import Ui_Dialog
from PyQt4 import QtGui, QtSql
from pyspatialite import dbapi2 as db
from Backup import backup

import os
import Utils

class UIFunctions2(UIFunctions):
    # We need to duplicate the __init__ so it uses this file's Ui_Dialog import, not the original's
    def __init__(self, iface):
        QtGui.QDialog.__init__(self)

        self.iface = iface

        # Get the main project directory
        self.saveDir = os.getcwd()

        # Create the main UI at launch. It hides itself as part of the creation process
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

    def run(self, layer):
        print "run function in secondary"
        # First, check if we really want to be run
        layer.finalLayer, layer.sampleLayer = Utils.mergeNeeded(layer)
        if not layer.finalLayer: # sampleLayer is also False, but we need only check one
            return

        self.layer = layer  # Save this so button functions can pick it up and pass it forwards

        # Create a copy of our layer's target in a zip file, indexed by date and time
        if not backup(layer.finalLayer):
            return

        print "Backup complete"

        # Create a temporary layer which is the result of merging the source and target
        # The user can check this over for mistakes before committing
        #self.temp = Utils.mergeSQLs(layer, layer.sampleLayer)
        #if not self.temp:
            #return

        # Show that temporary layer's content table
        #self.iface.showAttributeTable(self.temp)

        # Populate the UI with appropriate data, and show it
        self.fillFields(layer)
        self.show()

    def fillFields(self, layer):
        # Display Lithology and layer type
        lith = getattr(self.ui, "radioButton" + layer.cat)
        lith.setChecked(True)

        lType = getattr(self.ui, "radioButton" + layer.tableVariety)
        lType.setChecked(True)

        self.ui.projectPathField.setText(self.saveDir)

        # Handle the master layer
        self.fillLayerRow(layer, "master")

        # Handle the samples layer
        self.fillLayerRow(layer.sampleLayer, "samples")

        # Handle destination layer
        self.fillLayerRow(layer.finalLayer, "destination")

        # Handle the destination file name
        name = Utils.getLayerFilename(layer.finalLayer, False)
        self.ui.destinationFilenameField.setText(name)

        # Handle the temporary layer
        #self.fillLayerRow(self.temp, "temp")

        # Handle the backup path
        self.ui.backupPathField.setText(self.saveDir + r"\Backups")

        # Handle the backup filename
        self.ui.backupNameField.setText(layer.finalLayer.zipName)

        self.setupButtonFunctions()

    def proceedButtonFunction(self):
        self.appendToMerge(self.layer)
        self.handleClose()

    def appendToMerge(self, layer):
        print "Appendtomerge"
        myPath = Utils.getLayerPath(layer, True)
        samplePath = Utils.getLayerPath(layer.sampleLayer, True)
        finalPath = Utils.getLayerPath(layer.finalLayer, True)

        print "paths are"
        print myPath
        print samplePath
        print finalPath

        myName = Utils.getLayerFilename(layer, False)
        print "names"
        print myName

        if myName != "ignmeta_ages" and myName != "ignmeta_raw":
            print "Bad name, returning"
            return

        sampleName = Utils.getLayerFilename(layer.sampleLayer, False)
        finalName = Utils.getLayerFilename(layer.finalLayer, False)

        print sampleName
        print finalName

        #db = QtSql.QSqlDatabase.addDatabase('QSQLITE')
        #db.setDatabaseName(myPath)
        conn = db.connect(myPath)
        if not conn:
            print "Can't open db, returning"
            return

        cur = conn.cursor()

        #query = QtSql.QSqlQuery()
        #print "query made"
        print "cursor made"
        #print query.exec_('attach database "{}" as "{}"'.format(samplePath, sampleName))
        print cur.execute('attach database "{}" as "{}"'.format(samplePath, sampleName))
        print 'attached "{}" as "{}"'.format(samplePath, sampleName)

        #print query.exec_('attach database "{}" as "{}"'.format(finalPath, finalName))
        print cur.execute('attach database "{}" as "{}"'.format(finalPath, finalName))
        print 'attached "{}" as "{}"'.format(finalPath, finalName)

        # Next we build our query. This is going to get a bit mad.
        print "Starting string construction"
        queryString = ""
        if myName == "ignmeta_ages":
            queryString = "insert into {} select {}.ogc_fid, {}.sampleid, ".format(finalName, myName, myName)
        elif myName == "ignmeta_raw":
            queryString = "insert into {} select {}.ogc_fid, samplealiquotid, {}.sampleid, ".format(finalName, myName, myName)

        print queryString

        # for each field in layer, except some, concat
        for field in layer.fields():
            name = field.name()
            if name != "ogc_fid" and name != "sampleid" and name != "geometry" and name != "samplealiquotid":
                queryString = queryString + name + ", "

        print queryString

        for field in layer.sampleLayer.fields():
            name = field.name()
            if name != "ogc_fid" and name != "sampleid" and name != "geometry" and name != "samplealiquotid":
                if name == "longitude" or name == "latitude":
                    name = "cast({} as double) as {}".format(name, name)

                if name == "sampleno" and myName == "ignmeta_raw":
                    continue

                queryString = queryString + name + ", "

        print queryString

        queryString = (queryString +
                       "{}.GEOMETRY "
                       "from {} join {} "
                       "on ({}.sampleid={}.sampleid) "
                       "where {}.sampleid IN (select sampleid from {}) "
                       "and {}.sampleid not in (select sampleid from {})"
        ).format(sampleName, myName, sampleName, myName, sampleName, myName, sampleName, myName, finalName)

        print queryString

        #print query.exec_(queryString)
        print cur.execute(queryString)
        conn.commit()
        #print db.close()

        print "done"


        # Don't want second sampleno for raw


        # Refresh the map view
        if self.iface.mapCanvas().isCachingEnabled():
            layer.finalLayer.setCacheImage(None)
        else:
            self.iface.mapCanvas().refresh()
