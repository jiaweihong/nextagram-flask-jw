import peewee as pw
from models.base_model import BaseModel
from models.user import User

class Payment(BaseModel):
    amount = pw.DecimalField(null=False)
    transaction_id = pw.CharField(null=False)
    user = pw.ForeignKeyField(User, backref="payments")




