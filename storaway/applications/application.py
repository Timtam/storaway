from typing import TYPE_CHECKING, Tuple

if TYPE_CHECKING:
    from utils.platform import Platform


class Application:

    name: str
    description: str
    platforms: Tuple["Platform", ...]
