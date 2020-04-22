import os
import peewee as pw
import datetime
from database import db


class BaseModel(pw.Model):
    created_at = pw.DateTimeField(default=datetime.datetime.now)
    updated_at = pw.DateTimeField(default=datetime.datetime.now)

    def save(self, do_validate=True, *args, **kwargs): # do_validate will always be set to True and excecuted unless specified otherwise. 
        self.errors = []
        if do_validate: # it will set errors list to 0 and called the validate to see if the there are any errors that need to be added to the list.
            self.validate()
            # If there are multiple validate() function, it will call validate() base on the class that the object was created that called save(), if it doesnt have validate() inside of the class it looks up the heritance tree which would be BaseModel
            # I.e it was user.save() it will first look for validate() in user then only go to BaseModel

        if len(self.errors) == 0:
            self.updated_at = datetime.datetime.now()
            return super(BaseModel, self).save(*args, **kwargs)
        else:
            return 0

    def validate(self):
        print(
            f"Warning validation method not implemented for {str(type(self))}")
        return True

    class Meta:
        database = db
        legacy_table_names = False
