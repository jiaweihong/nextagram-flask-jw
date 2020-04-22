from flask import Blueprint, render_template
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
import os
import boto3, botocore
from models.image import Image

images_blueprint = Blueprint('images',
                            __name__,
                            template_folder='templates')


s3 = boto3.client(
    "s3",
    aws_access_key_id=os.environ.get("AWS_ACCESS"),
    aws_secret_access_key=os.environ.get("AWS_SECRET")
)

@images_blueprint.route("/new")
@login_required
def new():
    return render_template('images/new.html')

@images_blueprint.route("/new", methods=["POST"])
@login_required
def create():
    try:
        image_file = request.files.get("image")
        image_path = image_file.filename
        s3.upload_fileobj( 
            image_file,
            os.environ.get("AWS_BUCKET"), 
            image_path,
            ExtraArgs={
                "ACL": "public-read",
                "ContentType": image_file.content_type
            }
        )
        image = Image(image_path=image_path, user=current_user.id)
        image.save()
        flash(f"Image uploaded: {image.image_url}")
        return redirect(url_for('images.new'))
    except Exception as e:
        print("Something went wrong:", e)
        return redirect(url_for('images.new'))

