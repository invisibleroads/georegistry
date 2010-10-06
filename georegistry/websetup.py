'Setup the georegistry application'
# Import pylons modules
import pylons.test
# Import system modules
import logging; log = logging.getLogger(__name__)
# Import custom modules
from georegistry.config.environment import load_environment
from georegistry.model.meta import Session, Base


def setup_app(command, conf, vars):
    """Place any commands to setup georegistry here"""
    # Don't reload the app if it was loaded under the testing environment
    if not pylons.test.pylonsapp:
        load_environment(conf.global_conf, conf.local_conf)
    # Create the tables if they don't already exist
    Base.metadata.create_all(bind=Session.bind)
