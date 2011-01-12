#!/usr/bin/env python2.6
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
import geoalchemy
import shapely.geometry
# Import custom modules
import script_process
from georegistry import model
from georegistry.lib import geometry_store, store
from georegistry.model import Base, Session


def run(shapePath):
    'Load regions from shapefile'
    # Parse shapePath
    shapeName = store.extractFileBaseName(shapePath)
    alpha3, level = re.match(r'(.*)_adm(\d+)', shapeName).groups()
    alpha3 = alpha3.upper()
    level = int(level)
    # Load country
    countryName, alpha2 = countryPackByAlpha3[alpha3]
    country = Session.query(model.Country).filter(model.Country.name==countryName).first()
    if not country:
        print 'Adding country: ' + countryName
        country = model.Country(countryName, alpha2, alpha3)
        Session.add(country)
        Session.commit()
    # Load geometries
    proj4, geometries = geometry_store.load(shapePath)[:2]
    # Initialize
    srid = sridByProj4[model.simplifyProj(proj4)]
    regionCount = 0
    # For each geometry,
    for geometry in geometries:
        # Prepare
        geometry = geoalchemy.WKBSpatialElement(buffer(geometry.wkb), srid)
        # Add region
        Session.add(model.Region(geometry, country.id, level))
        regionCount += 1
    # If we are looking at the country outline,
    if level == 0:
        # Merge geometries
        countryGeometry = reduce(lambda x, y: x.union(y), geometries)
        # Compute center
        country.center = geoalchemy.WKBSpatialElement(buffer(countryGeometry.centroid.wkb), srid)
        # Compute bounds
        left, bottom, right, top = countryGeometry.bounds
        country.bound_lb = geoalchemy.WKBSpatialElement(buffer(shapely.geometry.Point(left, bottom).wkb), srid)
        country.bound_rt = geoalchemy.WKBSpatialElement(buffer(shapely.geometry.Point(right, top).wkb), srid)
    # Commit
    Session.commit()
    # Return
    return '%s: %s regions' % (shapeName, regionCount)


def loadCountryPackByAlpha3():
    'Generate a dictionary mapping alpha3 to countryPack'
    # Initialize
    countryPackByAlpha3 = {}
    countryPath = store.expandBasePath('utilities/countries.csv')
    # For each row,
    for countryName, alpha2, alpha3 in csv.reader(open(countryPath, 'rt')):
        countryPackByAlpha3[alpha3.upper()] = countryName, alpha2.upper()
    # Return
    return countryPackByAlpha3


# If we are running standalone,
if __name__ == '__main__':
    # Parse
    optionParser = script_process.buildOptionParser()
    options, arguments = optionParser.parse_args()
    # Initialize
    script_process.initialize(options)
    sridByProj4 = model.loadSRIDByProj4()
    countryPackByAlpha3 = loadCountryPackByAlpha3()
    folderPath = arguments[0] if arguments else ''
    # For each shapePath,
    for shapePath in sorted(glob.glob(os.path.join(folderPath, '*.shp'))):
        # Run
        print run(shapePath)
