from dataclasses import dataclass
from typing import List

from .run_js import Evaluator


@dataclass
class WindowInfo:
    title: str
    pid: int
    id: int


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
