import os
import config
from flask import Flask
from models.base_model import db
from flask_login import LoginManager
from models.user import User
from flask_jwt_extended import JWTManager

web_dir = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), 'instagram_web')

app = Flask('NEXTAGRAM', root_path=web_dir)


if os.getenv('FLASK_ENV') == 'production':
    app.config.from_object("config.ProductionConfig")
else:
    app.config.from_object("config.DevelopmentConfig")

login_manager = LoginManager()
login_manager.init_app(app)
jwt = JWTManager(app)


@login_manager.user_loader
# the argument is provided by login_user, once provided, we use it to get the object instance of the id.
def load_user(id):
    # 'current_user" now refers to this returned object instance
    return User.get_by_id(id)
    # the reason why it returns id instead of object is because if the object is updated, the pre-updated object instance will be slightly different to the post-update object instance. So by referencing ID it will be stable


@app.before_request
def before_request():
    db.connect()


@app.teardown_request
def _db_close(exc):
    if not db.is_closed():
        print(db)
        print(db.close())
    return exc
