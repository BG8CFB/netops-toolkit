import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from netops_toolkit import __version__


def test_version():
    assert __version__ == "0.4.1"


def test_cli_import():
    from netops_toolkit.cli import main
    assert callable(main)
