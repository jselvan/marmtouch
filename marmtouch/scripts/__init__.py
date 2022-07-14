import click

from marmtouch import __version__
from marmtouch.scripts.launcher import launch
from marmtouch.scripts.make_shortcut import make_shortcut
from marmtouch.scripts.run import run
from marmtouch.scripts.transfer_files import transfer_files


@click.group()
def marmtouch():
    print(f"marmtouch version {__version__}")


marmtouch.add_command(run)
marmtouch.add_command(make_shortcut)
marmtouch.add_command(transfer_files)
marmtouch.add_command(launch)

if __name__ == "__main__":
    marmtouch()
