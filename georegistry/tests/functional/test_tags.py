'Tests for tags controller'
# Import system modules
import geoalchemy
import datetime
# Import custom modules
from georegistry import model
from georegistry.model import Session
from georegistry.tests import *


class TestTagsController(TestController):

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
            (people[0].id, geoalchemy.WKTSpatialElement('POINT(6 10)'), model.scopePublic),
            (people[0].id, geoalchemy.WKTSpatialElement('LINESTRING(3 4,10 50,20 25)'), model.scopePrivate),
            (people[1].id, geoalchemy.WKTSpatialElement('POLYGON((1 1,5 1,5 5,1 5,1 1),(2 2,2 3,3 3,3 2,2 2))'), model.scopePrivate),
        ]
        for featurePack in featurePacks:
            feature = Session.query(model.Feature).filter(model.Feature.geometry.equals(featurePack[1])).first()
            if not feature:
                feature = model.Feature()
                feature.owner_id = featurePack[0]
                feature.geometry = featurePack[1]
                feature.scope = featurePack[2]
                Session.add(feature)
            features.append(feature)
        feature1Public, feature1Private, feature2Private = features
        feature1Public.tags = [tag1Public]
        feature1Private.tags = [tag1Private]
        feature2Private.tags = [tag2Private]
        Session.commit()

    def tearDown(self):
        Session.execute(model.feature_tags_table.delete())
        Session.execute(model.features_table.delete())
        Session.execute(model.tags_table.delete())
        Session.commit()

    def test_index(self):
        'Make sure we can index tags properly'
        # Initialize
        urlName = 'tag_index_'
        p = {
            'responseFormat': 'json',
            'key': self.person1Key,
        }
        print 'Expect error if we try to specify an unsupported responseFormat'
        self.app.get(url(urlName, **adjust(p, responseFormat='xxx')), status=400)
        print 'Check that we only see public tags if we are not authenticated'
        tagTexts = self.app.get(url(urlName, **adjust(p, key=''))).body.splitlines()
        self.assertEqual(tagTexts, sorted([self.tagTexts[0]]))
        print 'Check that we see public and private tags if we are authenticated'
        tagTexts = self.app.get(url(urlName, **p)).body.splitlines()
        self.assertEqual(tagTexts, sorted([self.tagTexts[0], self.tagTexts[1]]))
        tagTexts = self.app.get(url(urlName, **adjust(p, key=self.person2Key))).body.splitlines()
        self.assertEqual(tagTexts, sorted([self.tagTexts[0], self.tagTexts[2]]))
