import peewee as pw
from models.base_model import BaseModel
from models.user import User


class Following(BaseModel):
    # Backref 1) Doing user_instance.backref will give you a list of instances from this class that is linked to user_instance.
    # Backref 2) user_instance.backref[0] = <Follow: 1> (The first instance of the Follow class)
    # Backref 3) user_instance.backref[0].follower = <User: 2> as it is the value of the follower column for the first instance of the Follow class. Which in this case is a ForeignKeyField that links to follower's user's object.

    followed = pw.ForeignKeyField(User)
    follower = pw.ForeignKeyField(User)
    is_approved = pw.BooleanField(null=True)
    

    def validate(self):
        if Following.get_or_none((Following.followed_id == self.followed) & (Following.follower_id == self.follower) & (Following.is_approved==True)):
            self.errors.append("You already follow this user")
            
        if self.followed == self.follower:
            self.errors.append("You cannot follow yourself")
            
        


