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
from georegistry.lib import helpers as h
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
        srid = request.params.get('srid', '')
        try:
            proj4 = model.validateSRID(srid)
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
            # Load bboxFormat
            bboxFormat = request.params.get('bboxFormat', 'yxyx')
            if bboxFormat not in ['yxyx', 'xyxy']:
                abort(400, 'Must specify a valid bboxFormat: yxyx, xyxy')
            # Load bounding box
            bbox = request.params.get('bbox', '')
            # If a bounding box is specified,
            if bbox:
                # Expand
                try:
                    terms = [float(x) for x in bbox.split(',')]
                    if bboxFormat == 'yxyx':
                        minY, minX, maxY, maxX = terms
                    else:
                        minX, minY, maxX, maxY = terms
                except ValueError:
                    abort(400, 'Could not parse bbox as four floats separated by commas')
                # Define restriction
                restrict = lambda x: x.filter(model.Feature.geometry.op('&&')(geoalchemy.functions.transform(sa.func.setsrid(sa.func.box2d('BOX(%s %s, %s %s)' % (minY, minX, maxY, maxX)), srid), model.databaseSRID)))
            # If a bounding box is not specified,
            else:
                restrict = lambda x: x
            # Load simplified
            simplified = request.params.get('simplified', 1)
            try:
                simplified = int(simplified)
            except ValueError:
                abort(400, 'Could not parse simplified=%s as an integer' % simplified)
            # If simplification is desired,
            if simplified:
                # If a bounding box is specified,
                if bbox:
                    # Convert bounding box to a metric coordinate system
                    try:
                        multiPoint = shapely.wkb.loads(str(Session.execute(geoalchemy.functions.wkb(geoalchemy.functions.transform(geoalchemy.WKTSpatialElement('MULTIPOINT(%s %s, %s %s)' % (minY, minX, maxY, maxX), srid), 3857))).fetchone()[0]))
                    except sa.exc.InternalError:
                        Session.rollback()
                        y1, x1, y2, x2 = -20037508.34, -20037508.34, 20037508.34, 20037508.34
                    else:
                        y1, x1 = multiPoint.geoms[0].coords[0]
                        y2, x2 = multiPoint.geoms[1].coords[0]
                    metersPerPixel = min(abs(x2 - x1), abs(y2 - y1)) / 256.
                # If a bounding box is not specified,
                else:
                    metersPerPixel = 0.2
                # Define transformation in a metric coordinate system
                simplify = lambda x: sa.func.ST_SimplifyPreserveTopology(geoalchemy.functions.transform(x, 3857), metersPerPixel)
            # If simplification is not desired,
            else:
                simplify = lambda x: x
            # Prepare query
            featureQuery = restrict(Session.query(model.Feature.id, geoalchemy.functions.wkb(geoalchemy.functions.transform(simplify(model.Feature.geometry), srid)), model.Feature.properties).join(model.Feature.tags).filter(model.Tag.id.in_([x.id for x in tags])).filter(model.getFeatureFilter(personID)))
            # Prepare map
            try:
                geojsonFeatures = [geojson.Feature(id=featureID, geometry=shapely.wkb.loads(str(featureWKB)), properties=featureProperties) for featureID, featureWKB, featureProperties in featureQuery]
            except sa.exc.InternalError, error:
                abort(400, 'Could not execute query (%s)' % str(error))
            # Store map in cache
            cachedMap = model.Map()
            cachedMap.geojson = unicode(geojson.dumps(geojson.FeatureCollection(geojsonFeatures)), 'utf-8')
            cachedMap.query_hash = queryStringHash
            cachedMap.when_updated = datetime.datetime.utcnow()
            Session.add(cachedMap)
            Session.commit()
        # Return
        return cachedMap.geojson.encode('utf-8')
