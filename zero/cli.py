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

from docker.models.containers import ExecResult, Container
from rich.progress import Progress, SpinnerColumn, TextColumn


SUPPORTED_SUFFIX = {".yaml", ".yml", ".json"}

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
def run(file_path: Path = typer.Argument(None, help="Path to yaml file.")):
    """Run the specified file."""
    if file_path.suffix in SUPPORTED_SUFFIX:
        workspace_path, custom_data_path, extensions = (
            get_workspace_and_custom_data_paths(None, None)
        )
        try:
            workspace = Workspace(
                workspace_path=workspace_path,
                custom_data_path=custom_data_path,
                overwrite=False,
                extensions=extensions[0],
            )
        except:
            typer.echo("Workspace not initialized. Use `nyun init`.")
            raise typer.Abort()
        ext_obj = workspace.init_extension()
        try:
            progress = Progress(
                SpinnerColumn(spinner_name="dots8", speed=2),
                TextColumn("[progress.description]{task.description}"),
                transient=False,
            )
            with progress:
                task = progress.add_task(
                    f"[white](Nyun) Running script {file_path}...",
                    total=1,
                    start=False,
                )
                running_container: Container = ext_obj.run(
                    file_path=file_path, workspace=workspace
                )
                running_container.wait()
                # TODO: add checks on container if success or failed. use container.exec_run if needed
                progress.update(
                    task,
                    advance=1,
                    description=f"[blue]Done.",
                    completed=True,
                    refresh=True,
                )
        except Exception as e:
            print(e)
            raise Exception from e
    else:
        typer.echo("File must be a .yaml or .json file")


@app.command()
def version():
    """Show the version of the CLI."""
    version_string = NYUN_TRADEMARK.format(version=__version__)
    typer.echo(version_string)
