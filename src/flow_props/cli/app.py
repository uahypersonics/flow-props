"""CLI app for flow-props."""

from __future__ import annotations

from importlib.metadata import version as _pkg_version

import typer

from flow_props.cli.cmd_examples import cmd_examples
from flow_props.cli.cmd_init import cmd_init
from flow_props.cli.cmd_run import cmd_run

__version__ = _pkg_version("flow-props")


def _version_callback(value: bool) -> None:
    """Print version and exit."""
    if value:
        typer.echo(f"flow-props {__version__}")
        raise typer.Exit()


app = typer.Typer(
    name="flow-props",
    help="Extract boundary-layer properties from CFD data.",
    no_args_is_help=True,
    add_completion=False,
)


@app.callback()
def _main(
    version: bool = typer.Option(
        False,
        "--version",
        "-V",
        callback=_version_callback,
        is_eager=True,
        help="Show version and exit.",
    ),
) -> None:
    """flow-props: boundary-layer and entropy-layer extraction from CFD data."""
    del version


app.command("init")(cmd_init)
app.command("run")(cmd_run)
app.command("examples")(cmd_examples)
