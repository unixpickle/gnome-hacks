import base64
import os
import time
import uuid

from .evaluator import Evaluator, EvaluatorJavaScriptError


def capture_screenshot(
    e: Evaluator,
    include_cursor: bool = True,
    **kwargs,
) -> bytes:
    """
    Capture a screenshot as PNG data.

    Only one screenshot operation can take place at once.
    Otherwise, an exception will be thrown.

    :param e: the script evaluator.
    :param include_cursor: if True, render the cursor in the screenshot.
    :param kwargs: arguments to e.call_promise().
    :return: PNG image data of the screenshot.
    """

    code = """
    const Screenshot = imports.gi.Shell.Screenshot;
    const GLib = imports.gi.GLib;
    const Gio = imports.gi.Gio;
    return await new Promise((resolve, reject) => {
        const ss = new Screenshot();
        let output = '';
        if (use_file) {
            output = use_file;
        } else {
            output = Gio.MemoryOutputStream.new_resizable()
        }

        if (ss.screenshot_finish) {
            ss.screenshot(include_cursor, output, (_, async_result) => {
                try {
                    const result = ss.screenshot_finish(async_result);
                    if (use_file) {
                        resolve(result[2]);
                    } else {
                        output.close(Gio.Cancellable.get_current());
                        const data = output.steal_as_bytes();
                        const encoded = GLib.base64_encode(data.get_data());
                        resolve(encoded);
                    }
                } catch (e) {
                    reject(e);
                }
            });
        } else {
            if (!use_file) {
                // This is an older branch of gnome-shell that doesn't use GIO's async pattern.
                // This old branch only had filename support.
                reject('must use filename');
                return;
            }
            ss.screenshot(include_cursor, output, (_, success, _area, filename) => {
                if (!success) {
                    reject('screeshot failed');
                } else {
                    resolve(filename);
                }
            });
        }
    });
    """
    try:
        return base64.b64decode(
            e.call_async(code, include_cursor=include_cursor, use_file=None, **kwargs)
        )
    except EvaluatorJavaScriptError as exc:
        if (
            exc.message != "must use filename"
            and "Argument 'filename'" not in exc.message
        ):
            raise
        use_file = str(uuid.uuid4())
        path = e.call_async(code, include_cursor=include_cursor, use_file=use_file)
        with open(path, "rb") as f:
            data = f.read()
        os.unlink(path)
        return data
