import time

from .evaluator import Evaluator


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
    const Gio = imports.gi.Gio;
    return await new Promise((resolve, reject) => {
        const ss = new Screenshot();
        const output = Gio.MemoryOutputStream.new_resizable()
        ss.screenshot(include_cursor, output, (_, async_result) => {
            try {
                ss.screenshot_finish(async_result);
                output.close(Gio.Cancellable.get_current());
                const data = output.steal_as_bytes();
                const arr = imports.byteArray.fromGBytes(data);
                const result = [];
                for (let i = 0; i < arr.length; i++) {
                    result.push(arr[i]);
                }
                resolve(result);
            } catch (e) {
                reject(e);
            }
        });
    });
    """
    return bytes(e.call_async(code, include_cursor=include_cursor, **kwargs))