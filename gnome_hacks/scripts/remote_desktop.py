"""
Work-in-progress remote desktop web application.
"""

import io
from threading import Lock

from flask import Flask, Response, request
from gnome_hacks.evaluator import Evaluator
from gnome_hacks.keyboard import KeyEvent, simulate_key_events
from gnome_hacks.pointer import PointerButton, PointerMove, simulate_pointer_events
from gnome_hacks.screenshot import capture_screenshot
from PIL import Image

app = Flask(__name__)
lock = Lock()
evaluator = Evaluator()

TIMEOUT = 10000


@app.route("/")
def index():
    return """
    <!doctype html>
    <html>
        <head>
            <style>
            html, body {
                text-align: center;
            }

            .screenshot {
                max-width: 90%;
                max-height: 90%;
            }
            </style>
        </head>
        <body>
            <script>
            const REFRESH_RATE = 1000;
            let CUR_SCREENSHOT = null;

            let MOVING = false;
            let NEXT_MOVE = null;

            async function moveMouse(x, y) {
                if (MOVING) {
                    NEXT_MOVE = [x, y];
                    return;
                }
                MOVING = true;
                try {
                    await fetch('/mouse/move?x=' + x + '&y=' + y);
                } catch (e) {
                }
                MOVING = false;
                if (NEXT_MOVE) {
                    const m = NEXT_MOVE;
                    NEXT_MOVE = null;
                    moveMouse(m[0], m[1]);
                }
            }

            function sleepAsync(time) {
                return new Promise((resolve, reject) => {
                    if (time <= 0) {
                        resolve(null);
                    } else {
                        setTimeout(() => resolve(null), time);
                    }
                });
            }

            function loadScreenshotAsync() {
                return new Promise((resolve, reject) => {
                    const img = document.createElement('img');
                    img.onload = () => resolve(img);
                    img.onerror = (err) => reject(err);
                    img.src = '/screenshot?timestamp=' + (new Date().getTime());
                });
            }

            function showScreenshot(img) {
                const width = img.width;
                img.className = 'screenshot';
                if (CUR_SCREENSHOT != null) {
                    document.body.insertBefore(img, CUR_SCREENSHOT);
                    document.body.removeChild(CUR_SCREENSHOT);
                } else {
                    document.body.appendChild(img);
                }
                CUR_SCREENSHOT = img;
                img.onmousemove = (e) => {
                    const rect = img.getBoundingClientRect();
                    const scale = width / img.offsetWidth;
                    const x = Math.round(scale * (e.clientX - rect.left));
                    const y = Math.round(scale * (e.clientY - rect.top));
                    moveMouse(x, y);
                    e.preventDefault();
                    e.stopPropagation();
                    return false;
                };
            }

            async function refreshLoop() {
                while (true) {
                    const lastTime = new Date().getTime();
                    try {
                        const result = await loadScreenshotAsync();
                        showScreenshot(result);
                        const curTime = new Date().getTime();
                        await sleepAsync(REFRESH_RATE + lastTime - curTime);
                    } catch (e) {
                        await sleepAsync(1000);
                        continue;
                    }
                }
            }
            refreshLoop().then(() => null);
            </script>
        </body>
    </html>
    """


@app.route("/screenshot")
def screenshot():
    quality = int(request.args.get("q", "50"))

    with lock:
        png_data = capture_screenshot(evaluator, timeout_ms=TIMEOUT)
    img = Image.open(io.BytesIO(png_data))
    out = io.BytesIO()
    img.convert("RGB").save(out, format="jpeg", quality=quality)
    return Response(out.getvalue(), mimetype="image/jpeg")


@app.route("/mouse/move")
def move_mouse():
    x = int(request.args.get("x", "0"))
    y = int(request.args.get("y", "0"))
    with lock:
        simulate_pointer_events(evaluator, PointerMove(x, y), timeout_ms=TIMEOUT)
    return "ok"


@app.route("/mouse/press")
def press_mouse():
    pressed = request.args.get("pressed", "0") == "1"
    with lock:
        simulate_pointer_events(evaluator, PointerButton(pressed), timeout_ms=TIMEOUT)
    return "ok"


@app.route("/keyboard")
def keyboard():
    keyval = int(request.args.get("keyval", ""))
    pressed = request.args.get("pressed", "0") == "1"
    with lock:
        simulate_key_events(evaluator, KeyEvent(pressed, keyval=keyval), timeout_ms=TIMEOUT)
    return "ok"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
