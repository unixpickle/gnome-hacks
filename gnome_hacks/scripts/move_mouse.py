from gnome_hacks.run_js import Evaluator

e = Evaluator()
# Currently this doesn't seem to work.
# Based on https://github.com/GNOME/mutter/blob/main/src/tests/clutter/performance/test-common.h
code = """
    const Clutter = imports.gi.Clutter;
    const device = Clutter.get_default_backend().get_default_seat().get_pointer();

    const warmup = Clutter.Event.new(Clutter.EventType.CLUTTER_ENTER);
    warmup.set_coords(100,100);
    warmup.set_device(device);
    warmup.set_stage(global.get_stage());
    warmup.put();

    const e = Clutter.Event.new(Clutter.EventType.CLUTTER_MOTION);
    e.set_coords(100,100);
    e.set_device(device);
    e.set_stage(global.get_stage());
    e.put();
"""
print(e(code, raw=True))
