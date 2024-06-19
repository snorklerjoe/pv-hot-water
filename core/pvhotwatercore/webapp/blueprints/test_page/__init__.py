"""Test page template; contains just a hello world."""

from flask import Blueprint, render_template


bp = Blueprint("test-page", __name__, url_prefix="/test-page",
               template_folder="templates")


@bp.route("/")
@bp.route("/index.html")
def about() -> str:
    """Renders the test page."""
    return render_template("test_page/index.html")
