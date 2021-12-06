from dataclasses import dataclass
from typing import Dict

from utils.platform import Platform


@dataclass(init=False)
class ApplicationMetadata:
    collectors_map: Dict[str, int]
    platform: Platform
    storaway_version: str
