'Tests for feature controller'
# Import system modules
import simplejson
import geoalchemy
import geojson
import urllib
# Import custom modules
from georegistry import model
from georegistry.lib import geometry_store
from georegistry.model import Session
from georegistry.tests import *


# Prepare people
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
# Prepare features
features = []
featurePacks = [
    (people[0].id, geoalchemy.WKTSpatialElement('POINT (0 1)')),
    (people[1].id, geoalchemy.WKTSpatialElement('POINT (1 0)')),
]
for featurePack in featurePacks:
    feature = Session.query(model.Feature).filter_by(owner_id=featurePack[0]).first()
    if not feature:
        feature = model.Feature()
        feature.owner_id = featurePack[0]
        feature.geometry = featurePack[1]
        Session.add(feature)
        Session.commit()
    features.append(feature)
# Set constants
person1Key = people[0].key
person2Key = people[1].key
feature1ID = features[0].id
feature2ID = features[1].id


class TestFeaturesController(TestController):

    def tearDown(self):
        Session.execute(model.feature_tags_table.delete())
        Session.execute(model.features_table.delete())
        Session.execute(model.tags_table.delete())
        Session.commit()

    def assertEqualJSON(self, response, isOk):
        'Assert response as JSON'
        responseData = simplejson.loads(response.body)
        if responseData['isOk'] != isOk:
            print responseData
        self.assertEqual(responseData['isOk'], isOk)
        return responseData

    def test_update(self):
        'Make sure we can update features properly'
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
        # Expect error if we try to update features that do not exist
        self.assertEqualJSON(self.app.post(url('feature_update'), dict(key=person1Key, proj4=geometry_store.proj4LL, featureCollection=geojson.dumps(geojson.FeatureCollection([geojson.Feature(id=0, geometry=geojson.Point((0, 0)))])), tags=simplejson.dumps(['tag1']))), 0)
        # Expect error if we try to update features that we do not own
        self.assertEqualJSON(self.app.post(url('feature_update'), dict(key=person1Key, proj4=geometry_store.proj4LL, featureCollection=geojson.dumps(geojson.FeatureCollection([geojson.Feature(id=feature2ID, geometry=geojson.Point((0, 0)))])), tags=simplejson.dumps(['tag1']))), 0)
        # Expect error if we submit invalid geometry
        self.assertEqualJSON(self.app.post(url('feature_update'), dict(key=person1Key, proj4=geometry_store.proj4LL, featureCollection=geojson.dumps(geojson.FeatureCollection([geojson.Feature(id=feature2ID, geometry=None)])), tags=simplejson.dumps(['tag1']))), 0)
        # Check that an example request works properly
        responseData = self.assertEqualJSON(self.app.post(url('feature_update'), dict(key=person1Key, proj4=geometry_store.proj4LL, featureCollection=geojson.dumps(geojson.FeatureCollection([geojson.Feature(geometry=geojson.Point((0, 0)), properties={'population': 100})])), tags=simplejson.dumps(['tag1']))), 1)
        featureID = responseData['featureIDs'][0]
        responseData = self.assertEqualJSON(self.app.post(url('feature_update'), dict(key=person1Key, proj4=geometry_store.proj4LL, featureCollection=geojson.dumps(geojson.FeatureCollection([geojson.Feature(id=featureID, geometry=geojson.Point((0, 0)), properties={'population': 1000})])), tags=simplejson.dumps(['tag1']))), 1)
        feature = Session.query(model.Feature).get(featureID)
        self.assertEqual(feature.properties['population'], 1000)

    def test_delete(self):
        'Make sure we can delete features properly'
        # Expect error if we try to login without authentication
        self.assertEqualJSON(self.app.delete(url('feature_delete')), 0)
        self.assertEqualJSON(self.app.delete(url('feature_delete', key='')), 0)
        # Expect error if we try to delete features that do not exist
        self.assertEqualJSON(self.app.delete(url('feature_delete', key=person1Key, featureIDs=simplejson.dumps([0]))), 0)
        # Expect error if we try to delete features that we do not own
        self.assertEqualJSON(self.app.delete(url('feature_delete', key=person1Key, featureIDs=simplejson.dumps([feature2ID]))), 0)
        # Check that an example request works properly
        responseData = self.assertEqualJSON(self.app.delete(url('feature_delete', key=person1Key, featureIDs=simplejson.dumps([feature1ID]))), 1)
        self.assertEqual(Session.query(model.Feature).get(feature1ID), None)
