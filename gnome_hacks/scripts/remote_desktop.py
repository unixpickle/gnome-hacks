"""
Work-in-progress remote desktop web application.
"""

import io

from flask import Flask, request
from PIL import Image

from gnome_hacks.evaluator import Evaluator
from gnome_hacks.screenshot import capture_screenshot

app = Flask(__name__)


@app.route("/")
def index():
    return """
    <!doctype html>
    <html>
        <head>
        </head>
        <body>
            TODO: a UI for controlling the screen.
        </body>
    </html>
    """


@app.route("/screenshot")
def screenshot():
    quality = int(request.args.get("q", "50"))

    e = Evaluator()
    png_data = capture_screenshot(e)
    img = Image.open(io.BytesIO(png_data))
    out = io.BytesIO()
    img.save(out, format="jpeg", quality=quality)
    return out.getvalue()
