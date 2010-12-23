'Setup the georegistry application'
# Import pylons modules
import pylons.test
# Import system modules
import logging; log = logging.getLogger(__name__)
import getpass
# Import custom modules
from georegistry import model
from georegistry.config import parameter
from georegistry.lib import store
from georegistry.model.meta import Session, Base
from georegistry.config.environment import load_environment


def setup_app(command, conf, vars):
    """Place any commands to setup georegistry here"""
    # If we are not in a testing environment,
    if not pylons.test.pylonsapp:
        load_environment(conf.global_conf, conf.local_conf)
    # Create the tables if they don't already exist
    Base.metadata.create_all(bind=Session.bind)
    # If we are not in a testing environment and users do not exist,
    if not pylons.test.pylonsapp and not Session.query(model.Person).all():
        # Show feedback
        print 'Please create an administrator account.'
        # Prepare
        passwordDefault = store.makeRandomString(parameter.PASSWORD_LENGTH_AVERAGE)
        # Create
        person = model.Person(raw_input('Username (administrator): ') or 'administrator', model.hashString(getpass.getpass('Password (%s): ' % passwordDefault) or passwordDefault), raw_input('Nickname (Administrator): ') or u'Administrator', raw_input('Email (support@invisibleroads.com): ') or 'support@invisibleroads.com')
        person.is_super = True
        Session.add(person)
        Session.commit()
