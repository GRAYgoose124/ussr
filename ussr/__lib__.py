# Extended ResourceTransformer class to include file extension
from dataclasses import dataclass
from enum import Enum
import json
import os
from pathlib import Path
from typing import Literal
import logging
import yaml
import requests

log = logging.getLogger(__name__)


class ResourceTransformer:
    def __init__(self, content_type: str):
        self.content_type = content_type

    def __call__(self, resource):
        raise NotImplementedError


# Specific transformers with file extensions
class JsonToYamlTransformer(ResourceTransformer):
    def __init__(self):
        super().__init__("yaml")

    def __call__(self, resource):
        payload = json.loads(resource.payload.decode())
        return yaml.dump(payload).encode()


class YamlToJsonTransformer(ResourceTransformer):
    def __init__(self):
        super().__init__("json")

    def __call__(self, resource):
        payload = yaml.load(resource.payload.decode(), Loader=yaml.FullLoader)
        return json.dumps(payload).encode()


class FileSystemObject:
    @staticmethod
    def save(payload, location, mkdirs=False):
        if mkdirs:
            os.makedirs(Path(location).resolve().parent, exist_ok=True)

        with open(
            location,
            f"w{'b' if isinstance(payload, bytes) else '' if Path(location).exists() else '+'}",
        ) as f:
            f.write(payload)

    @staticmethod
    def load(location, bytes=False):
        with open(location, f"w{'b' if bytes else ''}") as f:
            return f.read()


class UrlObject:
    @staticmethod
    def load(location, bytes=False):
        requests.get(location)


@dataclass
class UnifiedSimpleScientificResource:
    name: str
    location: str
    location_type: Literal["mem", "fs", "url"]
    content_type: str
    payload: bytes | str = None

    def __post_init__(self):
        self._registered_content_mappings: dict[str, ResourceTransformer] = {}

    def register_transformer(self, transformer: ResourceTransformer):
        self._registered_content_mappings[transformer.content_type] = transformer

    def transform(self, content_type: str) -> "UnifiedSimpleScientificResource":
        transformer = self._registered_content_mappings.get(content_type)
        if transformer is None:
            raise ValueError(
                f"No transformer registered for content type: {content_type}"
            )

        # Transform to the new content type and return a new in-memory resource
        return UnifiedSimpleScientificResource(
            name=self.name,
            location=self.location,
            location_type=self.location_type,
            payload=transformer(self),
            content_type=content_type,
        )

    def save(self, location_type=None, content_type=None):
        if location_type is None:
            location_type = self.location_type

        if content_type is not None:
            return self.transform(content_type).save(location_type=location_type)

        if location_type == "fs":
            FileSystemObject.save(
                self.payload,
                Path(self.location).resolve() / f"{self.name}.{self.content_type}",
                mkdirs=True,
            )
        elif location_type == "mem" or location_type == "url":
            log.warn("Cannot save a Resource to %s.", location_type)

        return self

    def load(self):
        if self.location_type == "fs":
            self.payload = FileSystemObject.load(
                Path(self.location).resolve() / f"{self.name}.{self.content_type}"
            )
        elif self.location_type == "url":
            self.payload = UrlObject.load(self.location)
        elif self.location_type == "mem":
            log.warn("Cannot load a Resource from memory. Use .payload instead.")

        return self


USSR = UnifiedSimpleScientificResource
