import os
import json
import yaml
import logging
import requests
from abc import ABC, abstractmethod
from pathlib import Path
from dataclasses import dataclass
from typing import Literal, Dict, Type

log = logging.getLogger(__name__)


# Strategy Pattern for Resource Handlers
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
    handlers: Dict[str, Type[ResourceHandler]] = {
        "fs": FileSystemHandler,
        "url": UrlHandler,
    }

    def add_handler(self, location_type: str, handler: Type[ResourceHandler]):
        self.handlers[location_type] = handler

    @staticmethod
    def get_handler(location_type: str) -> ResourceHandler:
        handler_class = ResourceHandlerFactory.handlers.get(location_type)
        if not handler_class:
            raise ValueError(f"No handler for location type: {location_type}")
        return handler_class()


@dataclass
class ResourceTransformer(ABC):
    content_type: str = None

    @abstractmethod
    def transform(self, resource):
        pass


class JsonToYamlTransformer(ResourceTransformer):
    content_type = "yaml"

    def transform(self, resource):
        payload = json.loads(resource.payload.decode())
        return yaml.dump(payload).encode()


class YamlToJsonTransformer(ResourceTransformer):
    content_type = "json"

    def transform(self, resource):
        payload = yaml.load(resource.payload.decode(), Loader=yaml.FullLoader)
        return json.dumps(payload).encode()


@dataclass
class Resource:
    name: str
    location: str
    location_type: Literal["mem", "fs", "url"]
    content_type: str
    payload: bytes | str = None


class ResourceManager:
    def __init__(self):
        self.handler_factory = ResourceHandlerFactory()
        self._transformers = {}

    def register_transformer(self, transformer: ResourceTransformer, content_type=None):
        self._transformers[content_type] = transformer

    def transform(self, resource: Resource, content_type: str) -> Resource:
        transformer = self._transformers.get(content_type)
        if not transformer:
            raise ValueError(f"No transformer for content type: {content_type}")
        new_payload = transformer.transform(resource)
        resource.content_type = content_type
        resource.payload = new_payload
        return resource

    def save(self, resource: Resource, location=None):
        handler = self.handler_factory.get_handler(resource.location_type)
        if not location:
            location = (
                Path(resource.location).resolve()
                / f"{resource.name}.{resource.content_type}"
            )
        handler.save(resource, location)

    def load(self, resource: Resource):
        if resource.location_type in ["fs", "url"]:
            handler = self.handler_factory.get_handler(resource.location_type)
            resource.payload = handler.load(resource.location)
        else:
            log.warn("Cannot load a Resource from memory. Use .payload instead.")

        return resource


USSR = Resource
