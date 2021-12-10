import platform
from enum import IntEnum, auto

import lib_platform


class Platform(IntEnum):
    WINDOWS = auto()
    LINUX = auto()
    DARWIN = auto()
    UNKNOWN = auto()


def get_current_platform() -> Platform:
    if lib_platform.is_platform_windows:
        return Platform.WINDOWS
    elif lib_platform.is_platform_linux:
        return Platform.LINUX
    elif lib_platform.is_platform_darwin:
        return Platform.DARWIN
    else:
        return Platform.UNKNOWN


def is_64bit() -> bool:
    return platform.machine().endswith("64")


def is_32bit() -> bool:
    return not is_64bit()
