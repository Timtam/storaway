from typing import IO, Dict, Sequence

from collectors.file_collector import FileCollector
from extractors.file_extractor import FileExtractor
from utils.path import get_appdata
from utils.platform import Platform

from .application import Application


class Thunderbird(Application):

    name = "Thunderbird"
    description = "Mozilla Thunderbird"
    platforms = (Platform.WINDOWS,)

    def prepare_collectors(self) -> Sequence[FileCollector]:
        return [
            self.get_collector(FileCollector, "files", get_appdata() / "Thunderbird")
        ]

    def prepare_extractors(
        self, files: Dict[str, IO[bytes]]
    ) -> Sequence[FileExtractor]:

        return [
            self.get_extractor(
                FileExtractor, files["files"], get_appdata() / "Thunderbird"
            )
        ]
