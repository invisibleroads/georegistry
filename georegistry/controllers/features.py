'Features controller'
# Import pylons modules
from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect
# Import system modules
import simplejson
import geojson
import geoalchemy
# Import custom modules
from georegistry import model
from georegistry.model import Session
from georegistry.lib import helpers as h
from georegistry.lib.base import BaseController, render


class FeaturesController(BaseController):

    def update(self):
        'Add new or edit existing features'
        # Authenticate via personID or key
        personID = h.getPersonIDViaKey()
        if not personID:
            abort(401, 'Please log in or provide a valid key')
        # Load srid
        try:
            srid = model.getSRID(request.params.get('proj4', ''))
        except model.GeoRegistryError, error:
            abort(400, str(error))
        # Load featureDictionaries
        try:
            featureDictionaries = geojson.loads(request.params.get('featureCollection', ''))['features']
        except simplejson.JSONDecodeError, error:
            abort(400, 'Could not parse featureCollection as geojson (%s)' % error)
        except KeyError:
            abort(400, 'Could not get features from featureCollection')
        if not featureDictionaries:
            abort(400, 'Must specify at least one feature in featureCollection')
        # Load tags
        try:
            tags = model.getTags(request.params.get('tags', ''), addMissing=True)
        except model.GeoRegistryError, error:
            abort(400, str(error))
        # Load public
        public = request.params.get('public', 0)
        try:
            public = int(public)
        except ValueError:
            abort(400, 'Could not parse public=%s as an integer' % public)
        # Make sure that the user has write access to the given featureIDs
        try:
            featureByID = dict((x.id, x) for x in model.getWritableFeatures([x.get('id') for x in featureDictionaries], personID))
        except model.GeoRegistryError, error:
            abort(400, str(error))
        # Prepare
        features = []
        # For each featureDictionary,
        for featureDictionary in featureDictionaries:
            # Expand
            featureID = featureDictionary.get('id')
            featureGeometry = featureDictionary.get('geometry')
            featureProperties = featureDictionary.get('properties', {})
            # Validate
            try:
                featureGeometryWKT = geoalchemy.utils.to_wkt(featureGeometry)
            except (KeyError, TypeError), error:
                abort(400, 'Could not parse geometry=%s' % featureGeometry)
            # If featureID is specified, load it
            if featureID is not None:
                try:
                    featureID = int(featureID)
                except ValueError:
                    abort(400, 'Could not parse featureID=%s as an integer' % featureID)
                feature = featureByID[featureID]
            # If featureID is not specified, add it
            else:
                feature = model.Feature()
                feature.owner_id = personID
                Session.add(feature)
            # Set
            feature.properties = featureProperties
            feature.scope = model.scopePublic if public else model.scopePrivate
            feature.geometry = geoalchemy.WKTSpatialElement(featureGeometryWKT, srid)
            feature.tags = tags
            # Append
            features.append(feature)
        # Update timestamps for each tag
        for tag in tags:
            tag.updateTimestamp()
        # Commit
        Session.commit()
        # Return
        return '\n'.join(str(x.id) for x in features)

    def delete(self):
        'Delete features'
        # Authenticate via personID or key
        personID = h.getPersonIDViaKey()
        if not personID:
            abort(401, 'Please log in or provide a valid key')
        # Load featureIDs
        featureIDs = request.params.get('featureIDs', '').splitlines()
        if not featureIDs:
            abort(400, 'Must specify at least one featureID in featureIDs')
        # Make sure that the user has write access to the given featureIDs
        try:
            model.getWritableFeatures(featureIDs, personID)
        except model.GeoRegistryError, error:
            abort(400, str(error))
        # Update timestamps for each tag
        for tag in Session.query(model.Tag).join(model.Tag.features).filter(model.Feature.id.in_(featureIDs)):
            tag.updateTimestamp()
        # Delete
        Session.execute(model.feature_tags_table.delete(model.feature_tags_table.c.feature_id.in_(featureIDs)))
        Session.execute(model.features_table.delete(model.features_table.c.id.in_(featureIDs)))
        Session.commit()
