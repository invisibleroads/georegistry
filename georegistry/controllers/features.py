'Features controller'
# Import pylons modules
from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect
from pylons.decorators import jsonify
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

    @jsonify
    def update(self):
        'Add new or edit existing features'
        # Authenticate via personID or key
        personID = h.getPersonIDViaKey()
        if not personID:
            return dict(isOk=0, message='Please log in or provide a valid key')
        # Load srid
        proj4 = model.simplifyProj(request.POST.get('proj4', ''))
        if not proj4:
            return dict(isOk=0, message='Must specify valid proj4 spatial reference')
        try:
            srid = model.loadSRIDByProj4()[proj4]
        except KeyError:
            return dict(isOk=0, message='Could not recognize proj4 spatial reference')
        # Load featureDictionaries
        try:
            featureDictionaries = geojson.loads(request.POST.get('featureCollection', ''))['features']
        except simplejson.JSONDecodeError, error:
            return dict(isOk=0, message='Could not parse featureCollection as geojson (%s)' % error)
        except KeyError:
            return dict(isOk=0, message='Could not get features from featureCollection')
        if not featureDictionaries:
            return dict(isOk=0, message='Must have at least one feature')
        # Load tagTexts
        try:
            tagTexts = simplejson.loads(request.POST.get('tags', ''))
        except simplejson.JSONDecodeError, error:
            return dict(isOk=0, message='Could not parse tags as json (%s)' % error)
        if not tagTexts:
            return dict(isOk=0, message='Must have at least one tag')
        # Load isPublic
        isPublic = request.POST.get('isPublic', 0)
        # Process tags
        try:
            tags = model.processTags(tagTexts)
        except ValueError, error:
            return dict(isOk=0, message=str(error))
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
                return dict(isOk=0, message='Could not parse geometry=%s' % featureGeometry)
            # If featureID is specified,
            if featureID is not None:
                try:
                    featureID = int(featureID)
                except ValueError:
                    return dict(isOk=0, message='Could not parse featureID=%s as integer' % featureID)
                # Load feature
                feature = Session.query(model.Feature).get(featureID)
                # If it doesn't exist,
                if not feature:
                    return dict(isOk=0, message='Could not modify featureID=%s because it does not exist' % featureID)
                # If the user is not the owner,
                elif feature.owner_id != personID:
                    return dict(isOk=0, message='Could not modify featureID=%s because you are not the owner' % featureID)
            # If featureID is not specified,
            else:
                # Make feature
                feature = model.Feature()
                feature.owner_id = personID
                # Add feature
                Session.add(feature)
            # Set
            feature.properties = featureProperties
            feature.scope = model.scopePublic if isPublic else model.scopePrivate
            feature.geometry = geoalchemy.WKTSpatialElement(featureGeometryWKT, srid)
            feature.tags = tags
            # Append
            features.append(feature)
        # Commit
        Session.commit()
        # Load featureIDs inefficiently
        featureIDs = [x.id for x in features]
        # Return
        return dict(isOk=1, featureIDs=featureIDs)

    def delete(self):
        pass
