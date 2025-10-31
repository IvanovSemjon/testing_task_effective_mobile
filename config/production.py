from .base import *

DEBUG = False
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "").split(",")
if not SECRET_KEY: raise Exception("SECRET_KEY is not set!")