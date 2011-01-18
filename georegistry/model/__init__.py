'Database objects'
# Import system modules
import sqlalchemy as sa
import sqlalchemy.orm as orm
import hashlib
import datetime
import geoalchemy
import geoalchemy.postgis
import shapely.wkb
import osgeo.osr
# Import custom modules
from georegistry.model.meta import Session, Base
from georegistry.config import parameter
from georegistry.lib import store


# Constants

scopePrivate, scopePublic = xrange(2)
databaseSRID = 4326 # Longitude latitude


# Methods

def init_model(engine):
    'Call me before using any of the tables or classes in the model'
    Session.configure(bind=engine)

def hashString(string): 
    'Compute the hash of the string'
    return hashlib.sha256(string).digest()


# Tables

people_table = sa.Table('people', Base.metadata,
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('username', sa.String(parameter.USERNAME_LENGTH_MAXIMUM), unique=True, nullable=False),
    sa.Column('password_hash', sa.LargeBinary(32), nullable=False),
    sa.Column('nickname', sa.Unicode(parameter.NICKNAME_LENGTH_MAXIMUM), unique=True, nullable=False),
    sa.Column('email', sa.String(parameter.EMAIL_LENGTH_MAXIMUM), unique=True, nullable=False),
    sa.Column('minutes_offset', sa.Integer, default=0),
    sa.Column('rejection_count', sa.Integer, default=0),
    sa.Column('is_super', sa.Boolean, default=False),
    sa.Column('key', sa.String(parameter.KEY_LENGTH), unique=True, nullable=False),
)
person_candidates_table = sa.Table('person_candidates', Base.metadata,
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('username', sa.String(parameter.USERNAME_LENGTH_MAXIMUM), nullable=False),
    sa.Column('password_hash', sa.LargeBinary(32), nullable=False),
    sa.Column('nickname', sa.Unicode(parameter.NICKNAME_LENGTH_MAXIMUM), nullable=False),
    sa.Column('email', sa.String(parameter.EMAIL_LENGTH_MAXIMUM), nullable=False),
    sa.Column('person_id', sa.ForeignKey('people.id')),
    sa.Column('ticket', sa.String(parameter.TICKET_LENGTH), unique=True, nullable=False),
    sa.Column('when_expired', sa.DateTime, nullable=False),
)
sms_addresses_table = sa.Table('sms_addresses', Base.metadata,
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('email', sa.String(parameter.EMAIL_LENGTH_MAXIMUM), unique=True, nullable=False),
    sa.Column('owner_id', sa.ForeignKey('people.id')),
    sa.Column('is_active', sa.Boolean, default=False),
)
features_table = sa.Table('features', Base.metadata,
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('owner_id', sa.ForeignKey('people.id')),
    sa.Column('properties', sa.PickleType(mutable=False)),
    sa.Column('scope', sa.Integer, default=scopePrivate),
    geoalchemy.GeometryExtensionColumn('geometry', geoalchemy.Geometry(srid=databaseSRID), nullable=False),
)
feature_tags_table = sa.Table('feature_tags', Base.metadata,
    sa.Column('feature_id', sa.ForeignKey('features.id')),
    sa.Column('tag_id', sa.ForeignKey('tags.id')),
)
tags_table = sa.Table('tags', Base.metadata,
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('text', sa.Unicode(parameter.TAG_LENGTH_MAXIMUM), unique=True, nullable=False),
    sa.Column('when_updated', sa.DateTime, default=datetime.datetime.utcnow()),
)
maps_table = sa.Table('maps', Base.metadata,
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('query_hash', sa.LargeBinary(32), nullable=False),
    sa.Column('geojson', sa.UnicodeText, nullable=False),
    sa.Column('when_updated', sa.DateTime, default=datetime.datetime.utcnow()),
)


# Classes

class Person(object):

    def __init__(self, username, password_hash, nickname, email):
        self.username = username
        self.password_hash = password_hash
        self.nickname = nickname
        self.email = email
        self.key = store.makeRandomString(parameter.KEY_LENGTH)

    def __repr__(self):
        return "<Person('%s')>" % self.email


class PersonCandidate(Person):

    def __repr__(self):
        return "<PersonCandidate('%s')>" % self.email


class SMSAddress(object):

    def __init__(self, email, owner_id):
        self.email = email
        self.owner_id = owner_id

    def __repr__(self):
        return "<SMSAddress('%s')>" % self.email


class LowerCaseComparator(orm.properties.ColumnProperty.Comparator):

    def __eq__(self, other):
        return sa.func.lower(self.__clause_element__()) == sa.func.lower(other)


class Feature(object):

    def __repr__(self):
        return "<Feature(id=%s)>" % self.id


class Tag(object):

    def __init__(self, text):
        self.text = text

    def __repr__(self):
        return "<Tag(id=%s)>" % self.id

    def updateTimestamp(self):
        self.when_updated = datetime.datetime.utcnow()


