from gnome_hacks.evaluator import Evaluator
from gnome_hacks.windows import get_window_frame, list_windows

if __name__ == "__main__":
    e = Evaluator()
    for w in list_windows(e):
        print(w, get_window_frame(e, w.id))
