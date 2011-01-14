'Tests for tags controller'
# Import custom modules
from georegistry import model
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
    people.append(person)
Session.commit()
person1Key, person2Key = [x.key for x in people]
# Prepare tags
tags = []
tagPacks = [
    (u'tag with features that are public',),
    (u'tag with features that are private to person1',),
    (u'tag with features that are private to person2',),
]
for tagPack in tagPacks:
    tag = Session.query(model.Tag).filter_by(text=tagPack[0]).first()
    if not tag:
        tag = model.Tag(*tagPack)
        Session.add(tag)
    tags.append(tag)
Session.commit()
tag1Public, tag1Private, tag2Private = tags
# Prepare features
features = []
featurePacks = [
    (people[0].id, geoalchemy.WKTSpatialElement('POINT (0 0)'), model.scopePublic),
    (people[0].id, geoalchemy.WKTSpatialElement('POINT (1 0)'), model.scopePrivate),
    (people[1].id, geoalchemy.WKTSpatialElement('POINT (0 1)'), model.scopePrivate),
]
for featurePack in featurePacks:
    feature = Session.query(model.Feature).filter_by(owner_id=featurePack[0]).first()
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


class TestTagsController(TestController):

    def test_index(self):
        'Make sure we can index tags properly'
        # Initialize
        testURLName = testURLName
        # Expect error if we try to specify an unsupported responseFormat
        self.assertEqualJSON(self.app.get(url(testURLName, responseFormat='json')), 0)
        # Check that we only see public tags if we are not authenticated
        responseData = self.assertEqualJSON(self.app.get(url(testURLName, responseFormat='json')), 1)
        self.assertEqual(responseData['tags'], sorted(x.text for x in [tag1Public]))
        # Check that we see public and private tags if we are authenticated
        responseData = self.assertEqualJSON(self.app.get(url(testURLName, responseFormat='json', key=person1Key)), 1)
        self.assertEqual(responseData['tags'], sorted(x.text for x in [tag1Public, tag1Private]))
        responseData = self.assertEqualJSON(self.app.get(url(testURLName, responseFormat='json', key=person2Key)), 1)
        self.assertEqual(responseData['tags'], sorted(x.text for x in [tag1Public, tag2Private]))
