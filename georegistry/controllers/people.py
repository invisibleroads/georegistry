'People controller'
# Import pylons modules
from pylons import request, session, tmpl_context as c, url, config
from pylons.controllers.util import redirect
from pylons.decorators import jsonify
import formencode
# Import system modules
import datetime
import recaptcha.client.captcha as captcha
import cStringIO as StringIO
import sqlalchemy as sa
from sqlalchemy import orm
# Import custom modules
from georegistry import model
from georegistry.model import Session
from georegistry.config import parameter
from georegistry.lib import helpers as h, store, smtp
from georegistry.lib.base import BaseController, render
from georegistry.controllers import requireLogin, requireLoginJSON


class PeopleController(BaseController):
    'Methods to handle registration, authentication and account modification'

    def index(self):
        'Show information about people registered in the database'
        c.people = Session.query(model.Person).all()
        return render('/people/index.mako')

    def register(self):
        'Show account registration page'
        c.isNew = True
        return render('/people/change.mako')

    @jsonify
    def register_(self):
        'Store proposed changes and send confirmation email'
        return changePerson(dict(request.POST), 'registration')

    def confirm(self, ticket):
        'Confirm changes'
        # Send feedback
        candidate = confirmPersonCandidate(ticket)
        # If the candidate exists,
        if candidate:
            # Set
            messageCode = 'updated' if candidate.person_id else 'created'
            # Delete expired or similar candidates
            Session.execute(model.person_candidates_table.delete().where((model.PersonCandidate.when_expired < datetime.datetime.utcnow()) | (model.PersonCandidate.username == candidate.username) | (model.PersonCandidate.nickname == candidate.nickname) | (model.PersonCandidate.email == candidate.email)))
            Session.commit()
        # If the candidate does not exist,
        else:
            # Set
            messageCode = 'expired'
        # Return
        return redirect(url('person_login', url='/', messageCode=messageCode))

    @requireLogin
    def update(self):
        'Show account update page'
        # Render
        person = Session.query(model.Person).options(orm.eagerload(model.Person.sms_addresses)).get(h.getPersonID())
        c.isNew = False
        c.smsAddresses = person.sms_addresses
        # Return
        return formencode.htmlfill.render(render('/people/change.mako'), {
            'username': person.username,
            'nickname': person.nickname,
            'email': person.email,
            'key': person.key,
        })

    @jsonify
    @requireLoginJSON
    def update_(self):
        'Update account'
        # Initialize
        personID = h.getPersonID()
        # If the user is trying to update SMS information,
        if 'smsAddressID' in request.POST:
            # Load
            action = request.POST.get('action')
            smsAddressID = request.POST['smsAddressID']
            smsAddress = Session.query(model.SMSAddress).filter((model.SMSAddress.id==smsAddressID) & (model.SMSAddress.owner_id==personID)).first()
            if not smsAddress:
                return dict(isOk=0, message='Could not find smsAddressID=%s corresponding to personID=%s' % (smsAddressID, personID))
            # If the user is trying to activate an SMS address,
            elif action == 'activate':
                smsAddress.is_active = True
            # If the user is trying to deactivate an SMS address,
            elif action == 'deactivate':
                smsAddress.is_active = False
            # If the user is trying to remove an SMS address,
            elif action == 'remove':
                Session.delete(smsAddress)
            # Otherwise,
            else:
                return dict(isOk=0, message='Command not recognized')
            # Commit and return
            Session.commit()
            return dict(isOk=1)
        # If the user is trying to update account information,
        else:
            # Send update confirmation email
            return changePerson(dict(request.POST), 'update', Session.query(model.Person).get(personID))

    def login(self):
        'Show login form'
        c.url = request.GET.get('url', '/')
        c.messageCode = request.GET.get('messageCode')
        c.recaptchaPublicKey = config.get('recaptcha.public', '')
        return render('/people/login.mako')

    @jsonify
    def login_(self):
        'Process login credentials'
        # Check username
        username = str(request.POST.get('username', ''))
        person = Session.query(model.Person).filter_by(username=username).first()
        # If the username does not exist,
        if not person:
            return dict(isOk=0)
        # Check password
        password_hash = model.hashString(str(request.POST.get('password', '')))
        # If the password is incorrect,
        if password_hash != StringIO.StringIO(person.password_hash).read():
            # Increase and return rejection_count without a requery
            rejection_count = person.rejection_count = person.rejection_count + 1
            Session.commit()
            return dict(isOk=0, rejection_count=rejection_count)
        # If there have been too many rejections,
        if person.rejection_count >= parameter.REJECTION_LIMIT:
            # Expect recaptcha response
            recaptchaChallenge = request.POST.get('recaptcha_challenge_field', '')
            recaptchaResponse = request.POST.get('recaptcha_response_field', '')
            recaptchaPrivateKey = config.get('recaptcha.private', '')
            # Validate
            result = captcha.submit(recaptchaChallenge, recaptchaResponse, recaptchaPrivateKey, h.getRemoteIP())
            # If the response is not valid,
            if not result.is_valid:
                return dict(isOk=0, rejection_count=person.rejection_count)
        # Get minutesOffset from UTC
        minutesOffset = h.getMinutesOffset()
        # Save session
        session['minutesOffset'] = minutesOffset
        session['personID'] = person.id
        session['nickname'] = person.nickname
        session['is_super'] = person.is_super
        session.save()
        # Save person
        person.minutes_offset = minutesOffset
        person.rejection_count = 0
        Session.commit()
        # Return
        return dict(isOk=1)

    def logout(self):
        'Logout'
        # If the person is logged in,
        if h.isPerson():
            del session['minutesOffset']
            del session['personID']
            del session['nickname']
            del session['is_super']
            session.save()
        # Redirect
        return redirect(request.GET.get('url', '/'))

    @jsonify
    def reset(self):
        'Reset password'
        # Get email
        email = request.POST.get('email')
        # Try to load the person
        person = Session.query(model.Person).filter(model.Person.email==email).first()
        # If the email is not in our database,
        if not person: 
            return dict(isOk=0)
        # Reset account
        c.password = store.makeRandomAlphaNumericString(parameter.PASSWORD_LENGTH_AVERAGE)
        return changePerson(dict(username=person.username, password=c.password, nickname=person.nickname, email=person.email), 'reset', person)


