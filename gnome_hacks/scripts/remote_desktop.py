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
                img.className = 'screenshot';
                if (CUR_SCREENSHOT != null) {
                    document.body.insertBefore(img, CUR_SCREENSHOT);
                    document.body.removeChild(CUR_SCREENSHOT);
                } else {
                    document.body.appendChild(img);
                }
                CUR_SCREENSHOT = img;
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
        png_data = capture_screenshot(evaluator, timeout_ms=10000)
    img = Image.open(io.BytesIO(png_data))
    out = io.BytesIO()
    img.convert("RGB").save(out, format="jpeg", quality=quality)
    return Response(out.getvalue(), mimetype="image/jpeg")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
