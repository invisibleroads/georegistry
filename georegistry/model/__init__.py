'Database objects'
# Import system modules
import sqlalchemy as sa
import sqlalchemy.orm as orm
import hashlib
import geoalchemy
import shapely.wkb
import osgeo.osr
# Import custom modules
from georegistry.model.meta import Session, Base
from georegistry.config import parameter
from georegistry.lib import store


# Constants

scopePrivate, scopePublic = xrange(2)


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
    geoalchemy.GeometryExtensionColumn('geometry', geoalchemy.Geometry(srid=900913), nullable=False),
)
feature_tags_table = sa.Table('feature_tags', Base.metadata,
    sa.Column('feature_id', sa.ForeignKey('features.id')),
    sa.Column('tag_id', sa.ForeignKey('tags.id')),
)
tags_table = sa.Table('tags', Base.metadata,
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('text', sa.Unicode(parameter.TAG_LENGTH_MAXIMUM), unique=True, nullable=False),
    sa.Column('when_updated', sa.DateTime),
)
maps_table = sa.Table('maps', Base.metadata,
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('x', sa.Integer),
    sa.Column('y', sa.Integer),
    sa.Column('z', sa.Integer),
    sa.Column('geojson', sa.UnicodeText),
    sa.Column('when_updated', sa.DateTime),
    geoalchemy.GeometryExtensionColumn('center', geoalchemy.Point(srid=900913)),
    geoalchemy.GeometryExtensionColumn('bound_lb', geoalchemy.Point(srid=900913)),
    geoalchemy.GeometryExtensionColumn('bound_rt', geoalchemy.Point(srid=900913)),
)
map_tags_table = sa.Table('map_tags', Base.metadata,
    sa.Column('map_id', sa.ForeignKey('maps.id')),
    sa.Column('tag_id', sa.ForeignKey('tags.id')),
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


class Map(object):
    'GeoJSON cache'

    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def refresh(self):
        'Set center and bounding box'
        pass

    def getCenter(self):
        center = shapely.wkb.loads(str(self.center.geom_wkb))
        return center.x, center.y

    def getBox(self):
        bound_lb = shapely.wkb.loads(str(self.bound_lb.geom_wkb))
        bound_rt = shapely.wkb.loads(str(self.bound_rt.geom_wkb))
        return bound_lb.x, bound_lb.y, bound_rt.x, bound_rt.y

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
    'geometry': geoalchemy.GeometryColumn(features_table.c.geometry, comparator=geoalchemy.SpatialComparator),
    'tags': orm.relation(Tag, secondary=feature_tags_table, backref='features'),
})
orm.mapper(Tag, tags_table)
orm.mapper(Map, maps_table, properties={
    'tags': orm.relation(Tag, secondary=map_tags_table, backref='maps'),
    'center': geoalchemy.GeometryColumn(maps_table.c.center, comparator=geoalchemy.SpatialComparator),
    'bound_lb': geoalchemy.GeometryColumn(maps_table.c.bound_lb, comparator=geoalchemy.SpatialComparator),
    'bound_rt': geoalchemy.GeometryColumn(maps_table.c.bound_rt, comparator=geoalchemy.SpatialComparator),
})


# DDLs

geoalchemy.GeometryDDL(features_table)
geoalchemy.GeometryDDL(maps_table)


# Helpers

def simplifyProj(proj4):
    'Simplify proj4 string'
    spatialReference = osgeo.osr.SpatialReference()
    if spatialReference.ImportFromProj4(str(proj4)) != 0:
        return
    return spatialReference.ExportToProj4()

def loadSRIDByProj4():
    'Generate a dictionary mapping proj4 to srid'
    # Initialize
    sridByProj4 = {}
    # For each spatial reference,
    for proj4, srid in Session.execute('SELECT proj4text, srid FROM spatial_ref_sys'):
        # Skip empty proj4s
        if not proj4.strip():
            continue
        # Store
        sridByProj4[simplifyProj(proj4)] = srid
    # Return
    return sridByProj4

def processTagTexts(tagTexts):
    'Save changes to tags'
    # Load existing tags
    tags = Session.query(Tag).filter(Tag.text.in_(tagTexts)).all()
    # Add tags that don't exist
    for tagText in set(tagTexts).difference(tag.text for tag in tags):
        tagText = tagText.strip()
        if not tagText:
            raise ValueError('Cannot add a tag without text')
        tag = Tag(tagText)
        tags.append(tag)
        Session.add(tag)
    Session.commit()
    # Return
    return tags

def getFeatures(featureIDs, personID):
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
    missingIDs = set(featureIDs).difference(x.id for x in features)
    if missingIDs:
        raise GeoRegistryError('Cannot modify featureIDs=%s because they do not exist' % missingIDs)
    # Validate blockedIDs
    blockedIDs = [x.id for x in features if x.owner_id != personID]
    if blockedIDs:
        raise GeoRegistryError('Cannot modify featureIDs=%s because you are not the owner' % blockedIDs)
    # Return
    return features


# Errors

class GeoRegistryError(Exception):
    pass
