from flask import Blueprint, render_template
from flask import render_template, request, redirect, url_for, flash
from models.user import User
import boto3
import botocore
from flask_login import login_required, current_user
import os
from models.following import Following
import peewee as pw


users_blueprint = Blueprint('users',
                            __name__,
                            template_folder='templates')


s3 = boto3.client(
    "s3",
    aws_access_key_id=os.environ.get("AWS_ACCESS"),
    aws_secret_access_key=os.environ.get("AWS_SECRET")
)


# since its under users_blueprint with a prefix of 'users', it will always start with '/users'
@users_blueprint.route("/new")
def new():
    # when rendering templates, you need to state which folder the html file is in with a '/'
    return render_template('users/new.html')


@users_blueprint.route("/new", methods=["POST"])
def create():
    username = request.form.get("username")
    email = request.form.get("email")
    password = request.form.get("password")
    # this just creates an object, it doesnt actually interact with the database
    user = User(username=username, email=email, password=password)
    if user.save():  # when '.save()' is called, it is calling the .save() in base_model.py.
        flash('Account Succesfully Created')
        return redirect(url_for('home'))
    else:  # When this runs, it will get the 'errors' list and pass it down to the template.
        return render_template('users/new.html', errors=user.errors)


@users_blueprint.route("/profile_image_upload")
@login_required
def profile_image_upload():
    return render_template('users/profile_image_upload.html')


@users_blueprint.route("/profile_image_upload", methods=["POST"])
@login_required
def profile_image_uploaded():
    # Use request.files when getting files
    profile_image_file = request.files.get("profile_image")
    # When saving an image_path, you save its filename
    current_user.profile_image_path = profile_image_file.filename
    # we are specifying that do_validate = false so validate() will not run
    current_user.save(do_validate=False)
    print(current_user.errors)
    # Try and except is used to handle errors that are small (user is using application as intended), when there is an error it will go to except.
    try:
        s3.upload_fileobj(  # this uploads the image to s3
            profile_image_file,
            # when using variables from ".env" you use os.environ.get("<var>"). Need to import "os".
            os.environ.get("AWS_BUCKET"),
            profile_image_file.filename,
            ExtraArgs={
                "ACL": "public-read",
                "ContentType": profile_image_file.content_type
            }
        )
        flash(
            f"Profile Image Succesfully Uploaded! Link: {current_user.profile_image_url}")
        return redirect(url_for('users.profile_image_upload'))
    # You can print the error message to console then redirect the user to the homepage and flash() something went wrong.
    except Exception as e:
        print("Something happened: ", e)
        flash(f"Something went wrong: {current_user.profile_image_url}")
        return redirect(url_for('users.profile_image_upload'))


@users_blueprint.route("/<username>")
@login_required
def profile_page(username):
    user = User.get_or_none(User.username == username)
    is_following = Following.get_or_none((Following.followed_id == user.id) & (
        Following.follower_id == current_user.id) & (Following.is_approved == True))
    is_waiting_to_approve = Following.get_or_none((Following.followed_id == user.id) & (
        Following.follower_id == current_user.id) & (Following.is_approved == False))
    if user:
        return render_template("users/profile_page.html", user=user, is_following=is_following, is_waiting_to_approve=is_waiting_to_approve)
    else:
        return render_template("404.html")


@users_blueprint.route("/<username>", methods=["POST"])
@login_required
def profile_page_followed(username):
    user = User.get_or_none(User.username == username)
    if user.is_public:  # if public
        # will accept all followers
        following = Following(
            followed=user.id, follower=current_user.id, is_approved=True)
        if following.save():
            flash("followed succesful")
            return redirect(url_for('users.profile_page', username=user.username))
            # url_for()/render_template() 1) When using redirect(url_for()), it will rerun the function so you generally do not need to pass in any values
        else:  # to handle errors
            is_following = Following.get_or_none((Following.followed_id == user.id) & (
                Following.follower_id == current_user.id) & (Following.is_approved == True))
            is_waiting_to_approve = Following.get_or_none((Following.followed_id == user.id) & (
                Following.follower_id == current_user.id) & (Following.is_approved == False))
            return render_template("users/profile_page.html", errors=following.errors, user=user, is_following=is_following, is_waiting_to_approve=is_waiting_to_approve)
            # url_for()/render_template() 2) When using render_template(), it will render the html directly without running the function so you need to pass in all the variables required to properly run the html
    else:  # if private
        # will make an instance but will need to be approved
        following = Following(
            followed=user.id, follower=current_user.id, is_approved=False)
        following.save()
        return redirect(url_for('users.profile_page', username=user.username))


@users_blueprint.route("/follower_accepted", methods=["POST"])
@login_required
def accept_follower_request():
    follower_id = request.form.get("follower_id")
    followed_id = request.form.get("followed_id")
    following_instance = Following.get_or_none((Following.followed == followed_id) & (
        Following.follower == follower_id))  # gets the instance
    # edits the is_approved from False to True
    following_instance.is_approved = True
    following_instance.save()
    return redirect(url_for('users.profile_page', username=current_user.username))
