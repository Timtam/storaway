import click
import tabulate

from applications import applications


@click.command(name="list", help="lists all applications supported")
def ListCommand() -> None:

    click.echo_via_pager(
        tabulate.tabulate(
            [
                [app.name.lower(), app.description]
                for app in sorted(applications, key=lambda a: a.name)
            ],
            headers=(
                "application",
                "description",
            ),
        )
    )
