import pathlib
import zipfile
from typing import List

import click

from .extractor import Extractor


class FileExtractor(Extractor):

    path: pathlib.Path

    def __init__(self, path: pathlib.Path) -> None:

        super().__init__()

        self.path = path

    def extract(self) -> None:

        if self.path.exists() and not self.application.get_overwrite():
            self.application.report_warning(
                f"The target path already exists: {self.path}", critical=True
            )
            return

        zip = zipfile.ZipFile(self.input, "r")

        self.application.echo("Searching for files...")

        files: List[str] = zip.namelist()

        self.application.echo(f"Found {len(files)} files.")

        with click.progressbar(files) as bar:
            for file in bar:

                dir = self.path / pathlib.Path(file).parent
                dir.mkdir(parents=True, exist_ok=True)

                zip.extract(file, path=dir)

        zip.close()
