import pathlib

import winpath


def get_local_appdata() -> pathlib.Path:
    return pathlib.Path(winpath.get_local_appdata())


def get_appdata() -> pathlib.Path:
    return pathlib.Path(winpath.get_appdata())


def get_common_appdata() -> pathlib.Path:
    return pathlib.Path(winpath.get_common_appdata())


def get_common_documents() -> pathlib.Path:
    return pathlib.Path(winpath.get_common_documents())


def get_windows() -> pathlib.Path:
    return pathlib.Path(winpath.get_windows())


def get_system() -> pathlib.Path:
    return pathlib.Path(winpath.get_system())


def get_program_files() -> pathlib.Path:
    return pathlib.Path(winpath.get_program_files())


def get_my_documents() -> pathlib.Path:
    return pathlib.Path(winpath.get_my_documents())


def get_my_pictures() -> pathlib.Path:
    return pathlib.Path(winpath.get_my_pictures())
