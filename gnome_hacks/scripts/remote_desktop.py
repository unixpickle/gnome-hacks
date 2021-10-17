"""
Work-in-progress remote desktop web application.
"""

import io
import json
from threading import Lock

from flask import Flask, Response, request
from gnome_hacks.evaluator import Evaluator
from gnome_hacks.keyboard import KeyEvent, simulate_key_events
from gnome_hacks.keysyms import KeyVal
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

            let RUNNING_EVENT = false;
            let EVENT_QUEUE = [];

            async function runEvents(events) {
                if (RUNNING_EVENT) {
                    events.forEach((e) => EVENT_QUEUE.push(e));
                    return;
                }
                RUNNING_EVENT = true;
                const data = encodeURIComponent(JSON.stringify(events));
                try {
                    await fetch('/input?events=' + data);
                } catch (e) {
                }
                RUNNING_EVENT = false;
                if (EVENT_QUEUE.length > 0) {
                    const e = EVENT_QUEUE;
                    EVENT_QUEUE = [];
                    runEvents(e);
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

            function mouseCoordFn(img) {
                const width = img.width;
                return (e) => {
                    const rect = img.getBoundingClientRect();
                    const scale = width / img.offsetWidth;
                    const x = Math.round(scale * (e.clientX - rect.left));
                    const y = Math.round(scale * (e.clientY - rect.top));
                    return {x: x, y: y};
                };
            }

            function showScreenshot(img) {
                const coordFn = mouseCoordFn(img);
                img.className = 'screenshot';
                if (CUR_SCREENSHOT != null) {
                    document.body.insertBefore(img, CUR_SCREENSHOT);
                    document.body.removeChild(CUR_SCREENSHOT);
                } else {
                    document.body.appendChild(img);
                }
                CUR_SCREENSHOT = img;
                img.onmousemove = (e) => {
                    runEvents([{mousemove: coordFn(e)}]);
                    e.preventDefault();
                    e.stopPropagation();
                    return false;
                };
                img.onmousedown = (e) => {
                    runEvents([
                        {mousemove: coordFn(e)},
                        {mousebutton: {pressed: true}},
                    ]);
                    e.preventDefault();
                    e.stopPropagation();
                    return false;
                };
                img.onmouseup = (e) => {
                    runEvents([
                        {mousemove: coordFn(e)},
                        {mousebutton: {pressed: false}},
                    ]);
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

            function handleKeyEvent(e, pressed) {
                runEvents([{keypress: {keycode: e.which, pressed: pressed}}]);
                e.preventDefault();
                e.stopPropagation();
                return false;
            }

            refreshLoop();
            window.addEventListener('keydown', (e) => handleKeyEvent(e, true));
            window.addEventListener('keyup', (e) => handleKeyEvent(e, false));
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


@app.route("/input")
def simulate_input():
    event_data = json.loads(request.args.get("events"))
    events = []

    def flush_events():
        if not len(events):
            return
        with lock:
            if isinstance(events[0], KeyEvent):
                simulate_key_events(evaluator, *events, timeout_ms=TIMEOUT)
            else:
                simulate_pointer_events(evaluator, *events, timeout_ms=TIMEOUT)
        events.clear()

    for obj in event_data:
        if "mousemove" in obj:
            evt = PointerMove(obj["mousemove"]["x"], obj["mousemove"]["y"])
        if "mousebutton" in obj:
            evt = PointerButton(obj["mousebutton"]["pressed"])
        elif "keypress" in obj:
            evt = KeyEvent(
                obj["keypress"]["pressed"],
                keycode_to_keyval(obj["keypress"]["keycode"]),
            )
        if len(events) and isinstance(evt, KeyEvent) != isinstance(events[0], KeyEvent):
            # Cannot intertwine mouse and keyboard events.
            flush_events()
        events.append(evt)
    flush_events()
    return "ok"


def keycode_to_keyval(x):
    caps = range(b"A"[0], b"Z"[0] + 1)
    if x in caps:
        return x + (b"a"[0] - b"A"[0])
    if x in range(b"0"[0], b"9"[0] + 1):
        return x
    tbl = {
        16: KeyVal.KEY_Shift_L,
        17: KeyVal.KEY_Control_L,
        18: KeyVal.KEY_Alt_L,
        187: KeyVal.KEY_equal,
        189: KeyVal.KEY_minus,
        191: KeyVal.KEY_slash,
        192: KeyVal.KEY_grave,
        219: KeyVal.KEY_bracketleft,
        220: KeyVal.KEY_backslash,
        221: KeyVal.KEY_bracketright,
    }
    return tbl.get(x, 0xFF00 + x)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
