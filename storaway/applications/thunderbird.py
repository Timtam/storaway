from typing import Sequence

from collectors.file_collector import FileCollector
from utils.path import get_appdata
from utils.platform import Platform

from .application import Application


class Thunderbird(Application):

    name = "Thunderbird"
    description = "Mozilla Thunderbird"
    platforms = (Platform.WINDOWS,)

    def prepare_collectors(self) -> Sequence[FileCollector]:
        return [self.get_collector(FileCollector, get_appdata() / "Thunderbird")]
