import platform


from .base_os import BaseOS
from .windows.windows import Windows


def get_os() -> BaseOS:
    """
    Return the OS used by the device
    """
    if platform.system() == "Windows":
        return Windows()
    raise OSError("Unknown Operating System!")