class Map(object):
    'GeoJSON cache'

    def __repr__(self):
        return "<Map(id=%s)>" % self.id


# Links

orm.mapper(Person, people_table, properties={
    'username': orm.column_property(people_table.c.username, comparator_factory=LowerCaseComparator),
    'nickname': orm.column_property(people_table.c.nickname, comparator_factory=LowerCaseComparator),
    'email': orm.column_property(people_table.c.email, comparator_factory=LowerCaseComparator),
    'sms_addresses': orm.relation(SMSAddress),
})
orm.mapper(PersonCandidate, person_candidates_table, properties={
    'username': orm.column_property(person_candidates_table.c.username, comparator_factory=LowerCaseComparator),
    'nickname': orm.column_property(person_candidates_table.c.nickname, comparator_factory=LowerCaseComparator),
    'email': orm.column_property(person_candidates_table.c.email, comparator_factory=LowerCaseComparator),
})
orm.mapper(SMSAddress, sms_addresses_table, properties={
    'email': orm.column_property(sms_addresses_table.c.email, comparator_factory=LowerCaseComparator),
})
orm.mapper(Feature, features_table, properties={
    'owner': orm.relation(Person, backref='features'),
    'geometry': geoalchemy.GeometryColumn(features_table.c.geometry, comparator=geoalchemy.postgis.PGComparator),
    'tags': orm.relation(Tag, secondary=feature_tags_table, backref='features'),
})
orm.mapper(Tag, tags_table, properties={
    'text': orm.column_property(tags_table.c.text, comparator_factory=LowerCaseComparator),
})
orm.mapper(Map, maps_table)


# DDLs

geoalchemy.GeometryDDL(features_table)


# Helpers

def validateSRID(srid):
    'Make sure we have a valid SRID'
    if not srid:
        raise GeoRegistryError('Must specify spatial reference srid')
    try:
        srid = int(srid)
    except ValueError:
        raise GeoRegistryError('Could not parse srid=%s as an integer' % srid)
    result = Session.execute('SELECT proj4text FROM spatial_ref_sys WHERE srid=:srid', dict(srid=srid)).fetchone()
    if not result:
        raise GeoRegistryError('Could not recognize srid=%s' % srid)
    return result[0]

def getTags(string, addMissing=False):
    'Return corresponding tags'
    # Load tagTexts and discard empty lines
    tagTexts = filter(lambda x: x, (x.strip() for x in string.splitlines()))
    if not tagTexts:
        raise GeoRegistryError('Must specify at least one tag in tags')
    # Check whether tagTexts are too long
    longTagTexts = filter(lambda x: len(x) > parameter.TAG_LENGTH_MAXIMUM, tagTexts)
    if longTagTexts:
        raise GeoRegistryError('Cannot add the following tags because they are too long:\n%s' % '\n'.join(longTagTexts))
    # Check whether tags exist
    missingTagTexts = list(set(tagTexts).difference(tag.text for tag in Session.query(Tag).filter(Tag.text.in_(tagTexts))))
    if missingTagTexts:
        # If we are not supposed to add missing tags,
        if not addMissing:
            raise GeoRegistryError('Cannot match the following tags: %s' % missingTagTexts)
        # Add tags that don't exist
        Session.execute(tags_table.insert(), [{
            'text': x,
        } for x in missingTagTexts])
        # Commit
        Session.commit()
    # Return
    return Session.query(Tag).filter(Tag.text.in_(tagTexts)).all()

def getWritableFeatures(featureIDs, personID):
    'Raise GeoRegistryError if personID does not have write access to the featureIDs'
    # Validate featureIDs
    try:
        featureIDs = [int(x) for x in featureIDs if x is not None]
    except ValueError:
        raise GeoRegistryError('Could not parse featureIDs=%s as integers' % featureIDs)
    # If we have no featureIDs,
    if not featureIDs:
        return []
    # Load
    features = Session.query(Feature).filter(Feature.id.in_(featureIDs)).all()
    # Validate missingIDs
    missingIDs = list(set(featureIDs).difference(x.id for x in features))
    if missingIDs:
        raise GeoRegistryError('Cannot modify featureIDs=%s that do not exist' % missingIDs)
    # Validate blockedIDs
    blockedIDs = [x.id for x in features if x.owner_id != personID]
    if blockedIDs:
        raise GeoRegistryError('Cannot modify featureIDs=%s because you are not the owner' % blockedIDs)
    # Return
    return features

def getFeatureFilter(personID):
    'Get feature filter for use in queries'
    featureFilter = Feature.scope == scopePublic
    if personID:
        featureFilter |= Feature.owner_id == personID
    return featureFilter


# Errors

class GeoRegistryError(Exception):
    pass
