from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import check_password_hash
from models.user import User
from flask_login import login_user, login_required, logout_user, current_user
from instagram_web.blueprints.sessions.google_oauth import oauth


sessions_blueprint = Blueprint('sessions',
                            __name__,
                            template_folder='templates')
                            
@sessions_blueprint.route("/new")
def new():
    return render_template('sessions/new.html') 

@sessions_blueprint.route('/new', methods=['POST'])
def create():
    errors = []
    username_to_check = request.form.get('username')
    password_to_check = request.form.get('password')
    user = User.get_or_none(User.username == username_to_check) # if correct, it will return the object instance
    if not user:
        errors.append('Username is incorrect')
        return render_template('sessions/new.html', errors=errors )
    else: 
        hashed_password = user.password
        result = check_password_hash(hashed_password, password_to_check)
        if not result:
            errors.append('Password is incorrect')
            return render_template('sessions/new.html', errors=errors )
        else: 
            flash('Succesfully Logged In')
            login_user(user) # takes the id of the user object and saves it to the login_manager, it will then pass it to the 'load_user' function
            return redirect(url_for('home'))


@sessions_blueprint.route("/google_login")
def google_login():
    redirect_uri = url_for('sessions.authorize', _external = True) # Oauth 3) This generates the URL that the user should be redirected to after authorization is complete
    return oauth.google.authorize_redirect(redirect_uri) # Oauth 4) This authorizes a particular URL to have access to the authentication code and opens up the google sign in

@sessions_blueprint.route("/authorize/google")
def authorize():
    oauth.google.authorize_access_token() # Oauth 5) This exchanges the auth code for a token 
    email = oauth.google.get('https://www.googleapis.com/oauth2/v2/userinfo').json()['email'] # Oauth 5) Using the token to make an API call to retrieve data (end)
    user = User.get_or_none(User.email == email)
    if user:
        print("1")
        login_user(user)
        flash('Succesfully Logged In')
        return redirect(url_for('home'))
    else:
        print("2")
        flash('Email does not match database')
        return redirect(url_for('home'))


@sessions_blueprint.route('/logout')
@login_required
def logout():
    logout_user() # will logged the user out and clear any session cookies
    flash("succesfully logged out")
    return redirect(url_for('home'))

@sessions_blueprint.route('/setting')
@login_required
def setting():
    username = current_user.username
    return render_template('sessions/setting.html', username=username)

@sessions_blueprint.route('/setting_username', methods=['POST'])
@login_required
def update():
    username_to_update = request.form.get('username')
    print("look here 1")
    current_user.username = username_to_update
    current_user.save(do_validate=False)
    flash('username updated')
    return redirect(url_for('sessions.setting'))

@sessions_blueprint.route('/setting_privacy', methods=['POST']) # Need to have different route names if there are multiple functions
@login_required
def update_is_public():
    is_public_to_update = request.form.get('is_public') # HTML values are always given as a string so we need to convert them ourselves
    if is_public_to_update == "True":
        is_public_to_update = True
    else:
        is_public_to_update = False
    current_user.is_public = is_public_to_update
    if current_user.save(do_validate=False):
        print(current_user.is_public)
        flash('privacy settings updated')
        return redirect(url_for('sessions.setting'))
    else:
        return redirect(url_for('sessions.setting'))







    
                    