from flask import Flask
app = Flask(__name__)

# Import and register routes from views.py
from .views import bp

app.register_blueprint(bp)