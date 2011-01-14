'Tests for people controller'
# Import system modules
import re
# Import custom modules
from georegistry import model
from georegistry.model import Session
from georegistry.config import parameter
from georegistry.lib import store, helpers as h
from georegistry.tests import *


# Define shortcuts
username = 'username'
password = 'password'
nickname = u'nickname'
email = 'email@example.com'
emailSMS = '1234567890@example.com'


class TestPeopleController(TestController):

    def setUp(self):
        'Clear tables'
        # Logout
        self.app.get(url('person_logout'))
        # Delete all people
        Session.rollback()
        Session.query(model.Person).delete()
        Session.query(model.PersonCandidate).delete()
        Session.commit()

    def test_index(self):
        'Assert that the index page shows how many accounts are on file'
        # Initialize
        testURL = url('person_index')
        # Make sure that we begin with 0 people
        self.assert_('0 people' in self.app.get(testURL))
        # Add person
        Session.add(model.Person(username, model.hashString(password), nickname, email))
        Session.commit()
        # Make sure that we now have 1 person
        self.assert_('1 people' in self.app.get(testURL))

    def test_registration(self):
        'Make sure that registration works'
        # Make sure the registration page appears properly
        self.assert_('Registration' in self.app.get(url('person_register')))
        # Register
        self.app.post(url('person_register'), dict(username=username, password=password, nickname=nickname, email=email))
        # Register with the same username but with different case
        self.app.post(url('person_register'), dict(username=username.upper(), password=password, nickname=nickname + 'x', email=email + 'x'))
        # Register with the same nickname but with different case
        self.app.post(url('person_register'), dict(username=username + 'x', password=password, nickname=nickname.upper(), email=email + 'x'))
        # Register with the same email but with different case
        self.app.post(url('person_register'), dict(username=username + 'x', password=password, nickname=nickname + 'x', email=email.upper()))
        # Confirm registration
        self.app.get(url('person_confirm', ticket=Session.query(model.PersonCandidate.ticket).filter_by(email=email).first()[0]))
        # Make sure the person exists
        self.assertEqual(Session.query(model.Person).filter_by(email=email).count(), 1)
        # Make sure that conflicting registrations have been deleted
        self.assertEqual(Session.query(model.PersonCandidate).filter_by(password_hash=model.hashString(password)).count(), 0)

    def test_reset(self):
        """
        Make sure that resetting the password works
        Trying to reset an email that does not exist should return an error
        Make sure that resetting the password does not immediately change the password
        Make sure that reset confirmation works
        """
        # Reset an unfamiliar email
        self.assertEqualJSON(self.app.post(url('person_reset'), dict(email=email)), 0)
        # Add person
        Session.add(model.Person(username, model.hashString(password), nickname, email))
        Session.commit()
        # Reset password
        self.assertEqualJSON(self.app.post(url('person_reset'), dict(email=email)), 1)
        # Make sure the candidate exists
        self.assertEqual(Session.query(model.PersonCandidate).filter_by(email=email).count(), 1)
        # Activate candidate
        self.app.get(url('person_confirm', ticket=Session.query(model.PersonCandidate.ticket).filter_by(email=email).first()[0]))
        # Make sure the password has changed
        self.assertEqual(Session.query(model.Person).filter_by(password_hash=model.hashString(password)).count(), 0)

    def test_update(self):
        """
        Make sure that updating credentials works
        Make sure the update page only appears when the user is logged in
        Make sure the update form is filled with the user's credentials
        Make sure that update_ only works when the user is logged in
        Make sure that update confirmation works
        Make sure that update_ for SMS only works when the user is the owner
        """
        # Assert that we are redirected to the login page if the person is not logged in
        self.assert_(url('person_login', url=url('person_update')) in self.app.get(url('person_update')))
        # Assert that we get rejected if we try to post without logging in
        self.assertEqualJSON(self.app.post(url('person_update')), 0)
        # Add people
        Session.add(model.Person(username, model.hashString(password), nickname, email))
        Session.add(model.Person(username + 'x', model.hashString(password), nickname + 'x', email + 'x'))
        Session.commit()
        # Log in
        self.app.post(url('person_login'), dict(username=username, password=password))
        # Assert that the update form is filled with the user's credentials
        responseBody = self.app.get(url('person_update')).body
        self.assert_(username in responseBody)
        self.assert_(nickname in responseBody)
        self.assert_(email in responseBody)
        # Update credentials
        username_ = store.makeRandomString(parameter.USERNAME_LENGTH_MAXIMUM)
        password_ = store.makeRandomAlphaNumericString(parameter.PASSWORD_LENGTH_AVERAGE)
        nickname_ = unicode(store.makeRandomString(parameter.NICKNAME_LENGTH_MAXIMUM))
        email_ = re.sub(r'.*@', store.makeRandomString(16) + '@', email)
        self.assertEqualJSON(self.app.post(url('person_update'), dict(username=username_, password=password_, nickname=nickname_, email=email_)), 1)
        # Make sure the credentials have not changed yet
        self.assertEqual(Session.query(model.Person).filter_by(username=username_, password_hash=model.hashString(password_), nickname=nickname_, email=email_).count(), 0)
        # Activate candidate
        self.app.get(url('person_confirm', ticket=Session.query(model.PersonCandidate.ticket).filter_by(email=email_).first()[0]))
        # Make sure the credentials have changed
        self.assertEqual(Session.query(model.Person).filter_by(username=username_, password_hash=model.hashString(password_), nickname=nickname_, email=email_).count(), 1)
        # Load people
        person1 = Session.query(model.Person).filter_by(username=username_, password_hash=model.hashString(password_), nickname=nickname_, email=email_).first()
        person2 = Session.query(model.Person).filter_by(username=username + 'x').first()
        # Add SMSAddress
        smsAddress = model.SMSAddress(emailSMS, person2.id)
        Session.add(smsAddress)
        Session.commit()
        smsAddressID = smsAddress.id
        # Make sure that only the owner can update SMS information
        self.app.post(url('person_login'), dict(username=username, password=password))
        self.assertEqualJSON(self.app.post(url('person_update'), dict(smsAddressID=smsAddressID, action='activate')), 0)
        self.assertEqualJSON(self.app.post(url('person_update'), dict(smsAddressID=smsAddressID, action='deactivate')), 0)
        self.assertEqualJSON(self.app.post(url('person_update'), dict(smsAddressID=smsAddressID, action='remove')), 0)
        self.app.post(url('person_login'), dict(username=username + 'x', password=password))
        self.assertEqualJSON(self.app.post(url('person_update'), dict(smsAddressID=smsAddressID, action='activate')), 1)
        self.assertEqualJSON(self.app.post(url('person_update'), dict(smsAddressID=smsAddressID, action='deactivate')), 1)
        self.assertEqualJSON(self.app.post(url('person_update'), dict(smsAddressID=smsAddressID, action='remove')), 1)

    def test_login(self):
        """
        Make sure that logging in works
        Ensure that the login page shows
        Ensure that bad credentials result in an error message
        Ensure that good credentials result in a proper redirect
        """
        # Initialize
        testURL = url('person_update')
        # Assert that the login page shows and stores url
        self.assert_('Login' in self.app.get(url('person_login', url=testURL)))
        # Add person
        Session.add(model.Person(username, model.hashString(password), nickname, email))
        Session.commit()
        # Log in using bad credentials
        self.assertEqualJSON(self.app.post(url('person_login'), dict(username=username, password=password + 'x')), 0)
        # Log in using good credentials
        self.assertEqualJSON(self.app.post(url('person_login'), dict(username=username, password=password)), 1)

    def test_logout(self):
        """
        Make sure that logging out works
        If the person is logged in, make sure the person gets logged out
        and is redirected properly.  If the person is already logged out, 
        return the user to the page before the user tried to log out.
        """
        # Initialize
        testURL = url('person_index')
        # Add person
        Session.add(model.Person(username, model.hashString(password), nickname, email))
        Session.commit()
        # Logging out should redirect back
        self.assert_(testURL in self.app.get(url('person_logout', url=testURL)))
        # Log in
        self.assert_('Login' in self.app.get(url('person_login', url=testURL)))
        self.assertEqualJSON(self.app.post(url('person_login'), dict(username=username, password=password)), 1)
        # Logging out should redirect back
        self.assert_(testURL in self.app.get(url('person_logout', url=testURL)))
