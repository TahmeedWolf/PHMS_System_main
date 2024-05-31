from functools import wraps
from flask import abort, render_template, request
from Models.Users import *
from flask_login import login_required, current_user
from sqlalchemy import text
from Models.Authentication import *
from extension import db

# To create admin-only decorator
def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # If id is not 1 then return abort with 403 error
        if current_user.permission != "admin":
            # return abort(403)
            return render_template('home/page-unauthorized.html'), 200
        # Otherwise continue with the route function
        return f(*args, **kwargs)        
    return decorated_function

# To create doctor_admin_only decorator
def doctor_admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # If id is not 1 then return abort with 403 error
        if current_user.permission == "admin" or current_user.permission == "doctor":
            pass
        else:
            # return abort(403)
            return render_template('home/page-unauthorized.html'), 200
        # Otherwise continue with the route function
        return f(*args, **kwargs)        
    return decorated_function

# To get all information and log it into Access_Log table
def access_log(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get all informations
        user_agent = request.user_agent.string
        user_id = current_user.user_id
        verb = request.method
        ip = request.access_route
        what = request.url
        access_log_item = Access_Log(user_agent=user_agent,user_id=user_id,verb=verb,ip=ip,what=what)
        db.session.add(access_log_item)
        db.session.commit()
        return f(*args, **kwargs)
    return decorated_function