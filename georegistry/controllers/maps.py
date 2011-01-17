'Maps controller'
# Import pylons modules
from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect
# Import system modules
import logging; log = logging.getLogger(__name__)
import sqlalchemy as sa
import simplejson
import geojson
import shapely.wkb
import geoalchemy
import datetime
# Import custom modules
from georegistry import model
from georegistry.model import Session
from georegistry.lib import helpers as h, geometry_store
from georegistry.lib.base import BaseController, render


class MapsController(BaseController):

    def view(self, responseFormat='html'):
        'Assemble a map'
        # Get responseFormat
        responseFormat = responseFormat.lower()
        if responseFormat not in ['json', 'html']:
            abort(400, 'Must specify a valid responseFormat: json, html')
        if responseFormat == 'html':
            return render('/maps/index.mako')
        # Authenticate via personID or key
        personID = h.getPersonIDViaKey()
        # Load srid
        proj4 = request.params.get('proj4', '')
        try:
            srid = model.getSRID(proj4)
        except model.GeoRegistryError, error:
            abort(400, str(error))
        # Load tags
        try:
            tags = model.getTags(request.params.get('tags', ''))
        except model.GeoRegistryError, error:
            abort(400, str(error))
        # Load query string
        queryStringHash = model.hashString(request.query_string)
        # Load cached map
        cachedMap = Session.query(model.Map).filter_by(query_hash=queryStringHash).first()
        # If we do not have a cached map or the cached map is not current,
        if not cachedMap or not cachedMap.when_updated or cachedMap.when_updated < max(x.when_updated for x in tags):
            # Initialize
            featureQuery = Session.query(model.Feature.id, geoalchemy.functions.wkb(geoalchemy.functions.transform(model.Feature.geometry, srid)), model.Feature.properties).join(model.Feature.tags).filter(model.Tag.id.in_([x.id for x in tags])).filter(model.getFeatureFilter(personID))
            # Load bounding box
            bbox = request.params.get('bbox', '')
            # If a bounding box is specified,
            if bbox:
                # Expand
                try:
                    minLatitude, minLongitude, maxLatitude, maxLongitude = [float(x) for x in bbox.split(',')]
                except ValueError:
                    abort(400, 'Could not parse bbox as four floats separated by commas')
                # Query using bounding box
                featureQuery = featureQuery.filter(model.Feature.geometry.op('&&')(sa.func.setsrid(sa.func.box2d('BOX(%s %s, %s %s)' % (minLatitude, minLongitude, maxLatitude, maxLongitude)), 4326)))
            # Load simplified
            simplified = request.params.get('simplified', 1)
            try:
                simplified = int(simplified)
            except ValueError:
                abort(400, 'Could not parse simplified=%s as an integer' % simplified)
            # If simplification is desired and the projection is in meters,
            if simplified and '+units=m' in proj4:
                # If a bounding box is specified,
                if bbox:
                    transformPoint = geometry_store.getTransformPoint(geometry_store.proj4LL, geometry_store.proj4SM)
                    x1, y1 = transformPoint(minLongitude, minLatitude)
                    x2, y2 = transformPoint(maxLongitude, maxLatitude)
                    metersPerPixel = min(abs(x2 - x1), abs(y2 - y1)) / 256.
                # If a bounding box is not specified,
                else:
                    metersPerPixel = 0.1
                # Define
                simplifyShape = lambda x: x.simplify(metersPerPixel)
            # Otherwise,
            else:
                # Define
                simplifyShape = lambda x: x
            # Prepare map
            try:
                geojsonFeatures = [geojson.Feature(id=featureID, geometry=simplifyShape(shapely.wkb.loads(str(featureWKB))), properties=featureProperties) for featureID, featureWKB, featureProperties in featureQuery]
            except sa.exc.InternalError, error:
                abort(400, 'Could not execute query (%s)' % str(error))
            # Store map in cache
            cachedMap = model.Map()
            cachedMap.geojson = geojson.dumps(geojson.FeatureCollection(geojsonFeatures)).decode('utf-8')
            cachedMap.query_hash = queryStringHash
            cachedMap.when_updated = datetime.datetime.utcnow()
            Session.add(cachedMap)
            Session.commit()
        # Return
        return cachedMap.geojson.encode('utf-8')
