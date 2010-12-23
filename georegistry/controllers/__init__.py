'General decorators'
# Import pylons modules
from pylons import request, url
from pylons.controllers.util import redirect
# Import system modules
from decorator import decorator
# Import custom modules
from georegistry.lib import helpers as h


# Authentication

@decorator
def requireLogin(func, *args, **kwargs):
    'Redirect to login if the user is not logged in'
    # If the user is not logged in,
    if not h.isPerson():
        return redirect(url('person_login', url=request.path))
    # Execute
    return func(*args, **kwargs)

@decorator
def requireLoginJSON(func, *args, **kwargs):
    'Give error message if the user is not logged in'
    # If the user is not logged in,
    if not h.isPerson():
        return dict(isOk=0, message='Login required')
    # Execute
    return func(*args, **kwargs)


# Authorization

@decorator
def requireSuper(func, *args, **kwargs):
    'Redirect to homepage if the user is not a superuser'
    # If the user is not a superuser,
    if not h.isPersonSuper():
        return redirect(url('person_login', url='/'))
    # Execute
    return func(*args, **kwargs)

@decorator
def requireSuperJSON(func, *args, **kwargs):
    'Give error message if the user is not a superuser'
    # If the user is not a superuser,
    if not h.isPersonSuper():
        return dict(isOk=0, message='Access denied')
    # Execute
    return func(*args, **kwargs)
