#!/usr/bin/env python2.6
'Command-line script to check and send text messages'
# Import system modules
from sqlalchemy import orm
# Import custom modules
import script_process
from georegistry import model
from georegistry.lib import imap
from georegistry.model import Session


# Methods

def run():
    'Check and send text messages'
    # Initialize
    registrationActionCount = 0
    getX = lambda x: configuration.get('app:main', x) if x in configuration.options('app:main') else ''
    # Connect
    try:
        imapStore = imap.Store(getX('sms.imap_server'), getX('sms.imap_username'), getX('sms.imap_password'))
    except imap.IMAPError:
        return 'Unable to connect to IMAP server'
    # For each message,
    for message in imapStore.read(includes=['inbox']):
        # If the message is trying to register an SMS address,
        if isRegistrationAction(message):
            registrationActionCount += 1
        # Mark message for deletion
        message.markDeleted()
    # Finalize
    imapStore.expunge()
    Session.commit()
    return 'Registration actions: %s' % registrationActionCount

def isRegistrationAction(message):
    'Return True if the message is trying to register an SMS address'
    # Get
    messageFromWhom = message.fromWhom.lower()
    try:
        personID = int(message.subject)
    except ValueError:
        return False
    # If personID == 0, then the sender is trying to unregister his or her phone
    if personID == 0:
        Session.query(model.SMSAddress).filter_by(email=messageFromWhom).delete()
        return True
    # Load
    person = Session.query(model.Person).options(orm.eagerload(model.Person.sms_addresses)).get(personID)
    # If the person doesn't exist or we have recorded the address already,
    if not person or messageFromWhom in (x.email.lower() for x in person.sms_addresses):
        return False
    # Add
    Session.add(model.SMSAddress(messageFromWhom, personID))
    # Return
    return True


# If we are running standalone,
if __name__ == '__main__':
    # Parse
    optionParser = script_process.buildOptionParser()
    options = optionParser.parse_args()[0]
    # Initialize
    configuration = script_process.initialize(options)
    # Run
    print run()
