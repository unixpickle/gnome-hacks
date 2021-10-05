from gnome_hacks.evaluator import Evaluator

e = Evaluator()
# Currently this doesn't seem to work.
# Based on https://github.com/GNOME/mutter/blob/main/src/tests/clutter/performance/test-common.h
code = """
    const Clutter = imports.gi.Clutter;
    Clutter.get_default_backend().get_default_seat().warp_pointer(400, 400);
"""
print(e(code, raw=True))
