"""This will be loaded to create the Flask app."""

from flask import Flask

from .blueprints import test_page

app = Flask(__name__)

app.register_blueprint(test_page.bp)
