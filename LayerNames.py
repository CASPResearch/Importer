# Set up mappings from concat variables to their intended layer names
# Constructed in code from lithology type + table type where:
#   lithology == igneous or sedimentary
#   tableVariety == samples, ages, analyses, or excel

layerNames = {
    "igneoussample": "igneous samples",
    "igneousage": "igneous ages",
    "igneousanalysis": "igneous analyses",
    "igneousexcel": "igneous raw data",
    "igneoussampleagemerge": "igneous sample summary ages master",
    "igneoussamplerawmerge": "igneous sample raw data master",
    "sedimentarysample": "sedimentary samples",
    "sedimentaryage": "sedimentary ages",
    "sedimentaryanalysis": "sedimentary analyses",
    "sedimentaryexcel": "sedimentary raw data",
    "sedimentarysampleagemerge": "sedimentary sample summary ages master",
    "sedimentarysamplerawmerge": "sedimentary sample raw data master"
}
