'Maps controller'
# Import pylons modules
from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect
# Import system modules
import logging; log = logging.getLogger(__name__)
# Import custom modules
from georegistry.lib.base import BaseController, render


class MapsController(BaseController):

    def view(self, responseFormat='html', X=None, Y=None, Z=None):
    # GET    /maps.json (key=string, proj4=string, tags=strings) --> featureCollection=geojson
    # GET    /maps/{Z}/{X}/{Y}.json (key=string, proj4=string, tags=strings) --> featureCollection=geojson
        'Assemble a map'
        # Authenticate via personID or key
        personID = h.getPersonIDViaKey()
        # Load srid
        # Load tags
        # If we do not have a cached map or the cached map is not current,
            # Generate map 
            # Store map in cache
        # If the user wants html,
        # If the user wants json,

# Add bounding box
# Add simplify



import simplejson
import geojson
# Import custom modules
from georegistry import model
from georegistry.model import Session
from georegistry.lib.base import BaseController, render


class RegionsController(BaseController):

    def index(self, responseFormat='html'):
        'Return region summary'
        # Load countries
        c.countryPacks = Session.query(model.Country.code_alpha2, model.Country.name).all()
        c.countryCode = c.countryPacks[0][0]
        # If the user wants html,
        if responseFormat == 'html':
            return render('/regions/index.mako')

    def show(self, countryCode, responseFormat='json'):
        'Return region details'
        # Load country
        country = Session.query(model.Country).filter((model.Country.code_alpha2==countryCode) | (model.Country.code_alpha3==countryCode)).first()
        if not country:
            message = 'Could not find a country matching %s' % countryCode
            if responseFormat == 'json':
                return simplejson.dumps(dict(isOk=0, message=message))
            else:
                return message
        countryLongitude, countryLatitude = country.getCenter()
        countryLeft, countryBottom, countryRight, countryTop = country.getBox()
        # If the user wants json,
        if responseFormat == 'json':
            # Load
            regionLevelCount = Session.query(model.Region.level.distinct()).filter(model.Region.country_id==country.id).count()
            # Return json
            return simplejson.dumps(dict(
                isOk=1,
                countryName=country.name,
                countryLongitude=countryLongitude,
                countryLatitude=countryLatitude,
                countryLeft=countryLeft,
                countryBottom=countryBottom,
                countryRight=countryRight,
                countryTop=countryTop,
                regionLevelCount=regionLevelCount,
            ))
        # If the user wants geojson,
        elif responseFormat == 'geojson':
            # Load
            regionLevel = request.params.get('regionLevel', 0)
            # Return geojson
            return geojson.dumps(geojson.FeatureCollection([geojson.Feature(
                id='r%s' % regionID,
                geometry=geojson.loads(regionGeoJSON), # Might be inefficient here
                properties={},
            ) for regionID, regionGeoJSON in Session.query(model.Region.id, model.Region.geometry.geojson).filter(model.Region.country_id==country.id).filter(model.Region.level==regionLevel)]))
        # If the user wants some other format,
        else:
            # Show an error message for now
            return 'Supported formated are json and geojson'
