from gnome_hacks.evaluator import Evaluator
from gnome_hacks.windows import list_windows

if __name__ == "__main__":
    print("\n".join(map(str, list_windows(Evaluator()))))
