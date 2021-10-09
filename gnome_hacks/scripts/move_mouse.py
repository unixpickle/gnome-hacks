from gnome_hacks.evaluator import Evaluator
from gnome_hacks.pointer import PointerButton, PointerMove, simulate_pointer_events

e = Evaluator()
simulate_pointer_events(
    e, PointerMove(10, 10), PointerButton(True), PointerButton(False)
)
