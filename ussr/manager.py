import os
import json
import yaml
import logging
import requests
import copy
from abc import ABC, abstractmethod
from pathlib import Path
from dataclasses import dataclass
from typing import Literal, Dict, Type

from .handlers import ResourceHandlerFactory
from .transform import ResourceTransformer
from .resource import Resource

log = logging.getLogger(__name__)


class ResourceManager:
    def __init__(self):
        self.handler_factory = ResourceHandlerFactory()
        self.translaters = {}
        self.specialized_transformers = {}

    def register_transformer(self, transformer: ResourceTransformer, content_type=None):
        self.translaters[content_type] = transformer

    def transform(self, resource: Resource, content_type: str, **kwargs) -> Resource:
        transformer = self.translaters.get(content_type)
        if not transformer:
            raise ValueError(f"No transformer for content type: {content_type}")
        new_payload = transformer.transform(resource, **kwargs)
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
        handler = self.handler_factory.get_handler(resource.location_type)
        if handler is None:
            raise ValueError(f"No handler for location type: {resource.location_type}")

        resource_filename = (
            Path(resource.location).resolve()
            / f"{resource.name}.{resource.content_type}"
        )

        payload = handler.load(resource_filename)
        resource.payload = payload

    def clone(self, resource: Resource):
        return copy.deepcopy(resource)
