from models.base_model import db
import peeweedbevolve
# make sure to check that the order in which u import stuff makes sense
from models import *
import os

os.environ['MIGRATION'] = '1'

if not os.getenv('FLASK_ENV') == 'production':
    print("Loading environment variables from .env!")
    from dotenv import load_dotenv
    load_dotenv()


print("Running Migration")
if os.getenv('FLASK_ENV') == 'production':
    db.evolve(ignore_tables={'base_model'}, interactive=False)
else:
    db.evolve(ignore_tables={'base_model'})
print("Finish Migration")
