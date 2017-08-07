# DataImporter
# A QGIS plugin written in Python which imports data from a database or table into QGIS

# Initializes the plugin so that qGIS can see it
def classFactory(iface):
    # load AccAssess class from file AccAssess.py
    from ImporterMain import Importer
    return Importer(iface)