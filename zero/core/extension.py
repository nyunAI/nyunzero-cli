from zero.core.constants import WorkspaceExtension, DockerRepository, DockerTag, Algorithm
from zero.core.utils import pull_docker_image
from zero.core.models import NyunDocker
from typing import Any, Set, List, Dict, Union
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class DockerMetadata:
    # a class to store extension metadata: Algorithm, NyunDocker, BaseExtension

    def __init__(self, algorithm: Algorithm, docker_image: NyunDocker, extension: WorkspaceExtension):
        self.algorithm = algorithm
        self.docker_image = docker_image
        self.extension_type = extension


class BaseExtension:
    # to be defined on inheritence
    extension_type: Union[WorkspaceExtension, None] = None
    docker_images: Set[NyunDocker] = set()
    algorithm_to_docker: Dict[Algorithm, NyunDocker] = {}


    _all_docker_images: Set[NyunDocker] = set()
    _registry: Set[DockerMetadata] = set()

    def __init__(self):
        self.installed = False
        for image in self.docker_images:
            self._all_docker_images.add(image)
        
        for algorithm, docker_image in self.algorithm_to_docker.items():
            self.register(
                DockerMetadata(
                    algorithm=algorithm,
                    docker_image=docker_image,
                    extension=self.extension_type
                )
            )
    
    def register(self, metadata: DockerMetadata):
        self._registry.add(metadata)

    def install(self):
        if len(self._all_docker_images) == 0:
            raise ValueError(f"No docker images found for {self.extension_type}")

        # parallel pull
        pull_docker_image(*self._all_docker_images)
        
        # or sequencially do img.install() for each image in self._all_docker_images
    
    def uninstall(self):
        print(f"Uninstalling {self.extension_type}")
        # TODO
        # call utils.uninstall
        self.installed = False
    
    def run(self, file_path: Path):
        # find from registry the metadata that has algorithm and then find the corresponding NyunDocker; then for the NyunDocker trigger the .run()
        import yaml
        with open(file_path, "r") as file:
            data = yaml.safe_load(file)
        
        try:
            algorithm = Algorithm(data.get("algorithm"))
        except Exception as e:
            logger.error(e)
            raise Exception from e
        
        docker_image = None
        for metadata in self._registry:
            if metadata.algorithm == algorithm:
                docker_image = metadata.docker_image
                break
        if docker_image is None:
            raise ValueError(f"No docker image found for algorithm: {algorithm}")
        docker_image.run(file_path)


class KompressVisionExtension(BaseExtension):
    extension_type = WorkspaceExtension.VISION
    docker_images = {
        NyunDocker(DockerRepository.NYUN_KOMPRESS, DockerTag.MAIN_KOMPRESS),
        NyunDocker(DockerRepository.NYUN_KOMPRESS, DockerTag.KOMPRESS_MMRAZOR),
    }
    algorithm_to_docker = {

    }



class KompressTextGenerationExtension(BaseExtension):
    extension_type = WorkspaceExtension.TEXT_GENERATION
    docker_images = {
        NyunDocker(DockerRepository.NYUN_KOMPRESS, DockerTag.AWQ),
        NyunDocker(DockerRepository.NYUN_KOMPRESS, DockerTag.FLAP),
        NyunDocker(DockerRepository.NYUN_KOMPRESS, DockerTag.MLCLLM),
        NyunDocker(DockerRepository.NYUN_KOMPRESS, DockerTag.TENSORRTLLM),
        NyunDocker(DockerRepository.NYUN_KOMPRESS, DockerTag.EXLLAMA),
    }

    algorithm_to_docker = {
        Algorithm.AUTOAWQ: NyunDocker(DockerRepository.NYUN_KOMPRESS, DockerTag.AWQ)
    }


class AdaptExtension(BaseExtension):
    extension_type = WorkspaceExtension.ADAPT
    docker_images = {NyunDocker(DockerRepository.NYUN_ADAPT, DockerTag.ADAPT)}
    algorithm_to_docker = {

    }