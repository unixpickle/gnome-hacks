from gnome_hacks.evaluator import Evaluator
from gnome_hacks.screenshot import capture_screenshot

e = Evaluator()
data = capture_screenshot(e)
with open("foo.png", "wb") as f:
    f.write(data)
