"""
Command-line script to load GADM features into the database

Use the first argument to specify the path of the folder
containing the GADM shapefiles
"""
import os
import re
import csv
import glob
import zipfile
import functools
import itertools
import archiveIO
import geometryIO
import transaction
from osgeo import ogr, osr
from geoalchemy import WKBSpatialElement

import script_process
from georegistry.models import db, User, Feature, get_tags, scopePublic, ApplicationError


countryFile = open(script_process.expand_path('utilities/countries.csv'), 'rt')
countryByAlpha3 = {x[2]: x[0] for x in csv.reader(countryFile)}


def run(zipPath, ownerID, verbose=True):
    'Load features from GADM archive'
    with archiveIO.TemporaryFolder() as temporaryFolder:
        with zipfile.ZipFile(zipPath) as zipFile:
            zipFile.extractall(temporaryFolder)
        for shapePath in glob.glob(os.path.join(temporaryFolder, '*.shp')):
            load(shapePath, ownerID, verbose)


def load(shapePath, ownerID, verbose):
    'Load features from GADM shapefile'
    # Parse
    shapeName = os.path.splitext(os.path.basename(shapePath))[0]
    alpha3, administrativeLevel = re.match(r'(.*)_adm(\d+)', shapeName).groups()
    alpha3 = alpha3.upper()
    administrativeLevel = int(administrativeLevel)
    # Load
    try:
        countryName = countryByAlpha3[alpha3].decode('utf-8')
    except KeyError:
        raise ApplicationError('%s: Unable to match country code' % shapeName)
    proj4, shapelyGeometries, fieldPacks, fieldDefinitions = geometryIO.load(shapePath)
    srid = get_srid(proj4)
    # Make tags
    tagText = countryName
    if administrativeLevel:
        tagText += u' Administrative Level %s' % administrativeLevel
    tags = get_tags(tagText, addMissing=True)
    # For each geometry,
    featureCount = 0
    for shapelyGeometry, fieldPack in itertools.izip(shapelyGeometries, fieldPacks):
        # Gather attributes
        attributes = {}
        for fValue, (fName, fType) in itertools.izip(fieldPack, fieldDefinitions):
            if fType == ogr.OFTString and fValue:
                fValue = fValue.decode('latin-1')
            attributes[fName] = fValue
        if administrativeLevel > 0:
            name = attributes['NAME_%s' % administrativeLevel]
        else:
            name = attributes['NAME_ENGLI']
        attributes['Name'] = name
        # Make feature
        db.add(Feature(
            user_id=ownerID, 
            attributes=attributes,
            scope=scopePublic,
            geometry=WKBSpatialElement(buffer(shapelyGeometry.wkb), srid),
            tags=tags))
        # Increment
        featureCount += 1
    # Show feedback
    if verbose:
        print '%s: %s' % (shapeName, featureCount)


def get_srid(proj4):
    'Convert proj4 to srid'
    # Simplify
    proj4 = simplify_proj4(proj4)
    # For each spatial reference,
    for proj4Standard, srid in db.execute('SELECT proj4text, srid FROM spatial_ref_sys'):
        # Skip empty proj4s
        if not proj4Standard.strip():
            continue
        # If we have a match,
        if simplify_proj4(proj4Standard) == proj4:
            return srid
    # If we have no matches, raise exception
    else:
        raise ApplicationError("Could not find srid corresponding to proj4='%s'" % proj4)


def simplify_proj4(proj4):
    'Simplify proj4 string'
    spatialReference = osr.SpatialReference()
    try:
        spatialReference.ImportFromProj4(str(proj4))
    except RuntimeError:
        raise ApplicationError("Could not parse proj4='%s'" % proj4)
    else:
        return spatialReference.ExportToProj4()


# If we are running standalone,
if __name__ == '__main__':
    # Parse
    argumentParser = script_process.ArgumentParser(
        description='Load GADM features into the database')
    argumentParser.add_argument('-u',
        dest='username', 
        help='assign features to the corresponding user',
        metavar='USERNAME')
    argumentParser.add_argument('paths',
        help='load the specified folders and/or files',
        metavar='PATH',
        nargs='+')
    args = argumentParser.parse_args()
    # Load
    script_process.initialize(args)
    if args.username:
        userFilter = User.username == args.username
    else:
        userFilter = User.is_super == True
    user = db.query(User).filter(userFilter).first()
    userID = user.id
    run_ = functools.partial(run, ownerID=userID, verbose=args.verbose)
    # Run
    for path in args.paths:
        if path.endswith('.zip'):
            run_(path)
            continue
        for filePath in sorted(glob.glob(os.path.join(path, '*.zip'))):
            run_(filePath)
    # Commit
    transaction.commit()
