'Tests for feature controller'
# Import system modules
import simplejson
import geoalchemy
import geojson
# Import custom modules
from georegistry import model
from georegistry.lib import geometry_store
from georegistry.model import Session
from georegistry.tests import *


# Prepare database
people = []
personPacks = [
    ('test_person1', model.hashString('test_person1'), u'test_person1', 'test_person1@example.com'),
    ('test_person2', model.hashString('test_person2'), u'test_person2', 'test_person2@example.com'),
]
for personPack in personPacks:
    person = Session.query(model.Person).filter_by(username=personPack[0]).first()
    if not person:
        person = model.Person(*personPack)
        Session.add(person)
        Session.commit()
    people.append(person)


class TestFeaturesController(TestController):

    def tearDown(self):
        Session.execute(model.feature_tags_table.delete())
        Session.execute(model.features_table.delete())
        Session.execute(model.tags_table.delete())
        Session.commit()

    def assertEqualJSON(self, response, isOk):
        'Assert response as JSON'
        responseData = simplejson.loads(response.body)
        self.assertEqual(responseData['isOk'], isOk)
        return responseData

    def test_update(self):
        'Make sure we can update features properly'
        # Initialize
        person1Key = people[0].key
        person2ID = people[1].id
        feature2 = Session.query(model.Feature).filter_by(owner_id=person2ID).first()
        if not feature2:
            feature2 = model.Feature()
            feature2.owner_id = person2ID
            feature2.geometry = geoalchemy.WKTSpatialElement('POINT (1 1)')
            Session.add(feature2)
            Session.commit()
        feature2ID = feature2.id
        # Expect error if we try to login without authentication
        self.assertEqualJSON(self.app.post(url('feature_update')), 0)
        self.assertEqualJSON(self.app.post(url('feature_update'), dict(key='')), 0)
        # Expect error if we submit invalid proj4
        self.assertEqualJSON(self.app.post(url('feature_update'), dict(key=person1Key, proj4='')), 0)
        # Expect error if we submit invalid featureCollection
        self.assertEqualJSON(self.app.post(url('feature_update'), dict(key=person1Key, proj4=geometry_store.proj4LL, featureCollection='')), 0)
        self.assertEqualJSON(self.app.post(url('feature_update'), dict(key=person1Key, proj4=geometry_store.proj4LL, featureCollection=geojson.dumps(geojson.FeatureCollection([])))), 0)
        # Expect error if we submit invalid tags
        self.assertEqualJSON(self.app.post(url('feature_update'), dict(key=person1Key, proj4=geometry_store.proj4LL, featureCollection=geojson.dumps(geojson.FeatureCollection([geojson.Feature(geometry=geojson.Point((0, 0)))])), tags='')), 0)
        self.assertEqualJSON(self.app.post(url('feature_update'), dict(key=person1Key, proj4=geometry_store.proj4LL, featureCollection=geojson.dumps(geojson.FeatureCollection([geojson.Feature(geometry=geojson.Point((0, 0)))])), tags=simplejson.dumps([]))), 0)
        self.assertEqualJSON(self.app.post(url('feature_update'), dict(key=person1Key, proj4=geometry_store.proj4LL, featureCollection=geojson.dumps(geojson.FeatureCollection([geojson.Feature(geometry=geojson.Point((0, 0)))])), tags=simplejson.dumps(['']))), 0)
        # Expect error if we try to update a feature that does not exist
        self.assertEqualJSON(self.app.post(url('feature_update'), dict(key=person1Key, proj4=geometry_store.proj4LL, featureCollection=geojson.dumps(geojson.FeatureCollection([geojson.Feature(id=0, geometry=geojson.Point((0, 0)))])), tags=simplejson.dumps(['tag1']))), 0)
        # Expect error if we try to update a feature that we do not own
        self.assertEqualJSON(self.app.post(url('feature_update'), dict(key=person1Key, proj4=geometry_store.proj4LL, featureCollection=geojson.dumps(geojson.FeatureCollection([geojson.Feature(id=feature2ID, geometry=geojson.Point((0, 0)))])), tags=simplejson.dumps(['tag1']))), 0)
        # Expect error if we submit invalid geometry
        self.assertEqualJSON(self.app.post(url('feature_update'), dict(key=person1Key, proj4=geometry_store.proj4LL, featureCollection=geojson.dumps(geojson.FeatureCollection([geojson.Feature(id=feature2ID, geometry=None)])), tags=simplejson.dumps(['tag1']))), 0)
        # Check that an example request works properly
        responseData = self.assertEqualJSON(self.app.post(url('feature_update'), dict(key=person1Key, proj4=geometry_store.proj4LL, featureCollection=geojson.dumps(geojson.FeatureCollection([geojson.Feature(geometry=geojson.Point((0, 0)))])), tags=simplejson.dumps(['tag1']))), 1)
        responseData = self.assertEqualJSON(self.app.post(url('feature_update'), dict(key=person1Key, proj4=geometry_store.proj4LL, featureCollection=geojson.dumps(geojson.FeatureCollection([geojson.Feature(id=responseData['featureIDs'][0], geometry=geojson.Point((0, 0)))])), tags=simplejson.dumps(['tag1']))), 1)
