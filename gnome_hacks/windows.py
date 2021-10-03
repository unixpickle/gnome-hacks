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
