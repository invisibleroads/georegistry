# -*- coding: utf-8 -*-
'Tests for features controller'
# Import system modules
import geoalchemy
import geojson
import urllib
# Import custom modules
from georegistry import model
from georegistry.config import parameter
from georegistry.model import Session
from georegistry.tests import *


class TestFeaturesController(TestController):

    def setUp(self):
        'Prepare database'
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
            people.append(person)
        Session.commit()
        self.person1Key, self.person2Key = [x.key for x in people]
        # Prepare features
        features = []
        featurePacks = [
            (people[0].id, geoalchemy.WKTSpatialElement('LINESTRING(3 4,10 50,20 25)')),
            (people[1].id, geoalchemy.WKTSpatialElement('POLYGON((1 1,5 1,5 5,1 5,1 1),(2 2,2 3,3 3,3 2,2 2))')),
        ]
        for featurePack in featurePacks:
            feature = model.Feature()
            feature.owner_id = featurePack[0]
            feature.geometry = featurePack[1]
            Session.add(feature)
            features.append(feature)
        Session.commit()
        self.feature1ID, self.feature2ID = [x.id for x in features]

    def tearDown(self):
        Session.execute(model.feature_tags_table.delete())
        Session.execute(model.features_table.delete())
        Session.execute(model.tags_table.delete())
        Session.commit()

    def test_update(self):
        'Make sure we can update features properly'
        # Initialize
        urlName = 'feature_update'
        p = {
            'key': self.person1Key,
            'srid': 4326,
            'featureCollection': geojson.dumps(geojson.FeatureCollection([
                geojson.Feature(geometry=geojson.Point((0, 0)), properties={
                    'Population': 100,
                }),
            ])),
            'tags': 'tag1',
            'public': 0,
        }
        # Test
        print 'Expect error if we try to login without authentication'
        self.app.post(url(urlName), status=401)
        self.app.post(url(urlName), adjust(p, key=''), status=401)
        print 'Expect error if we submit invalid srid'
        self.app.post(url(urlName), adjust(p, srid=''), status=400)
        self.app.post(url(urlName), adjust(p, srid='xxx'), status=400)
        self.app.post(url(urlName), adjust(p, srid='-1'), status=400)
        print 'Expect error if we submit invalid featureCollection'
        self.app.post(url(urlName), adjust(p, featureCollection=''), status=400)
        self.app.post(url(urlName), adjust(p, featureCollection=geojson.dumps(geojson.FeatureCollection([]))), status=400)
        print 'Expect error if we submit invalid tags'
        self.app.post(url(urlName), adjust(p, tags=''), status=400)
        self.app.post(url(urlName), adjust(p, tags='x' * (parameter.TAG_LENGTH_MAXIMUM + 1)), status=400)
        print 'Expect error if we submit invalid public'
        self.app.post(url(urlName), adjust(p, public='xxx'), status=400)
        print 'Expect error if we try to specify an invalid featureID'
        self.app.post(url(urlName), adjust(p, featureCollection=geojson.dumps(geojson.FeatureCollection([geojson.Feature(id='xxx', geometry=geojson.Point((0, 0)))]))), status=400)
        print 'Expect error if we try to update features that do not exist'
        self.app.post(url(urlName), adjust(p, featureCollection=geojson.dumps(geojson.FeatureCollection([geojson.Feature(id=0, geometry=geojson.Point((0, 0)))]))), status=400)
        print 'Expect error if we try to update features that we do not own'
        self.app.post(url(urlName), adjust(p, featureCollection=geojson.dumps(geojson.FeatureCollection([geojson.Feature(id=self.feature2ID, geometry=geojson.Point((0, 0)))]))), status=400)
        print 'Expect error if we submit invalid geometry'
        self.app.post(url(urlName), adjust(p, featureCollection=geojson.dumps(geojson.FeatureCollection([geojson.Feature(geometry=None)]))), status=400)
        print 'Check that an add request works properly'
        featureID = self.app.post(url(urlName), p).body.splitlines()[0]
        print 'Check that an edit request works properly'
        self.app.post(url(urlName), adjust(p, featureCollection=geojson.dumps(geojson.FeatureCollection([geojson.Feature(id=featureID, geometry=geojson.Point((0, 0)), properties={'Name': u'Montréal'})]))))
        self.assertEqual(Session.query(model.Feature).get(featureID).properties['Name'], u'Montréal')

    def test_delete(self):
        'Make sure we can delete features properly'
        # Initialize
        urlName = 'feature_delete'
        p = {
            'key': self.person1Key,
            'featureIDs': str(self.feature1ID),
        }
        # Test
        print 'Expect error if we try to login without authentication'
        self.app.delete(url(urlName), status=401)
        self.app.delete(url(urlName, **adjust(p, key='')), status=401)
        print 'Expect error if we try to delete features that do not exist'
        self.app.delete(url(urlName, **adjust(p, featureIDs=str(0))), status=400)
        print 'Expect error if we try to delete features that we do not own'
        self.app.delete(url(urlName, **adjust(p, featureIDs=str(self.feature2ID))), status=400)
        print 'Check that a delete request works properly'
        self.app.delete(url(urlName, **p))
        self.assertEqual(Session.query(model.Feature).get(self.feature1ID), None)
