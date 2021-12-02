import pathlib
import zipfile
from typing import Any, List

import click

from .extractor import Extractor


class FileExtractor(Extractor):

    path: pathlib.Path

    def __init__(self, path: pathlib.Path, *args: Any, **kwargs: Any) -> None:

        self.path = path

    def extract(self) -> None:

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
