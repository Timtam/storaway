import textwrap
from typing import IO, TYPE_CHECKING, List, Literal, Type, Union

import click

from applications import applications
from utils.platform import get_current_platform
from utils.warnings import Warnings

if TYPE_CHECKING:
    from applications.application import Application


@click.command(
    name="restore",
    help="Restore a backup of a given application. The backup must have been created using the backup command. The APPLICATION argument defines the application which you want to restore. See the list command for a list of all supported applications. The FILE argument defines the backup archive which you want to restore.",
    no_args_is_help=True,
)
@click.argument(
    "application",
)
@click.argument(
    "file",
    type=click.File("rb"),
)
@click.option(
    "-w",
    "--warnings",
    type=click.Choice(["ignore", "ask", "error"], case_sensitive=False),
    default="ignore",
    help="what should be done with warnings. Ignore (default) means that warnings are shown, but will not interfere with the backup process. Ask will show an interactive question, allowing you to interactively abort the process. Error will abort the backup process as soon as a warning is encountered.",
)
def RestoreCommand(
    application: str,
    file: IO[bytes],
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

    app: "Application" = found_apps[0]()

    if not get_current_platform() in app.platforms:
        click.echo(f"Storaway doesn't support {app.name} on this platform yet.")
        return

    app.set_warnings_level(Warnings(warnings))
