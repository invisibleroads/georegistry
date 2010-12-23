'URL configuration'
# Import pylons modules
from routes import Mapper


def make_map(config):
    'Create, configure and return the routes mapper'
    # Initialize map
    map = Mapper(directory=config['pylons.paths']['controllers'], always_scan=config['debug'])
    map.minimization = False
    map.explicit = False
    # Remove trailing slash
    map.redirect('/{controller}/', '/{controller}')
    # Map errors
    map.connect('/errors/{action}', controller='errors')
    map.connect('/errors/{action}/{id}', controller='errors')
    # Map people
    map.connect('person_index', '/people', controller='people', action='index')
    map.connect('person_register', '/people/register', controller='people', action='register', conditions=GET)
    map.connect('person_register', '/people/register', controller='people', action='register_', conditions=POST)
    map.connect('person_confirm', '/people/confirm/{ticket}', controller='people', action='confirm')
    map.connect('person_login', '/people/login', controller='people', action='login', conditions=GET)
    map.connect('person_login', '/people/login', controller='people', action='login_', conditions=POST)
    map.connect('person_update', '/people/update', controller='people', action='update', conditions=GET)
    map.connect('person_update', '/people/update', controller='people', action='update_', conditions=POST)
    map.connect('person_logout', '/people/logout', controller='people', action='logout')
    map.connect('person_reset', '/people/reset', controller='people', action='reset')
    # Map regions
    map.connect('region_index_plain', '/regions', controller='regions', action='index')
    map.connect('region_index', '/regions.:(responseFormat)', controller='regions', action='index')
    map.connect('region_show', '/regions/:(countryCode).:(responseFormat)', controller='regions', action='show')
    map.connect('region_show_plain', '/regions/:(countryCode)', controller='regions', action='show')
    # Redirect index
    map.redirect('/', '/regions')
    # Return
    return map


# Set constants
GET = dict(method=['GET'])
POST = dict(method=['POST'])
