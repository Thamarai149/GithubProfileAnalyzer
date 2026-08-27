import sys
import os

# Make the project root importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from backend.web_app import create_app

app = create_app()
