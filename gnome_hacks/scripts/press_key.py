from gnome_hacks.evaluator import Evaluator
from gnome_hacks.keyboard import KeyEvent, simulate_key_events
from gnome_hacks.keysyms import KeyVal

e = Evaluator()
simulate_key_events(
    e,
    KeyEvent(pressed=True, keyval=KeyVal.KEY_H),
    KeyEvent(pressed=False, keyval=KeyVal.KEY_H),
    KeyEvent(pressed=True, keyval=KeyVal.KEY_i),
    KeyEvent(pressed=False, keyval=KeyVal.KEY_i),
    KeyEvent(pressed=True, keyval=KeyVal.KEY_Return),
    KeyEvent(pressed=False, keyval=KeyVal.KEY_Return),
)
