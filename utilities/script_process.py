'Define common functions for command-line utilities'
# Import context modules
import os; basePath = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
import sys; sys.path.append(basePath)
# Import system modules
import sqlalchemy as sa
import ConfigParser
import optparse
# Import custom modules
from georegistry import model
from georegistry.lib import store
from georegistry.config import environment


def buildOptionParser():
    'Return default optionParser'
    optionParser = optparse.OptionParser()
    optionParser.add_option('-c', '--configurationPath', dest='configurationPath', help='use the specified configuration file', metavar='PATH', default=store.expandBasePath('development.ini'))
    return optionParser


def initialize(options):
    'Initialize connection to database'
    # Show feedback
    print 'Using %s' % options.configurationPath
    # Load
    configuration = ConfigParser.ConfigParser({'here': basePath})
    configuration.read(options.configurationPath)
    safe = environment.loadSafe(configuration.get('app:main', 'safe_path'))
    sqlalchemyURL = environment.patchSQLAlchemyURL(configuration.get('app:main', 'sqlalchemy.url'), safe)
    # Connect
    model.init_model(sa.create_engine(sqlalchemyURL))
    # Return
    return configuration
