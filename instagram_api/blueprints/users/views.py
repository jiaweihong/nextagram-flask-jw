from flask import Blueprint, jsonify, request
from models.user import User
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity
)

users_api_blueprint = Blueprint('users_api',
                                __name__,
                                template_folder='templates')


@users_api_blueprint.route('/', methods=['GET'])
def index():
    return "USERS API"


@users_api_blueprint.route('/images')
def get_users_images():
    # this takes any query string params with key of 'userId'
    # using .get() will return None if the key does not exists but using request.args['key'] will return KeyError
    userId = request.args.get('userId')
    if userId:  # if userId is provided it will look for all the images related to this User
        user = User.get_by_id(userId)
        return jsonify([{"id": image.id, "url": image.image_url} for image in user.images])
    else:
        users = User.select()
        return jsonify([[{"id": image.id, "url": image.image_url} for image in user.images] for user in users])


@users_api_blueprint.route('/users')
def get_users_info():
    users = User.select()
    return jsonify([{"id": user.id, "username": user.username, "profileImage": user.profile_image_url} for user in users])


@users_api_blueprint.route('/users/<id>')
def get_user_info(id):
    user = User.get_by_id(id)
    profile_image = user.profile_image_url
    username = user.username
    return jsonify({"id": id, "profileImage": profile_image, "username": username})


@users_api_blueprint.route('/users/checkname/check_name')
def get_check_username():
    username = request.args.get('username')
    print(username)
    if username:
        print('if')
        duplicate_username = User.get_or_none(User.username == username)
        if duplicate_username:
            return jsonify({"exists": True, "valid": False})
        else:
            return jsonify({"exists": False, "valid": True})
    else:
        print('else')
        return "No username entered"


@users_api_blueprint.route('/user/me')
@jwt_required
def authorise_me_info():
    user_id = get_jwt_identity()
    user = User.get_by_id(user_id)
    return jsonify({"email": user.email, "id": user.id, "username": user.username, "profile_picture": user.profile_image_url})


@users_api_blueprint.route('/images/me')
@jwt_required
def authorise_me_images():
    user_id = get_jwt_identity()  # this function returns the value of the identity key
    user = User.get_by_id(user_id)
    return jsonify([image.image_url for image in user.images])
