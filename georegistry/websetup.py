'Setup the georegistry application'
# Import pylons modules
import pylons.test
# Import system modules
import logging; log = logging.getLogger(__name__)
import getpass
# Import custom modules
from georegistry import model
from georegistry.model.meta import Session, Base
from georegistry.config.environment import load_environment


def setup_app(command, conf, vars):
    """Place any commands to setup georegistry here"""
    # Don't reload the app if it was loaded under the testing environment
    if not pylons.test.pylonsapp:
        load_environment(conf.global_conf, conf.local_conf)
    # Create the tables if they don't already exist
    Base.metadata.create_all(bind=Session.bind)
    # If users do not exist,
    if not Session.query(model.Person).all():
        print 'Please create an administrator account.'
        # Create admin
        person = model.Person(raw_input('Username (admin): ') or 'admin', model.hashString(getpass.getpass('Password (admin): ') or 'admin'), raw_input('Nickname (Administrator): ') or u'Administrator', raw_input('Email (support@invisibleroads.com): ') or 'support@invisibleroads.com', raw_input('SMS: '))
        person.is_super = True
        Session.add(person)
        Session.commit()
