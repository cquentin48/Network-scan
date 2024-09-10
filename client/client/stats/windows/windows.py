import sys

import dataclasses

from stats.base_os import BaseOS


@dataclasses.dataclass
class Windows(BaseOS):
    def __init__(self) -> None:
        pass

    def __str__(self) -> str:
        return "Windows 11" if sys.getwindowsversion() >= 22000 else "Windows 10"
