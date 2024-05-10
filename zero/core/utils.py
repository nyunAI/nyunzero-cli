"""
This module provides utility functions for managing Docker containers and images.
It includes functions for pulling Docker images, starting containers, running containers,
and removing containers.
"""

from typing import Union
from logging import getLogger
import os
import docker
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed
from rich.progress import Progress, SpinnerColumn, TextColumn
from docker.models.containers import Container, ExecResult
from zero.core.constants import DockerPath, DockerCommand
from docker.types import Mount, DeviceRequest
from pathlib import Path


logger = getLogger(__name__)


def get_docker_client() -> docker.DockerClient:
    """
    Get a Docker client instance authenticated with the provided credentials.

    Returns:
        docker.DockerClient: A Docker client instance.
    """
    load_dotenv()

    client = docker.from_env()
    client.login(
        username=os.getenv("DOCKER_USERNAME"), password=os.getenv("DOCKER_ACCESS_TOKEN")
    )
    return client


def pull_docker_image(*image: "NyunDocker"):
    """
    Pull Docker images in parallel using ThreadPoolExecutor.

    Args:
        *image (NyunDocker): One or more NyunDocker instances representing the Docker images to pull.

    Raises:
        Exception: If any of the images fail to pull.
    """
    client = get_docker_client()

    total = len(image)
    count = 0
    img_map = {}

    def counter(img):
        nonlocal img_map
        nonlocal count

        # return from memoized
        if img_map.get(str(img), False):
            return img_map.get(str(img))
        
        if count == total:
            count = 0
        count += 1
        img_map[str(img)] = count # memoize
        return count

    def wrap(repo, tag, task):
        try:
            if client.images.list(repo, tag, filters={"dangling": True}):
                return
            client.images.pull(repo, tag)
        except Exception as e:
            raise Exception(f"Failed to pull {repo}:{tag}") from e

    progress = Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=False,
    )
    with progress:
        tasks = {
            progress.add_task(
                f"[white]Loading component ({counter(img)}/{total}).",
                total=total,
                start=False,
            ): img
            for img in image
        }

        with ThreadPoolExecutor() as executor:
            futures = {
                executor.submit(wrap, img.repository, img.tag, tasks[task]): task
                for task, img in tasks.items()
            }

            for future in as_completed(futures):
                task = futures[future]
                img = tasks[task]

                try:
                    future.result()
                    progress.update(
                        task,
                        advance=1,
                        description=f"[green]Component ({counter(img)}/{total}) loaded.",
                        completed=True,
                        refresh=True,
                    )
                except Exception as e:
                    progress.stop()
                    raise Exception(f"Failed to pull {img.repository}:{img.tag}") from e


def remove_docker_image(*image: "NyunDocker"):
    """
    Remove Docker images.

    Args:
        *image (NyunDocker): One or more NyunDocker instances representing the Docker images to remove.

    Raises:
        Exception: If any of the images fail to remove.
    """
    client = get_docker_client()
    for img in image:
        try:
            client.images.remove(img.repository, img.tag)
            logger.info(f"Image {img} removed successfully")
        except Exception as e:
            logger.error(f"Image {img} failed to remove: {e}")
            raise Exception from e


def start_docker_container(*image: "NyunDocker"):
    """
    Start Docker containers in parallel using ThreadPoolExecutor.

    Args:
        *image (NyunDocker): One or more NyunDocker instances representing the Docker images to start.

    Raises:
        Exception: If any of the containers fail to start.
    """
    client = get_docker_client()

    with ThreadPoolExecutor() as executor:
        futures = {
            executor.submit(client.containers.crea, img.repository, img.tag): img
            for img in image
        }

        for future in futures:
            img = futures[future]
            try:
                future.result()
                logger.info(f"Container {img} started successfully")
            except Exception as e:
                logger.error(f"Container {img} failed to start: {e}")
                raise Exception from e


def run_docker_container(
    script: Path,
    workspace: "Workspace",
    metadata: "DockerMetadata",
    *image: "NyunDocker",
) -> Container:
    """
    Run a Docker container with a specified command in detached mode with auto-removal.

    Args:
        script (Path): The script path to run in the Docker container. (It will be mounted on the docker inside "/scripts").
        workspace (Workspace): The workspace object.
        metadata (DockerMetadata): The docker metadata object.
        *image (NyunDocker): A NyunDocker instance representing the Docker image to run.

    Returns:
        Container: The running Docker container.

    Raises:
        Exception: If the container fails to run.
    """

    # TODO: Update to handle running multiple containers

    try:
        client = get_docker_client()
        script_path = DockerPath.get_script_path_in_docker(script_path=script)
        command = DockerCommand.get_run_command(script_path=script_path)
        volumes = {
            str(workspace.workspace_path): {
                "bind": str(DockerPath.USER_DATA.value),
                "mode": "rw",
            },
            str(workspace.custom_data_path): {
                "bind": str(
                    DockerPath.get_customdata_path_in_docker(metadata.extension_type)
                ),
                "mode": "rw",
            },
            str(script.absolute().resolve()): {"bind": str(script_path), "mode": "rw"},
        }

        device_requests = [DeviceRequest(device_ids=["all"], capabilities=[["gpu"]])]

        logger.info(f"Running {image[0]} with command: {command}; Volumes: {volumes}")
        running_container: Container = client.containers.run(
            command=command,
            image=str(image[0]),
            device_requests=device_requests,
            detach=True,
            volumes=volumes,
            remove=True,
        )
        return running_container

    except Exception as e:
        logger.error(f"Container {image[0]} failed to run with command {command}: {e}")
        raise Exception from e


def remove_container(*image: "NyunDocker"):
    """
    Remove a Docker container.

    Args:
        *image (NyunDocker): A NyunDocker instance representing the Docker container to remove.

    Raises:
        Exception: If the container fails to remove.
    """
    client = get_docker_client()
    try:
        container_to_remove: Container = client.containers.get(
            container_id=image.container_id
        )
        container_to_remove.remove()
        logger.info(f"Container {image} removed successfully")
    except Exception as e:
        logger.error(f"Container {image} failed to remove: {e}")
        raise Exception from e
