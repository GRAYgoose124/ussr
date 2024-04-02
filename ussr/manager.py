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

    def transform(
        self, resource: Resource, extension: str, inverse=False, **kwargs
    ) -> Resource:
        transformer = self.translaters.get(extension)
        if not transformer:
            raise ValueError(f"No transformer for content type: {extension}")

        if inverse:
            transformer.inverse(resource, **kwargs)
        else:
            transformer.transform(resource, **kwargs)

        return resource

    def save(self, resource: Resource):
        handler = self.handler_factory.get_handler(resource.location_type)

        if handler is None:
            raise ValueError(f"No handler for location type: {resource.location_type}")

        handler.save(resource)

    def load(self, resource: Resource):
        handler = self.handler_factory.get_handler(resource.location_type)

        if handler is None:
            raise ValueError(f"No handler for location type: {resource.location_type}")

        payload = handler.load(resource, resource.location)
        resource.payload = payload
