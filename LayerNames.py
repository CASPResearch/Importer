# Set up mappings from concat variables to their intended layer names
# Constructed in code from lithology type + table type where:
#   lithology == ignmeta or sedimentary
#   tableVariety == samples, ages, analyses, or raw

layerNames = {
    "ignmetasample": "ignmeta_samples",
    "ignmetaage": "ignmeta_ages",
    "ignmetaanalysis": "ignmeta_analyses",
    "ignmetaraw": "ignmeta_raw",
    "ignmetasampleagemerge": "ignmeta_sample_ages_merge",
    "ignmetasamplerawmerge": "ignmeta_sample_raw_merge",
    "sedimentarysample": "sedimentary samples",
    "sedimentaryage": "sedimentary ages",
    "sedimentaryanalysis": "sedimentary analyses",
    "sedimentaryraw": "sedimentary raw data",
    "sedimentarysampleagemerge": "sedimentary sample summary ages master",
    "sedimentarysamplerawmerge": "sedimentary sample raw data master"
}
