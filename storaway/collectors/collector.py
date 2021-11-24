from abc import abstractmethod
from typing import TYPE_CHECKING, BinaryIO, Type

if TYPE_CHECKING:
    from applications.application import Application


class Collector:

    application: Type["Application"]

    def __init__(self, application: Type["Application"]) -> None:
        self.application = application

    @abstractmethod
    def collect(self, output: BinaryIO) -> None:
        pass