# Helpers

def changePerson(valueByName, action, person=None):
    'Validate values and send confirmation email if values are okay'
    # Validate form
    try:
        form = PersonForm().to_python(valueByName, person)
    except formencode.Invalid, error:
        return dict(isOk=0, errorByID=error.unpack_errors())
    # Prepare candidate
    candidate = model.PersonCandidate(form['username'], model.hashString(form['password']), form['nickname'], form['email'])
    candidate.person_id = person.id if person else None
    candidate.ticket = store.makeRandomUniqueTicket(parameter.TICKET_LENGTH, Session.query(model.PersonCandidate))
    candidate.when_expired = datetime.datetime.utcnow() + datetime.timedelta(days=parameter.TICKET_LIFESPAN_IN_DAYS)
    Session.add(candidate) 
    Session.commit()
    # Send confirmation
    toByValue = dict(nickname=form['nickname'], email=form['email'])
    subject = '[%s] Confirm %s' % (parameter.SITE_NAME, action)
    c.candidate = candidate
    c.username = form['username']
    c.action = action
    body = render('/people/confirm.mako')
    try:
        smtp.sendMessage(dict(email=config['error_email_from'], smtp=config['smtp_server'], username=config.get('smtp_username', ''), password=config.get('smtp_password', ''), nickname=parameter.SITE_NAME + ' Support'), toByValue, subject, body)
    except smtp.SMTPError:
        return dict(isOk=0, errorByID={'status': 'Unable to send confirmation; please try again later.'})
    # Return
    return dict(isOk=1)

def confirmPersonCandidate(ticket):
    'Move changes from the PersonCandidate table into the Person table'
    # Load
    candidate = Session.query(model.PersonCandidate).filter(model.PersonCandidate.ticket==ticket).filter(model.PersonCandidate.when_expired>=datetime.datetime.utcnow()).first()
    # If the ticket exists,
    if candidate:
        # If the person exists,
        if candidate.person_id:
            # Update
            person = Session.query(model.Person).get(candidate.person_id)
            person.username = candidate.username
            person.password_hash = candidate.password_hash
            person.nickname = candidate.nickname
            person.email = candidate.email
            # Reset
            person.rejection_count = 0
        # If the person does not exist,
        else:
            # Add person
            Session.add(model.Person(candidate.username, candidate.password_hash, candidate.nickname, candidate.email))
        # Commit
        Session.commit()
    # Return
    return candidate


# Validators

class Unique(formencode.validators.FancyValidator):
    'Validator to ensure unique values in a field'

    def __init__(self, fieldName, errorMessage):
        'Store fieldName and errorMessage'
        super(Unique, self).__init__()
        self.fieldName = fieldName
        self.errorMessage = errorMessage

    def _to_python(self, value, person):
        'Check whether the value is unique'
        # If the person is new or the value changed,
        if not person or getattr(person, self.fieldName) != value:
            # Make sure the value is unique
            if Session.query(model.Person).filter(getattr(model.Person, self.fieldName)==value).first():
                # Raise
                raise formencode.Invalid(self.errorMessage, value, person)
        # Return
        return value

class SecurePassword(formencode.validators.FancyValidator):
    'Validator to prevent weak passwords'

    def _to_python(self, value, person):
        'Check whether a password is strong enough'
        if len(set(value)) < 4:
            raise formencode.Invalid('That password needs more variety', value, person)
        return value

class PersonForm(formencode.Schema):
    'Validate person credentials'

    username = formencode.All(
        formencode.validators.String(
            min=parameter.USERNAME_LENGTH_MINIMUM,
            max=parameter.USERNAME_LENGTH_MAXIMUM,
        ),
        Unique('username', 'That username already exists'),
    )
    password = formencode.All(
        formencode.validators.MinLength(
            parameter.PASSWORD_LENGTH_MINIMUM, 
            not_empty=True,
        ), 
        SecurePassword(),
    )
    nickname = formencode.All(
        formencode.validators.PlainText(), 
        formencode.validators.UnicodeString(
            min=parameter.NICKNAME_LENGTH_MINIMUM, 
            max=parameter.NICKNAME_LENGTH_MAXIMUM,
        ),
        Unique('nickname', 'That nickname already exists'),
    )
    email = formencode.All(
        formencode.validators.Email(not_empty=True),
        Unique('email', 'That email is reserved for another account'),
    )
