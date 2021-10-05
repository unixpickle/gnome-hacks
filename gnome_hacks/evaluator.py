import json
from typing import Any

from gi.repository import GLib, GObject, Gio


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

    def __call__(self, script: str, raw=False, timeout_ms=1000, **kwargs) -> Any:
        """
        Evaluate JavaScript code inside the GNOME shell.

        :param script: JavaScript code to execute.
        :param raw: if True, don't attempt to parse the output as JSON.
        :param timeout_ms: the timeout for the DBus call.;
        :param kwargs: extra variables to pass to the script. These must be
                       JSON serializable.
        """
        vars = ";".join(
            f"var {name}={json.dumps(value)}" for name, value in kwargs.items()
        )
        if len(kwargs):
            vars += ";"
        wrapped_script = vars + script
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


class EvaluatorJavaScriptError(Exception):
    """
    An error thrown when GNOME's JavaScript engine fails to execute a script.
    """

    pass
