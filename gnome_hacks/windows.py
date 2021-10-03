from dataclasses import dataclass
from typing import List, Optional

from .run_js import Evaluator


@dataclass
class WindowInfo:
    title: str
    pid: int
    id: int


@dataclass
class Rect:
    x: int
    y: int
    width: int
    height: int


def list_windows(e: Evaluator) -> List[WindowInfo]:
    code = """
    const actors = global.get_window_actors();
    const result = [];
    for (let i = 0; i < actors.length; i++) {
        const window = actors[i].get_meta_window();
        result.push({
            title: window.get_title(),
            pid: window.get_pid(),
            id: window.get_id(),
        });
    }
    result;
    """
    return [WindowInfo(**x) for x in e(code)]


def get_window_frame(e: Evaluator, id: int) -> Optional[Rect]:
    code = """
    const actors = global.get_window_actors();
    let result = null;
    for (let i = 0; i < actors.length; i++) {
        const window = actors[i].get_meta_window();
        if (window.get_id() == window_id) {
            const f = window.get_frame_rect();
            result = {
                x: f.x,
                y: f.y,
                width: f.width,
                height: f.height,
            };
        }
    }
    result;
    """
    result = e(code, window_id=id)
    return None if result is None else Rect(**result)


def get_window_monitor_frame(e: Evaluator, id: int) -> Optional[Rect]:
    code = """
    const actors = global.get_window_actors();
    let result = null;
    for (let i = 0; i < actors.length; i++) {
        const window = actors[i].get_meta_window();
        if (window.get_id() == window_id) {
            const display = window.get_display();
            const monitor = window.get_monitor();
            const f = display.get_monitor_geometry(monitor);
            result = {
                x: f.x,
                y: f.y,
                width: f.width,
                height: f.height,
            };
        }
    }
    result;
    """
    result = e(code, window_id=id)
    return None if result is None else Rect(**result)


def move_window(e: Evaluator, id: int, x: int, y: int, user_op: bool = False) -> bool:
    code = """
    const actors = global.get_window_actors();
    let result = false;
    for (let i = 0; i < actors.length; i++) {
        const window = actors[i].get_meta_window();
        if (window.get_id() == window_id) {
            window.move_frame(user_op, x, y);
            result = true;
        }
    }
    result;
    """
    return e(code, window_id=id, x=x, y=y, user_op=user_op)
