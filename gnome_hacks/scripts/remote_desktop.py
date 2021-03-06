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

            class App {
                constructor() {
                    this.cur_screenshot = null;
                    this.running_event = false;
                    this.event_queue = [];
                }

                run() {
                    this.refreshLoop();
                    window.addEventListener('keydown', (e) => this.handleKeyEvent(e, true));
                    window.addEventListener('keyup', (e) => this.handleKeyEvent(e, false));
                }

                async runEvents(events) {
                    if (this.running_event) {
                        events.forEach((e) => this.event_queue.push(e));
                        return;
                    }
                    this.running_event = true;
                    const data = encodeURIComponent(JSON.stringify(events));
                    try {
                        await fetch('/input?events=' + data);
                    } catch (e) {
                    }
                    this.running_event = false;
                    if (this.event_queue.length > 0) {
                        const e = this.event_queue;
                        this.event_queue = [];
                        this.runEvents(e);
                    }
                }


                showScreenshot(img) {
                    const coordFn = mouseCoordFn(img);
                    img.className = 'screenshot';
                    if (this.cur_screenshot != null) {
                        document.body.insertBefore(img, this.cur_screenshot);
                        document.body.removeChild(this.cur_screenshot);
                    } else {
                        document.body.appendChild(img);
                    }
                    this.cur_screenshot = img;
                    img.onmousemove = (e) => {
                        this.runEvents([{mousemove: coordFn(e)}]);
                        e.preventDefault();
                        e.stopPropagation();
                        return false;
                    };
                    img.onmousedown = (e) => {
                        this.runEvents([
                            {mousemove: coordFn(e)},
                            {mousebutton: {pressed: true}},
                        ]);
                        e.preventDefault();
                        e.stopPropagation();
                        return false;
                    };
                    img.onmouseup = (e) => {
                        this.runEvents([
                            {mousemove: coordFn(e)},
                            {mousebutton: {pressed: false}},
                        ]);
                        e.preventDefault();
                        e.stopPropagation();
                        return false;
                    };
                }

                async refreshLoop() {
                    while (true) {
                        const lastTime = new Date().getTime();
                        try {
                            const result = await loadScreenshotAsync();
                            this.showScreenshot(result);
                            const curTime = new Date().getTime();
                            await sleepAsync(REFRESH_RATE + lastTime - curTime);
                        } catch (e) {
                            await sleepAsync(1000);
                            continue;
                        }
                    }
                }

                handleKeyEvent(e, pressed) {
                    this.runEvents([{keypress: {keycode: e.which, pressed: pressed}}]);
                    e.preventDefault();
                    e.stopPropagation();
                    return false;
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

            window.app = new App();
            window.app.run();
            </script>
        </body>
    </html>
    """


@app.route("/screenshot")
def screenshot():
    quality = int(request.args.get("q", "50"))

    with lock:
        png_data = capture_screenshot(evaluator)
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
                simulate_key_events(evaluator, *events)
            else:
                simulate_pointer_events(evaluator, *events)
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
        32: KeyVal.KEY_space,
        46: KeyVal.KEY_Delete,
        186: KeyVal.KEY_semicolon,
        187: KeyVal.KEY_equal,
        188: KeyVal.KEY_comma,
        189: KeyVal.KEY_minus,
        190: KeyVal.KEY_period,
        191: KeyVal.KEY_slash,
        192: KeyVal.KEY_grave,
        219: KeyVal.KEY_bracketleft,
        220: KeyVal.KEY_backslash,
        221: KeyVal.KEY_bracketright,
        222: KeyVal.KEY_apostrophe,
    }
    return tbl.get(x, 0xFF00 + x)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
