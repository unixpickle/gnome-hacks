from .evaluator import Evaluator


def move_pointer(e: Evaluator, x: int, y: int):
    code = """
    const Clutter = imports.gi.Clutter;
    Clutter.get_default_backend().get_default_seat().warp_pointer(x, y);
    """
    e(code, x=x, y=y)


def click_pointer(e: Evaluator, button: int):
    code = """
    const Clutter = imports.gi.Clutter;
    const seat = Clutter.get_default_backend().get_default_seat();
    const dev = seat.create_virtual_device(Clutter.InputDeviceType.CLUTTER_POINTER_DEVICE);
    dev.notify_button(0, button, Clutter.ButtonState.PRESSED);
    dev.notify_button(0, button, Clutter.ButtonState.RELEASED);
    """
    e(code, button=button)
