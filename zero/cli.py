import typer
from pathlib import Path
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
    workspace: Path = typer.Argument(
        None,
        help="Path to the workspace directory. If not provided, the current working directory will be used.",
    ),
    custom_data: Path = typer.Argument(
        None,
        help='Path to the custom data directory. If not provided, a default directory ("custom_data") will be created within the workspace.',
    ),
    overwrite: bool = typer.Option(
        False,
        "--overwrite",
        "-o",
        help="Overwrite the existing workspace spec if it already exists.",
    ),
    extensions: WorkspaceExtension = typer.Option(
        WorkspaceExtension.ALL,
        "--extensions",
        "-e",
        help="Specify the extensions to install. Defaults to installing all available extensions. Available extensions are: kompress-vision, kompress-text-generation, adapt, all, none.",
    ),
):
    """
    Initialize the Nyun workspace and custom data directory.

    This command initializes the Nyun workspace and custom data directory.
    You can provide the path to the workspace directory and the custom data directory.
    If not provided, default paths will be used.
    Additionally, you can specify whether to overwrite the existing workspace spec and which extensions to install.
    """
    workspace_path, custom_data_path, _ = get_workspace_and_custom_data_paths(
        workspace, custom_data
    )

    # Resolve absolute paths
    workspace_path = (
        workspace_path.resolve()
        if workspace_path.is_absolute()
        else Path.cwd() / workspace_path
    )
    custom_data_path = (
        custom_data_path.resolve()
        if custom_data_path.is_absolute()
        else workspace_path / custom_data_path
    )

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


@app.command(help="Run scripts within the initialized Nyun workspace.")
def run(
    file_path: Path = typer.Argument(
        None, help="Path to the YAML or JSON script file you want to run."
    )
):
    """
    Run scripts within the initialized Nyun workspace.

    This command allows you to run scripts within the initialized Nyun workspace.
    You need to provide the path to the YAML or JSON script file you want to run.
    The script will be executed within the initialized workspace.
    """
    if file_path.suffix in SUPPORTED_SUFFIX:
        # Get workspace paths and extensions
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
            # Initialize progress bar
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


@app.command(help="Show the version of the Nyun CLI.")
def version():
    """
    Show the version of the Nyun CLI.

    This command displays the version of the Nyun CLI currently installed on your system.
    """
    version_string = NYUN_TRADEMARK.format(version=__version__)
    typer.echo(version_string)
