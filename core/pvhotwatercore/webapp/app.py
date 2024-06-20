"""This will be loaded to create the Flask app."""

from flask import Flask
from flask_bootstrap import Bootstrap  # type: ignore[import-untyped]

from .blueprints import test_page

# Create Flask app
app = Flask(
    __name__,
    static_url_path="/static",
    static_folder="static",
    template_folder="templates"
)

# Set up Flask-Bootstrap
Bootstrap(app)

# Register blueprints
app.register_blueprint(test_page.bp)
