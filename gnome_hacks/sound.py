from .evaluator import Evaluator


def bell_notify(e: Evaluator):
    code = """
    const Clutter = imports.gi.Clutter;
    const seat = Clutter.get_default_backend().get_default_seat();
    seat.bell_notify();
    """
    return e(code)


def play_bell_sound(e: Evaluator):
    code = """
    const disp = global.get_display();
    disp.get_sound_player().play_from_theme(
        "bell-window-system",
        "Bell event",
        null,
    );
    """
    return e(code)
