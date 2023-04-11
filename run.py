from app import app
from app import celery
# Both needed

app.app_context().push()
