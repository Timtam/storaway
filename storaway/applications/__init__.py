from typing import TYPE_CHECKING, Tuple, Type

from .kompletekontrol import KompleteKontrol
from .kontakt import Kontakt
from .spitfireaudio import SpitfireAudio
from .thunderbird import Thunderbird

if TYPE_CHECKING:
    from .application import Application

applications: Tuple[Type["Application"], ...] = (
    KompleteKontrol,
    Kontakt,
    SpitfireAudio,
    Thunderbird,
)
