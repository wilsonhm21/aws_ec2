from flask import Flask
import os

app = Flask(__name__)

# Clave secreta para sesiones y flash
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'clave-por-defecto-123')

from . import views
