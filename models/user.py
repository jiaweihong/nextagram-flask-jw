from models.base_model import BaseModel
import peewee as pw
from werkzeug.security import generate_password_hash
from flask_login import UserMixin
from playhouse.hybrid import hybrid_property
import os

class User(BaseModel, UserMixin): #Usermixin makes it such that when a user is created it comes with these classes install: is_authenticated(), is_active(), is_anonymous() and get_id()
    username = pw.CharField(unique=True, null=False) #these database constraints are only triggered at the very end right before it is submitted to the database
    email = pw.CharField(unique=True, null=False)
    password = pw.CharField(unique=False, null=False)
    profile_image_path = pw.CharField(null=True)
    is_public = pw.BooleanField(default=True) # All accounts created will have a public profile

    @hybrid_property # Is used to make a function that includes a property from the class but the function itself doesnt need to be a property for the class
    def profile_image_url(self): 
        if self.profile_image_path:
            # You reference this function like a class property e.g object.profile_image_url instead of object.profile_image_url()
            return os.environ.get('AWS_S3_DOMAIN') + self.profile_image_path

    @hybrid_property
    def followers(self):
        from models.following import Following
        return User.select().join(Following, on=(User.id==Following.follower_id)).where((self.id==Following.followed_id) & (Following.is_approved==True))
        # join() says I am joining User's table with Following's table
        # where() says to retrieve the rows where the person's id (whos followers we are trying to look at) matches the followed_id as it gives us the follower column
        # on() is because follower_id is a foreign key of User.id so they are the same

    @hybrid_property
    def followings(self):
        from models.following import Following
        return User.select().join(Following, on=(User.id==Following.followed_id)).where((self.id==Following.follower_id) & (Following.is_approved==True))

    @hybrid_property
    def pending_follower_requests(self):
        from models.following import Following
        return User.select().join(Following, on=(User.id==Following.follower_id)).where((self.id==Following.followed_id) & (Following.is_approved==False))

    def validate(self):
        duplicate_username = User.get_or_none(User.username == self.username) # 'get_or_none' first requires a table column to check against ie. 'User.username' and the value it is comparing to ie. 'self.username'. If there is no match it returns 'None'
        duplicate_email = User.get_or_none(User.email == self.email)
        special_characters = "@_!#$%^&*()<>?/\|}{~:]"

        # If no matches, it will not append anything to errors list. Meaning it will run the 'if' code and save it
        if duplicate_email:
            self.errors.append('Email is taken')

        if duplicate_username:
            self.errors.append('Username is taken')

        if len(self.password) <= 7:
            self.errors.append('Password has be greater than 6 characters')
        
        if not any(char.isupper() for char in self.password):
            self.errors.append('Need atleast 1 uppercase')
        
        if not any(char.islower() for char in self.password):
            self.errors.append('Need atleast 1 lowercase')

        if not any([True if char in special_characters else False for char in self.password]):
            self.errors.append("need atleast 1 special characters")

        self.password = generate_password_hash(self.password) # you only want to has your password after doing all your validations    

 