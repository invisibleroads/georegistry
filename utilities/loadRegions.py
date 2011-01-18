#!/usr/bin/env python2.7
"""
Command-line script to load GADM regions into the database

Use the first argument to specify the path of the folder
containing the GADM shapefiles
"""
# Import system modules
import os
import re
import csv
import glob
import osgeo.osr
import itertools
import geoalchemy
# Import custom modules
import script_process
from georegistry import model
from georegistry.lib import store, geometry_store
from georegistry.model import Session


# Core

def run(shapePath):
    'Load regions from shapefile'
    # Parse shapePath
    shapeName = store.extractFileBaseName(shapePath)
    countryAlpha3, administrativeLevel = re.match(r'(.*)_adm(\d+)', shapeName).groups()
    countryAlpha3 = countryAlpha3.upper()
    administrativeLevel = int(administrativeLevel)
    # Load
    countryName = countryPackByAlpha3[countryAlpha3][0]
    proj4, shapelyGeometries, fieldPacks, fieldDefinitions = geometry_store.load(shapePath)
    # Initialize
    srid = getSRID(proj4)
    areaCount = 0
    # Make tags
    tagTexts = [
        countryName + (u': Administrative Level %s' % administrativeLevel if administrativeLevel > 0 else ''),
    ]
    if administrativeLevel == 0:
        tagTexts.append(u'* countries')
    tags = model.getTags('\n'.join(tagTexts), addMissing=True)
    # For each geometry,
    for shapelyGeometry, fieldPack in itertools.izip(shapelyGeometries, fieldPacks):
        # Make feature
        feature = model.Feature()
        feature.owner_id = personID
        feature.geometry = geoalchemy.WKBSpatialElement(buffer(shapelyGeometry.wkb), srid)
        feature.scope = model.scopePublic
        feature.properties = dict((fieldName, fieldValue) for fieldValue, (fieldName, fieldType) in itertools.izip(fieldPack, fieldDefinitions))
        feature.tags = tags
        Session.add(feature)
        # Increment
        areaCount += 1
    # Commit
    Session.commit()
    # Return
    return '%s: %s' % (shapeName, areaCount)

def simplifyProj4(proj4):
    'Simplify proj4 string'
    spatialReference = osgeo.osr.SpatialReference()
    if spatialReference.ImportFromProj4(str(proj4)) != 0:
        return
    return spatialReference.ExportToProj4()

def getSRID(proj4):
    'Convert proj4 to srid'
    # Simplify
    proj4Simplified = simplifyProj4(proj4)
    if not proj4Simplified:
        raise model.GeoRegistryError('Must specify valid proj4 spatial reference')
    # For each spatial reference,
    for proj4Standard, srid in Session.execute('SELECT proj4text, srid FROM spatial_ref_sys'):
        # Skip empty proj4s
        if not proj4Standard.strip():
            continue
        # If we have a match,
        if simplifyProj4(proj4Standard) == proj4Simplified:
            return srid
    # If we have no matches, raise exception
    raise model.GeoRegistryError('Could not recognize proj4 spatial reference')


# If we are running standalone,
if __name__ == '__main__':
    # Parse
    optionParser = script_process.buildOptionParser()
    options, arguments = optionParser.parse_args()
    # Load countryPackByAlpha3
    countryPackByAlpha3 = {}
    countryPath = store.expandBasePath('utilities/countries.csv')
    for countryName, countryAlpha2, countryAlpha3 in csv.reader(open(countryPath, 'rt')):
        countryPackByAlpha3[countryAlpha3.upper()] = countryName, countryAlpha2.upper()
    # Initialize
    script_process.initialize(options)
    person = Session.query(model.Person).filter_by(username='administrator').first()
    personID = person.id
    folderPath = arguments[0] if arguments else ''
    # For each filePath,
    for filePath in sorted(glob.glob(os.path.join(folderPath, '*.shp'))):
        # Run
        print run(filePath)
