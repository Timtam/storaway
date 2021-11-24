from typing import TYPE_CHECKING, Tuple, Type

from .kompletekontrol import KompleteKontrol
from .thunderbird import Thunderbird

if TYPE_CHECKING:
    from .application import Application

applications: Tuple[Type["Application"], ...] = (
    Thunderbird,
    KompleteKontrol,
)
