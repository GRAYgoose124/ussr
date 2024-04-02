import os, shutil, logging, requests
from abc import ABC, abstractmethod
from pathlib import Path
from dataclasses import dataclass
from typing import Literal, Dict, Type

log = logging.getLogger(__name__)


class ResourceHandler(ABC):
    @abstractmethod
    def save(self, resource):
        pass

    @abstractmethod
    def load(self, resource):
        pass


class FileSystemHandler(ResourceHandler):
    def save(self, resource):
        try:
            os.makedirs(Path(resource.location).parent, exist_ok=True)

            with open(
                Path(resource.location).resolve()
                / f"{resource.name}.{resource.extension}",
                "wb" if isinstance(resource.payload, bytes) else "w",
            ) as f:
                f.write(resource.payload)
        except Exception as e:
            log.error(f"Error saving file: {e}")
            raise

    def load(self, resource):
        try:
            with open(
                Path(resource.location).resolve()
                / f"{resource.name}.{resource.extension}",
                "rb",
            ) as f:
                return f.read()
        except Exception as e:
            log.error(f"Error loading file: {e}")
            raise


class UrlHandler(ResourceHandler):
    def load(self, resource):
        try:
            response = requests.get(resource.location)
            response.raise_for_status()
            return response.content
        except Exception as e:
            log.error(f"Error loading URL: {e}")
            raise


class MemoryHandler(ResourceHandler):
    def save(self, resource):
        return resource.clone()

    def load(self, resource):
        return resource.payload


class ResourceHandlerFactory:
    handlers: dict[str, Type[ResourceHandler]] = {
        "fs": FileSystemHandler,
        "url": UrlHandler,
        "mem": MemoryHandler,
    }

    def add_handler(self, location_type: str, handler: Type[ResourceHandler]):
        self.handlers[location_type] = handler

    @staticmethod
    def get_handler(location_type: str) -> ResourceHandler:
        handler_class = ResourceHandlerFactory.handlers.get(location_type)
        if not handler_class:
            return None
        return handler_class()
