import peewee as pw 
from models.base_model import BaseModel
from models.user import User
from playhouse.hybrid import hybrid_property
import os

class Image(BaseModel):
    image_path = pw.CharField(null=True)
    user = pw.ForeignKeyField(User, backref="images")

    @hybrid_property
    def image_url(self):
        return os.environ.get('AWS_S3_DOMAIN') + self.image_path
