'Pylons environment configuration'
# Import pylons modules
from pylons.configuration import PylonsConfig
from pylons.error import handle_mako_error
from mako.lookup import TemplateLookup
# Import system modules
import os
from sqlalchemy import engine_from_config
# Import custom modules
from georegistry.lib import app_globals, helpers
from georegistry.config.routing import make_map
from georegistry.model import init_model


def load_environment(global_conf, app_conf):
    'Configure the Pylons environment via the ``pylons.config`` object'
    # Set paths
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    paths = dict(
        root=root,
        controllers=os.path.join(root, 'controllers'),
        static_files=os.path.join(root, 'public'),
        templates=[os.path.join(root, 'templates')])
    # Initialize config with the basic options
    config = PylonsConfig()
    config.init_app(global_conf, app_conf, package='georegistry', paths=paths)
    config['routes.map'] = make_map(config)
    config['pylons.app_globals'] = app_globals.Globals(config)
    config['pylons.h'] = helpers
    # Setup cache object as early as possible
    import pylons
    pylons.cache._push_object(config['pylons.app_globals'].cache)
    # Create the Mako TemplateLookup, with the default auto-escaping
    config['pylons.app_globals'].mako_lookup = TemplateLookup(
        directories=paths['templates'],
        error_handler=handle_mako_error,
        module_directory=os.path.join(app_conf['cache_dir'], 'templates'),
        input_encoding='utf-8', default_filters=['escape'],
        imports=['from webhelpers.html import escape'])
    # Setup the SQLAlchemy database engine
    engine = engine_from_config(config, 'sqlalchemy.')
    init_model(engine)
    # Return
    return config
