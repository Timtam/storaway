import pathlib
import textwrap
from typing import IO, TYPE_CHECKING, List, Literal, Optional, Type, Union

import click

from applications import applications
from utils.platform import get_current_platform
from utils.warnings import Warnings

if TYPE_CHECKING:
    from applications.application import Application


@click.command(
    name="backup",
    help="Create a backup of a given application. The APPLICATION argument defines the application from which to save the configuration. See the list command for a list of all supported applications.",
    no_args_is_help=True,
)
@click.argument(
    "application",
)
@click.option("-o", "--output", type=click.File("wb"), help="output file", default=None)
@click.option(
    "-w",
    "--warnings",
    type=click.Choice(["ignore", "ask", "error"], case_sensitive=False),
    default="ignore",
    help="what should be done with warnings. Ignore (default) means that warnings are shown, but will not interfere with the backup process. Ask will show an interactive question, allowing you to interactively abort the process. Error will abort the backup process as soon as a warning is encountered.",
)
def BackupCommand(
    application: str,
    output: Optional[IO[bytes]],
    warnings: Union[Literal["ignore"], Literal["ask"], Literal["error"]],
) -> None:

    found_apps: List[Type["Application"]] = list(
        filter(lambda app: app.name.lower() == application.lower(), applications)
    )

    if len(found_apps) == 0:
        click.echo(
            textwrap.fill(
                f"application {application} not supported, see the list command for a list of all supported applications."
            ),
            err=True,
        )
        return

    app: Application = found_apps[0]()

    if not get_current_platform() in app.platforms:
        click.echo(f"Storaway doesn't support {app.name} on this platform yet.")
        return

    app.set_warnings_level(Warnings(warnings))

    if not output:
        with (pathlib.Path("./").resolve() / app.get_backup_file_name()).open(
            "wb"
        ) as output:
            app.backup(output)
    else:
        app.backup(output)
