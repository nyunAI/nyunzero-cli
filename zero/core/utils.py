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
from docker.models.containers import Container
import click
from click import style


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

    count = 0
    def wrap(repo: str, tag: str):
        nonlocal count 
        count += 1
        with click.progressbar(
            label=f"Installing extension ({count}/{len(image)})",
            length=100,
            show_eta=True,
            show_percent=True,
            fill_char=style("#", fg="green"),
            empty_char=" ",
        ) as bar:
            for _ in bar:
                try:
                    client.images.pull(repo, tag)
                    logger.info(f"Image {repo}:{tag} pulled successfully")
                except Exception as e:
                    raise Exception(f"Failed to pull {repo}:{tag}") from e

    for img in image:
        wrap(img.repository, img.tag)
    

    # Use futures to pull multiple images in parallel
    # with ThreadPoolExecutor() as executor:
    #     futures = {
    #         executor.submit(wrap, img.repository, img.tag): img
    #         for img in image
    #     }

    #     for future in as_completed(futures):
    #         img = futures[future]
    #         try:
    #             future.result()
    #             logger.info(f"Image {img} pulled successfully")
    #         except Exception as e:
    #             logger.error(f"Image {img} failed to pull: {e}")
    #             raise Exception from e

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

def run_docker_container(command: str, *image: "NyunDocker", workspace_path: str, custom_data_path: str) -> Container:
    """
    Run a Docker container with a specified command in detached mode with auto-removal.

    Args:
        command (str): The command to run in the Docker container.
        *image (NyunDocker): A NyunDocker instance representing the Docker image to run.
        workspace_path (str): The path to the workspace directory to mount.
        custom_data_path (str): The path to the custom data directory to mount.

    Returns:
        Container: The running Docker container.

    Raises:
        Exception: If the container fails to run.
    """

    # TODO: Update to handle running multiple containers

    client = get_docker_client()

    try:
        volumes = {
            workspace_path: {"bind": "/workspace", "mode": "rw"},
            custom_data_path: {"bind": "/custom_data", "mode": "rw"},
        }

        running_container = client.containers.run(
            image=str(image[0]),
            command=command,
            detach=True,
            auto_remove=True,
            volumes=volumes,
        )

        logger.info(f"Container {image[0]} started successfully with command: {command}")
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
