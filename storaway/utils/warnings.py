from enum import Enum


class Warnings(str, Enum):
    IGNORE = "ignore"
    ASK = "ask"
    ERROR = "error"
