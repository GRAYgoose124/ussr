import os, shutil, logging, requests
from abc import ABC, abstractmethod
from pathlib import Path
from dataclasses import dataclass
from typing import Literal, Dict, Type

log = logging.getLogger(__name__)


class ResourceHandler(ABC):
    @abstractmethod
    def save(self, resource, location):
        pass

    @abstractmethod
    def load(self, location):
        pass


class FileSystemHandler(ResourceHandler):
    def save(self, resource, location):
        try:
            os.makedirs(Path(location).parent, exist_ok=True)
            with open(
                location, "wb" if isinstance(resource.payload, bytes) else "w"
            ) as f:
                f.write(resource.payload)
        except Exception as e:
            log.error(f"Error saving file: {e}")
            raise

    def load(self, location):
        try:
            with open(location, "rb") as f:
                return f.read()
        except Exception as e:
            log.error(f"Error loading file: {e}")
            raise


class UrlHandler(ResourceHandler):
    def load(self, location):
        try:
            response = requests.get(location)
            response.raise_for_status()
            return response.content
        except Exception as e:
            log.error(f"Error loading URL: {e}")
            raise


class ResourceHandlerFactory:
    handlers: dict[str, Type[ResourceHandler]] = {
        "fs": FileSystemHandler,
        "url": UrlHandler,
    }

    def add_handler(self, location_type: str, handler: Type[ResourceHandler]):
        self.handlers[location_type] = handler

    @staticmethod
    def get_handler(location_type: str) -> ResourceHandler:
        handler_class = ResourceHandlerFactory.handlers.get(location_type)
        if not handler_class:
            return None
        return handler_class()
