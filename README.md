# Nyun CLI

Nyun CLI is a command-line interface tool that provides a convenient way to initialize and manage your Nyun workspace, as well as run various scripts and algorithms supported by Nyun.

## Installation

To install Nyun CLI, you need to have Python 3.6 or later installed on your system. You can then install the CLI tool using pip:

```shell
pip install nyun-cli
```

## Usage

After installation, you can use the `nyun` command to access the available commands. Run `nyun --help` to see the list of available commands and their descriptions.

### Initializing the Workspace

Before you can run any scripts or algorithms, you need to initialize your Nyun workspace. You can do this using the `init` command:

```shell
nyun init [WORKSPACE_PATH] [CUSTOM_DATA_PATH] [OPTIONS]
```

- `WORKSPACE_PATH`: The path to the workspace directory. If not provided, the current working directory will be used.
- `CUSTOM_DATA_PATH`: The path to the custom data directory. If not provided, a default directory will be created within the workspace.
- `OPTIONS`:
  - `--overwrite`, `-o`: Overwrite the existing workspace spec if it already exists.
  - `--extensions`, `-e`: Specify the extensions to install. Defaults to installing all available extensions. Available extensions are:
    - `kompress-vision`: For vision-related tasks (e.g., object detection, image classification), using Nyun Kompress.
    - `kompress-text-generation`: For text generation tasks using Nyun Kompress.
    - `adapt`: For the Adapt framework, which supports various tasks like detection, segmentation, and text generation.
    - `all`: Install all available extensions.
    - `none`: Don't install any extension.

Example:

```shell
# mkdir ~/my-workspace
nyun init ~/my-workspace ~/my-data --extensions kompress-vision
```

This command initializes a new workspace at `~/my-workspace` and sets the custom data directory to `~/my-data`, installing the Nyun Kompress Vision extension.

### Running Scripts

Once your workspace is initialized, you can run scripts using the `run` command in the workspace directory. The command syntax is as follows:

```shell
nyun run [SCRIPT_PATH]
```

- `SCRIPT_PATH`: The path to the YAML or JSON script file you want to run.

Example:

```shell
nyun run ~/my-script.yaml
```

This command runs the script located at `~/my-script.yaml` within your initialized workspace.

### Checking Version

To check the version of the Nyun CLI you have installed, use the `version` command:

```shell
nyun version
```

<!-- ## Contributing

If you'd like to contribute to the Nyun CLI project, please follow the standard GitHub workflow:

1. Fork the repository
2. Create a new branch for your feature or bug fix
3. Make your changes and commit them with descriptive commit messages
4. Push your changes to your forked repository
5. Create a pull request against the main repository

We welcome all contributions, whether they are bug fixes, feature requests, or documentation improvements. -->

<!-- ## License

The Nyun CLI is released under the [MIT License](LICENSE). -->