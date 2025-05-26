"""Application configuration."""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Flask settings
FLASK_APP = os.getenv('FLASK_APP', 'run.py')
FLASK_ENV = os.getenv('FLASK_ENV', 'development')