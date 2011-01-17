# -*- coding: utf-8 -*-
'Tests for maps controller'
# Import system modules
import geoalchemy
# Import custom modules
from georegistry import model
from georegistry.config import parameter
from georegistry.model import Session
from georegistry.tests import *


class TestMapsController(TestController):

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
        # Prepare tags
        tags = []
        self.tagTexts = [
            u'tag with features that are public',
            u'tag with features that are private to person1',
            u'tag with features that are private to person2',
        ]
        for tagText in self.tagTexts:
            tag = Session.query(model.Tag).filter_by(text=tagText).first()
            if not tag:
                tag = model.Tag(tagText)
                Session.add(tag)
            tags.append(tag)
        Session.commit()
        tag1Public, tag1Private, tag2Private = tags
        # Prepare features
        features = []
        featurePacks = [
            (people[0].id, geoalchemy.WKTSpatialElement('MULTIPOINT (15.7834710000000005 -90.2307590000000062, 37.5665350000000018 126.9779692000000040, 5.5557169999999996 -0.1963060000000000, 14.8361560000000008 -91.5219589999999954)'), model.scopePublic, {'description': 'Santa Eulalia; Seoul; Accra; Xela'}),
            (people[0].id, geoalchemy.WKTSpatialElement('LINESTRING (41.8781135999999989 -87.6297981999999962, 33.7489953999999983 -84.3879823999999985, 37.7749294999999989 -122.4194154999999995)'), model.scopePrivate, {'description': 'Chicago; Atlanta; San Francisco'}),
            (people[1].id, geoalchemy.WKTSpatialElement('LINESTRING (40.7143528 -74.0059731, 14.6133333 -90.5352778)'), model.scopePrivate, {'passenger': u'Hélène'}),
        ]
        for featurePack in featurePacks:
            feature = model.Feature()
            feature.owner_id, feature.geometry, feature.scope, feature.properties = featurePack
            Session.add(feature)
            features.append(feature)
        feature1Public, feature1Private, feature2Private = features
        feature1Public.tags = [tag1Public]
        feature1Private.tags = [tag1Private]
        feature2Private.tags = [tag2Private]
        Session.commit()
        self.feature1ID = feature1Public.id

    def tearDown(self):
        Session.execute(model.feature_tags_table.delete())
        Session.execute(model.features_table.delete())
        Session.execute(model.tags_table.delete())
        Session.commit()

    def test_view(self):
        'Make sure we can view maps properly'
        # Initialize
        urlName = 'map_view_'
        p = {
            'responseFormat': 'json',
            'key': self.person1Key,
            'srid': 3857,
            'tags': '\n'.join(self.tagTexts[:2]),
            'bbox': '',
            'simplified': 1,
        }
        # Test
        print 'Expect error if we try to specify an unsupported responseFormat'
        self.app.get(url(urlName, **adjust(p, responseFormat='xxx')), status=400)
        print 'Expect error if we submit invalid srid'
        self.app.get(url(urlName, **adjust(p, srid='')), status=400)
        self.app.post(url(urlName, **adjust(p, srid='xxx')), status=400)
        self.app.post(url(urlName, **adjust(p, srid='-1')), status=400)
        print 'Expect error if we submit invalid tags'
        self.app.get(url(urlName, **adjust(p, tags='')), status=400)
        self.app.get(url(urlName, **adjust(p, tags='x' * (parameter.TAG_LENGTH_MAXIMUM + 1))), status=400)
        print 'Expect error if we submit invalid bbox'
        self.app.get(url(urlName, **adjust(p, bbox='xxx')), status=400)
        print 'Expect error if we submit invalid simplified'
        self.app.get(url(urlName, **adjust(p, simplified='xxx')), status=400)
        print 'Check that a view request works properly'
        self.app.get(url(urlName, **p))
        self.app.get(url(urlName, **adjust(p, bbox='10, -100, 210, 100')))
        self.app.get(url(urlName, **adjust(p, bbox='10, -100, 210, 100', simplified=0)))
        print 'Check that caching works properly'
        def getCacheTimestamps():
            return [x[0] for x in Session.query(model.Map.when_updated).order_by(model.Map.when_updated)]
        oldCacheTimeStamps = getCacheTimestamps()
        self.app.get(url(urlName, **p))
        self.assertEqual(getCacheTimestamps(), oldCacheTimeStamps)
        self.app.delete(url('feature_delete', key=self.person1Key, featureIDs=self.feature1ID))
        self.app.get(url(urlName, **p))
        self.assertNotEqual(getCacheTimestamps(), oldCacheTimeStamps)
