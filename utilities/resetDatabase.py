#!/usr/bin/env python2.6
'Command-line script to reset database'
# Import pylons modules
import sqlalchemy as sa
# Import custom modules
import script_process
from georegistry import model
from georegistry.model import Base, Session


def run():
    'Reset database'
    # Gather tables
    tables = filter(lambda x: isinstance(x, sa.Table), [getattr(model, itemName) for itemName in dir(model)])
    # Clear database
    Base.metadata.bind = Session.bind
    Base.metadata.drop_all(tables=tables)
    Base.metadata.create_all()
    # Return
    return 'Reset'


# If we are running standalone,
if __name__ == '__main__':
    # Parse
    optionParser = script_process.buildOptionParser()
    options = optionParser.parse_args()[0]
    # Initialize
    script_process.initialize(options)
    # Run
    print run()
