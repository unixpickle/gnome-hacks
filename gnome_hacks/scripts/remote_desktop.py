"""
Work-in-progress remote desktop web application.
"""

import io
from threading import Lock

from flask import Flask, Response, request
from PIL import Image

from gnome_hacks.evaluator import Evaluator
from gnome_hacks.screenshot import capture_screenshot

app = Flask(__name__)
lock = Lock()
evaluator = Evaluator()


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

    with lock:
        png_data = capture_screenshot(evaluator, timeout_ms=10000)
    img = Image.open(io.BytesIO(png_data))
    out = io.BytesIO()
    img.convert("RGB").save(out, format="jpeg", quality=quality)
    return Response(out.getvalue(), mimetype="image/jpeg")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
