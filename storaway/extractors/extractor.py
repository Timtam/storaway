from typing import IO, TYPE_CHECKING, Any

if TYPE_CHECKING:
    from applications.application import Application


class Extractor:

    application: "Application"
    input: IO[bytes]

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        pass

    def extract(self) -> None:
        pass
