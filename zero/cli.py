import os
import typer
from pathlib import Path
from typing import Union, AnyStr, List
from zero.version import __version__
from zero.docs import NYUN_TRADEMARK

from zero.core.workspace import (
    Workspace,
    WorkspaceExtension,
    get_workspace_and_custom_data_paths,
)

SUPPORTED_SUFFIX = {".yaml", ".json"}

app = typer.Typer()


@app.command()
def init(
    workspace: Path = typer.Argument(None, help="Path to the workspace directory"),
    custom_data: Path = typer.Argument(None, help="Path to the custom data directory"),
    overwrite: bool = typer.Option(
        False, "--overwrite", "-o", help="Overwrite the existing workspace spec"
    ),
    extensions: WorkspaceExtension = typer.Option(
        WorkspaceExtension.ALL,
        "--extensions",
        "-e",
        help="Extensions to install",
    ),
):
    """Initialize the workspace and custom data directory."""

    workspace_path, custom_data_path, _ = get_workspace_and_custom_data_paths(
        workspace, custom_data
    )

    if workspace_path.is_absolute():
        workspace_path = workspace_path.resolve()
    else:
        workspace_path = Path.cwd() / workspace_path

    if custom_data_path.is_absolute():
        custom_data_path = custom_data_path.resolve()
    else:
        custom_data_path = workspace_path / custom_data_path

    # typer.echo(f"Workspace: {workspace_path}")
    # typer.echo(f"Custom Data: {custom_data_path}")
    # typer.echo(f"Extensions: {extensions}")
    # typer.echo(f"Overwrite: {overwrite}")

    try:
        workspace = Workspace(
            workspace_path=workspace_path,
            custom_data_path=custom_data_path,
            extensions=extensions,
            overwrite=overwrite,
        )
        workspace.init_extension()
        typer.echo(f"Initialized workspace.")
    except ValueError as e:
        typer.echo(e)
        raise typer.Abort()


@app.command()
def run(file_path: Path):
    """Run the specified file."""
    if file_path.suffix in SUPPORTED_SUFFIX:
        workspace_path, custom_data_path, extensions = (
            get_workspace_and_custom_data_paths(None, None)
        )
        workspace = Workspace(
            workspace_path=workspace_path,
            custom_data_path=custom_data_path,
            overwrite=False,
            extensions=extensions,
        )
        workspace.init_extension()
        typer.echo(f"Running file: {file_path}")
        typer.echo(f"{workspace}")
        # Perform the file processing logic here
    else:
        typer.echo("File must be a .yaml or .json file")


# add --version or -V option to the CLI
@app.command()
def version():
    """Show the version of the CLI."""
    version_string = NYUN_TRADEMARK.format(version=__version__)
    typer.echo(version_string)
