from dotenv import load_dotenv

from .base import *

load_dotenv()

env_name = os.getenv("DJANGO_ENV", "development")

if env_name == "production":
    from .production import *
else:
    from .development import *
