from app import app
from flask import render_template, request, redirect, url_for, flash
from instagram_web.blueprints.users.views import users_blueprint
from instagram_web.blueprints.sessions.views import sessions_blueprint
from instagram_web.blueprints.images.views import images_blueprint
from instagram_web.blueprints.payments.views import payments_blueprint
from flask_assets import Environment, Bundle
from .util.assets import bundles
from models.user import User
import os
from instagram_web.blueprints.sessions.google_oauth import oauth
import config

app.secret_key = os.environ.get("APP_SECRET")

assets = Environment(app)
assets.register(bundles)
oauth.init_app(app)

app.register_blueprint(users_blueprint, url_prefix="/users")
app.register_blueprint(sessions_blueprint, url_prefix="/login")
app.register_blueprint(images_blueprint, url_prefix="/images")
app.register_blueprint(payments_blueprint, url_prefix="/payments")

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

@app.errorhandler(403)
def forbidden_page(e):
    return render_template("403.html"), 403

@app.errorhandler(401)
def authorization_page(e):
    return forbidden_page(e)

@app.route("/")
def home():
    return render_template('home.html')




    
