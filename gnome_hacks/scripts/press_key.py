from gnome_hacks.run_js import Evaluator

import time

e = Evaluator()
code = """
    const Clutter = imports.gi.Clutter;
    const seat = Clutter.get_default_backend().get_default_seat();
    const dev = seat.create_virtual_device(Clutter.InputDeviceType.CLUTTER_KEYBOARD_DEVICE);
    dev.notify_key(0, 51, Clutter.KeyState.PRESSED);
    dev.notify_key(0, 51, Clutter.KeyState.RELEASED);
"""
print(e(code, raw=True))
