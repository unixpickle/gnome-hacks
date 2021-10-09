from dataclasses import dataclass
from typing import Optional

from .evaluator import Evaluator


@dataclass
class KeyEvent:
    pressed: bool

    # One of these two must be supplied
    keyval: Optional[int] = None  # layout-agnostic key code, see keysyms.py.
    key: Optional[int] = None  # hardware key code


def simulate_key_events(e: Evaluator, *events: KeyEvent):
    code = """
    const Clutter = imports.gi.Clutter;
    const seat = Clutter.get_default_backend().get_default_seat();
    let dtype = Clutter.InputDeviceType.CLUTTER_KEYBOARD_DEVICE;
    if ('undefined' == typeof dtype) {
        // GNOME 3.36
        dtype = Clutter.InputDeviceType.KEYBOARD_DEVICE;
    }
    const dev = seat.create_virtual_device(dtype);
    events.forEach((e) => {
        const state = e.pressed ? Clutter.KeyState.PRESSED : Clutter.KeyState.RELEASED;
        if (e.keyval != null) {
            dev.notify_keyval(0, e.keyval, state);
        } else {
            dev.notify_key(0, e.key, state);
        }
    });
    """
    for evt in events:
        if sum(x is not None for x in [evt.key, evt.keyval]) != 1:
            raise ValueError(
                f"must specify exactly one of keyval or key, but got {evt}"
            )
    e(
        code,
        events=[dict(pressed=x.pressed, key=x.key, keyval=x.keyval) for x in events],
    )
