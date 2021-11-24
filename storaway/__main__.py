import click

from commands.backup_command import BackupCommand
from commands.list_command import ListCommand


@click.group(
    help="This application let's you create backups of several system tools and transfer the data over to a new system, sometimes even being able to bridge platform gaps while at it."
)
def main() -> None:
    pass


main.add_command(BackupCommand)
main.add_command(ListCommand)

if __name__ == "__main__":
    main()
