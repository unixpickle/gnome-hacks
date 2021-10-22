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


def play_sound(e: Evaluator, path: str, description: str = ""):
    code = """
    const Gio = imports.gi.Gio;
    const disp = global.get_display();
    const file = Gio.File.new_for_path(path);
    disp.get_sound_player().play_from_file(
        file,
        description,
        null,
    );
    """
    return e(code, path=path, description=description)
