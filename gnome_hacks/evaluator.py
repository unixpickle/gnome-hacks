import json
import random
import time
from typing import Any

from gi.repository import Gio, GLib, GObject


class Evaluator(GObject.Object):
    """
    A connection to the GNOME shell for evaluating scripts.
    """

    def __init__(self):
        super().__init__()
        self.proxy = Gio.DBusProxy.new_for_bus_sync(
            Gio.BusType.SESSION,
            Gio.DBusProxyFlags.NONE,
            None,
            "org.gnome.Shell",
            "/org/gnome/Shell",
            "org.gnome.Shell",
        )

    def __call__(self, script: str, raw=False, timeout_ms: int = 1000, **kwargs) -> Any:
        """
        Evaluate JavaScript code inside the GNOME shell.

        :param script: JavaScript code to execute.
        :param raw: if True, don't attempt to parse the output as JSON.
        :param timeout_ms: the timeout for the DBus call.;
        :param kwargs: extra variables to pass to the script. These must be
                       JSON serializable.
        """
        wrapped_script = _add_variables(script, **kwargs)
        status, result = self.proxy.call_sync(
            "Eval",
            GLib.Variant.new_tuple(GLib.Variant.new_string(wrapped_script)),
            Gio.DBusCallFlags.NO_AUTO_START,
            timeout_ms,
        ).unpack()
        if not status:
            raise EvaluatorJavaScriptError(result)
        if raw:
            return result
        elif not result:
            return None
        return json.loads(result)

    def call_async(
        self, script: str, timeout_ms: int = 2000, poll_interval: int = 50, **kwargs
    ) -> Any:
        """
        Evaluate code inside an async function and wait for the results.
        """
        wait_name = f"_waitCtx{random.randrange(2**40)}"
        wrapped_script = _add_variables(script, **kwargs)
        code = (
            "const _waitCtx = {status: 0};"
            "global[_waitName] = _waitCtx;"
            "(async function(){" + wrapped_script + "})().then((result)=>{"
            "_waitCtx.result=result; _waitCtx.status=1;}).catch((err)=>{"
            "_waitCtx.error=''+err; _waitCtx.status=2;});"
            """
            // Cleanup global object if the call times out.
            const GLib = imports.gi.GLib;
            GLib.timeout_add(GLib.PRIORITY_DEFAULT, _waitTimeout, () => {
                if (global[_waitName]) {
                    delete global[_waitName];
                }
                return false;
            });
            """
        )
        self(
            code,
            timeout_ms=timeout_ms,
            _waitName=wait_name,
            _waitTimeout=timeout_ms + 1000,  # buffer time before cleanup
        )
        t1 = time.time()
        while time.time() < t1 + timeout_ms / 1000:
            check_code = """
            const res = global[_waitName];
            if (res.status) {
                delete global[_waitName];
            }
            res;
            """
            out = self(check_code, _waitName=wait_name)
            if out["status"] == 1:
                return out["result"]
            elif out["status"] == 2:
                raise EvaluatorJavaScriptError(out["error"])
            time.sleep(poll_interval / 1000)
        raise EvaluatorPromiseTimeoutError("result was not received in time")


def _add_variables(script: str, **kwargs):
    vars = ";".join(f"var {name}={json.dumps(value)}" for name, value in kwargs.items())
    if len(kwargs):
        vars += ";"
    return vars + script


class EvaluatorJavaScriptError(Exception):
    """
    An error thrown when GNOME's JavaScript engine fails to execute a script.
    """

    def __init__(self, msg: str):
        super().__init__(msg)
        self.message = msg


class EvaluatorPromiseTimeoutError(Exception):
    """
    An error thrown when a Promise evaluation times out.
    """

    pass
