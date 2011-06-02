'Classes and functions for command-line utilities'
import os; basePath = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
import sys; sys.path.append(basePath)
import argparse
from sqlalchemy import create_engine

from georegistry import load_settings
from georegistry.models import initialize_sql


expand_path = lambda relativePath: os.path.join(basePath, relativePath)


class ArgumentParser(argparse.ArgumentParser):
    'ArgumentParser with default arguments'

    def __init__(self, *args, **kwargs):
        super(ArgumentParser, self).__init__(*args, **kwargs)
        self.add_argument('-c', 
            default=expand_path('development.ini'),
            dest='configurationPath', 
            help='use the specified configuration file',
            metavar='PATH')
        self.add_argument('-q',
            action='store_false',
            default=True,
            dest='verbose',
            help='be quiet')


def initialize(args):
    'Connect to database and return configuration settings'
    if args.verbose:
        print 'Using %s' % args.configurationPath
    settings = load_settings(args.configurationPath, basePath)
    initialize_sql(create_engine(settings['sqlalchemy.url']))
    return settings
