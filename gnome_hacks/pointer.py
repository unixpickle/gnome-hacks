from dataclasses import dataclass
from typing import Any, Dict, Tuple, Union

from .evaluator import Evaluator


@dataclass
class PointerMove:
    x: Union[int, float]
    y: Union[int, float]
    delay_ms: int = 100

    def encode_pointer_event(self) -> Dict[str, Any]:
        return dict(move=dict(x=self.x, y=self.y, delay_ms=self.delay_ms))


@dataclass
class PointerButton:
    pressed: bool
    button: int = 1

    def encode_pointer_event(self) -> Dict[str, Any]:
        return dict(button=dict(pressed=self.pressed, button=self.button))


def simulate_pointer_events(e: Evaluator, *events: Union[PointerMove, PointerButton]):
    code = """
    const Clutter = imports.gi.Clutter;
    const GLib = imports.gi.GLib;

    const seat = Clutter.get_default_backend().get_default_seat();
    const dev = seat.create_virtual_device(Clutter.InputDeviceType.CLUTTER_POINTER_DEVICE);

    const waitPromise = (ms) => {
        return new Promise((resolve, reject) => {
            GLib.timeout_add(GLib.PRIORITY_DEFAULT, ms, () => resolve(null));
        });
    };

    for (let i = 0; i < events.length; i++) {
        const e = events[i];
        if (e.button) {
            dev.notify_button(
                0,
                e.button.button,
                e.button.pressed ? Clutter.ButtonState.PRESSED : Clutter.ButtonState.RELEASED,
            );
        } else if (e.move) {
            dev.notify_absolute_motion(0, e.move.x, e.move.y);

            // For some reason, some click events don't work if they are
            // directly after a mouse movement, so mouse movements can have
            // a delay before them.
            await waitPromise(e.move.delay_ms);
        }
    }
    """
    total_delay = sum(x.delay_ms if isinstance(x, PointerMove) else 0 for x in events)
    delay = 2000 + total_delay
    e.call_async(
        code, timeout_ms=2000 + delay, events=[x.encode_pointer_event() for x in events]
    )
