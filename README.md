# gnome-hacks

This is a collection of APIs that allow programmatic manipulation of the [GNOME shell](https://en.wikipedia.org/wiki/GNOME_Shell). If you use GNOME (the default graphical shell in Ubuntu), then this allows you to create scripts that move your mouse, simulate key presses, manipulate windows, and more.

**Disclaimer:** Since these hacks hook directly into the internals of the shell, they depend heavily on the particular shell version. I have only tested this on Ubuntu 21.04 with GNOME version 3.38.5.

# Exposed APIs

[Evaluator](gnome_hacks/evaluator.py) - an object that evaluates JavaScript code inside the GNOME shell.
 * `__call__`: run some JavaScript code inside the shell and get the result as a Python object (it is serialized via JSON). Optionally pass extra kwargs to create variables in the JavaScript code's context. For example, `evaluator("hi+3", hi=4)`.
 * `call_async`: similar to `__call__`, but supports JavaScript code that has to wait for callbacks or asynchronous events. In particular, the JavaScript code can use the `await` keyword to yield control to the event loop. Ideal for blocks of code that need to handle callbacks.

[Window manipulation](gnome_hacks/windows.py)
 * `list_windows`: get all open windows, including their title, owning PID, and ID.
 * `get_window_frame`: get the bounding box of a window.
 * `get_window_monitor_frame`: get the bounding box of the monitor containing a window.
 * `move_window`: set the position of a window.

[Screenshots](gnome_hacks/screenshot.py)
 * `capture_screenshot`: get a screenshot of the display as PNG `bytes`. On newer versions of GNOME, this happens entirely in memory without ever writing a temporary file.

[Keyboard](gnome_hacks/keyboard.py)
 * `simulate_key_events`: trigger a series of key events, allowing a script to type text, trigger keystrokes, etc.

[Pointer](gnome_hacks/pointer.py)
 * `simulate_pointer_events`: trigger a series of mouse events, allowing a script to move, click, and drag the cursor using absolute coordinates on the screen.

[Sound](gnome_hacks/sound.py)
 * `play_bell_sound`: play the bell sound that apps use to signal errors or get a user's attention.
 * `bell_notify`: similar to `play_bell_sound`, but may also flash the screen or use other feedback if the user has configured the shell to do so.

# How it works

The GNOME shell provides a [DBus](https://en.wikipedia.org/wiki/D-Bus) interface, allowing other processes to connect to it and make IPC calls. Through this interface, it exposes an `Eval` method for evaluating JavaScript inside an embedded interpreter. This JavaScript code has access to most of the types and functions used by the shell, exposed through [GJS bindings](https://gitlab.gnome.org/GNOME/gjs).

The shell exposes a `global` object which [has methods](https://github.com/GNOME/gnome-shell/blob/4e5ddc5459adbee87be2519c1e199b3b526adc0e/src/shell-global.h#L18-L22) to access various shell state, such as the list of open windows or the global [MetaDisplay](https://github.com/GNOME/mutter/blob/867db93043dd3c93d8ccb6cb197d4a3687d3a5e5/src/meta/display.h#L88-L313) object.
