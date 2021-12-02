from abc import abstractmethod
from typing import IO, TYPE_CHECKING, Any

if TYPE_CHECKING:
    from applications.application import Application


class Collector:

    application: "Application"
    name: str

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        pass

    @abstractmethod
    def collect(self, output: IO[bytes]) -> None:
        pass
