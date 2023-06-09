DEBUG = True

# Define the application directory
import os
import uuid

BASE_DIR = os.path.abspath(os.path.dirname(__file__))  

# Define the database - we are working with
# SQLite for this example
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'app.db')
DATABASE_CONNECT_OPTIONS = {}

UPLOAD_FOLDER = os.path.join(BASE_DIR) + '/app/static/uploads' 

# Application threads. A common general assumption is
# using 2 per available processor cores - to handle
# incoming requests using one and performing background
# operations using the other.
THREADS_PER_PAGE = 2

# Enable protection agains *Cross-site Request Forgery (CSRF)*
CSRF_ENABLED     = True

# Use a secure, unique and absolutely secret key for
# signing the data. 
CSRF_SESSION_KEY = uuid.uuid4().hex

# Secret key for signing cookies
SECRET_KEY = uuid.uuid4().hex

CELERY_CONFIG = {"broker_url": "redis://redis", "result_backend": "redis://redis"}

static_folder="/static" 
