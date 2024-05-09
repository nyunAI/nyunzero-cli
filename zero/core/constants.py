from enum import StrEnum
from pathlib import Path
from typing import Union, Dict


# ==============================================================
#                       Logging Messages
# ==============================================================


# Workspace messages
class WorkspaceMessage(StrEnum):

    # error
    WORKSPACE_PATH_DOES_NOT_EXIST = "Workspace path does not exist: {}"

    # info
    WORKSPACE_SPEC_FOUND = "Workspace spec found."
    CREATED_NEW_WORKSPACE = "Creating a new workspace spec."

    CUSTOM_DATA_PATH_ALREADY_EXISTS = "A custom data path already exists. Existing path: {current_path}. Given path: {given_path}."
    CUSTOM_DATA_PATH_UPDATED = (
        "Custom data path updated, from: {from_path} to: {to_path} in workspace spec."
    )

    EXTENSION_ALREADY_EXISTS = "A different extension set already exists. Existing extension(s): {current_extensions}. Given extension(s): {given_extensions}."
    EXTENSION_UPDATED = "Extension(s) updated, from: {from_extensions} to {to_extensions} in workspace spec."

    WORKSPACE_INITIALIZED = "Workspace initialized."

# Workspace extension
class WorkspaceExtension(StrEnum):

    VISION = "kompress-vision"
    TEXT_GENERATION = "kompress-text-generation"
    ADAPT = "adapt"

    ALL = "all"
    NONE = "none"

    @staticmethod
    def get_extensions_list(
        extension: Union["WorkspaceExtension", Dict["WorkspaceExtension", str]]
    ):
        if isinstance(extension, Dict):
            extension = {
                WorkspaceExtension(key): value for key, value in extension.items()
            }
            retlist = [ext for ext, value in extension.items() if value == "True"]
            return retlist
        elif extension == WorkspaceExtension.ALL:
            return [
                WorkspaceExtension.VISION,
                WorkspaceExtension.TEXT_GENERATION,
                WorkspaceExtension.ADAPT,
            ]
        else:
            return [extension]

    @staticmethod
    def get_extensions_dict(
        *extension: "WorkspaceExtension",
    ) -> Dict["WorkspaceExtension", str]:
        if any(WorkspaceExtension(ext) == WorkspaceExtension.ALL for ext in extension):
            return {
                WorkspaceExtension.VISION: "True",
                WorkspaceExtension.TEXT_GENERATION: "True",
                WorkspaceExtension.ADAPT: "True",
            }
        elif any(
            WorkspaceExtension(ext) == WorkspaceExtension.NONE for ext in extension
        ):
            return {
                WorkspaceExtension.VISION: "False",
                WorkspaceExtension.TEXT_GENERATION: "False",
                WorkspaceExtension.ADAPT: "False",
            }
        else:
            # iteratively carry ahead the dictionary and update the extension
            _extensions = WorkspaceExtension.get_extensions_dict(
                WorkspaceExtension.NONE
            )
            for ext in extension:
                _extensions.update({WorkspaceExtension(ext): "True"})
            return _extensions

    @staticmethod
    def is_extension_different(
        extension: Dict["WorkspaceExtension", str],
        other_extension: Dict["WorkspaceExtension", str],
    ):

        # cast keys to WorkspaceExtension and values to bool
        extension = {WorkspaceExtension(key): value for key, value in extension.items()}
        other_extension = {
            WorkspaceExtension(key): value for key, value in other_extension.items()
        }
        return extension != other_extension


# Workspace spec
class WorkspaceSpec(StrEnum):
    # key constants
    WORKSPACE = "Workspace"
    CUSTOM_DATA = "CustomData"
    LOGS = "Logs"
    EXTENSIONS = "Extensions"

    PATH = "path"

    # path constants
    NYUN = ".nyunservices"
    WORKSPACE_SPEC = "workspace.spec"
    LOG_FILE = "zero.log"

    @staticmethod
    def get_workspace_spec_path(workspace_path: Path):
        return workspace_path / WorkspaceSpec.NYUN / WorkspaceSpec.WORKSPACE_SPEC

    @staticmethod
    def get_workspace_spec_dir(workspace_path: Path):
        return workspace_path / WorkspaceSpec.NYUN

    @staticmethod
    def get_log_file_path(workspace_path: Path):
        return workspace_path / WorkspaceSpec.NYUN / WorkspaceSpec.LOG_FILE


# Docker

class DockerRepository(StrEnum):
    # kompress
    NYUN_KOMPRESS = "nyunadmin/nyun_kompress"

    # adapt
    NYUN_ADAPT = "nyunadmin/adapt"

class DockerTag(StrEnum):
    # kompress vision
    MAIN_KOMPRESS = "main_kompress"
    KOMPRESS_MMRAZOR = "mmrazor"

    # kompress text generation
    FLAP = "flap"
    MLCLLM = "mlcllm"
    TENSORRTLLM = "tensorrtllm"
    EXLLAMA = "exllama"
    AWQ = "autoawq"

    # adapt
    ADAPT = "february"

class Algorithm(StrEnum):
    AUTOAWQ = "AutoAWQ"