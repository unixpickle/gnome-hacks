from dataclasses import dataclass
from typing import Any, Dict, Tuple, Union

from .evaluator import Evaluator


@dataclass
class PointerMove:
    x: Union[int, float]
    y: Union[int, float]

    def encode_pointer_event(self) -> Dict[str, Any]:
        return dict(move=(self.x, self.y))


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

    const waitPromise = () => {
        return new Promise((resolve, reject) => {
            GLib.timeout_add(GLib.PRIORITY_DEFAULT, 100, () => resolve(null));
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
            seat.warp_pointer(e.move.x, e.move.y);

            // For some reason we can't click right after
            // calling warp_pointer.
            await waitPromise();

            // For some reason this sends the pointer to (0,0) and
            // breaks the trackpad until the next warp_pointer().
            // The touchscreen still works though.
            // dev.notify_absolute_motion(0, e.move.x, e.move.y);
        }
    }
    """
    num_moves = sum(isinstance(x, PointerMove) for x in events)
    delay = 2000 + 100 * num_moves
    e.call_async(
        code, timeout_ms=2000 + delay, events=[x.encode_pointer_event() for x in events]
    )
