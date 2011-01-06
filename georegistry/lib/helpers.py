'Helpers'
# Import pylons modules
from pylons import session, request, url
# Import system modules
from webhelpers.util import html_escape
from webhelpers.html import literal
from webhelpers.html.tags import *
# Import custom modules
from georegistry.config.parameter import *
from georegistry.lib import whenIO


def isPerson():
    return 1 if 'personID' in session else 0

def isPersonSuper():
    return 1 if session.get('is_super', False) else 0

def getPersonID():
   return session.get('personID', 0)

def getPersonIDViaKey():
    'Try to get personID via key; otherwise, try to get personID via session'
    # Load key
    key = request.params.get('key', '').strip()
    # If we have a key,
    if key:
        # Load person
        person = Session.query(model.Person).filter_by(key=key).first()
        # If the person exists,
        if person:
            # Return personID via key
            return person.id
    # Return personID via session
    return getPersonID()

def getMinutesOffset():
    try:
        return int(request.params.get('minutesOffset', session.get('minutesOffset', MINUTES_OFFSET_DEFAULT)))
    except ValueError:
        return MINUTES_OFFSET_DEFAULT

def getWhenIO():
    return whenIO.WhenIO(getMinutesOffset())

def getRemoteIP():
    return request.environ.get('HTTP_X_REAL_IP', 
           request.environ.get('HTTP_X_FORWARDED_FOR', 
           request.environ.get('REMOTE_ADDR')))
