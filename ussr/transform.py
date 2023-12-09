import logging
import json, yaml, csv, zlib

from abc import ABC, abstractmethod
from pathlib import Path
from dataclasses import dataclass
from typing import Literal, Type

from .resource import Resource


log = logging.getLogger(__name__)


@dataclass
class ResourceTransformer(ABC):
    content_type: str = None

    @abstractmethod
    def transform(self, resource, **kwargs):
        pass

    def __rshift__(self, resource_or_transformer):
        if isinstance(resource_or_transformer, Resource):
            return self.transform(resource_or_transformer)
        elif isinstance(resource_or_transformer, ResourceTransformer):
            return ComposedTransformer(self, resource_or_transformer)
        else:
            raise ValueError(
                f"Cannot compose {type(self)} with {type(resource_or_transformer)}"
            )


class ComposedTransformer(ResourceTransformer):
    def __init__(
        self, transformer1: ResourceTransformer, transformer2: ResourceTransformer
    ):
        self.transformer1 = transformer1
        self.transformer2 = transformer2

    def transform(self, resource, **kwargs):
        return self.transformer2.transform(
            self.transformer1.transform(resource, **kwargs), **kwargs
        )


class JsonToYamlTransformer(ResourceTransformer):
    content_type = "yaml"

    def transform(self, resource):
        payload = json.loads(resource.payload.decode())
        return yaml.dump(payload).encode()


class YamlToJsonTransformer(ResourceTransformer):
    content_type = "json"

    def transform(self, resource, **kwargs):
        payload = yaml.load(resource.payload.decode(), Loader=yaml.FullLoader)
        return json.dumps(payload).encode()


class CsvToJsonTransformer(ResourceTransformer):
    content_type = "json"

    def transform(self, resource, **kwargs):
        """We will construct our json payload as a dictionary of lists representing the rows and columns of the csv file."""
        payload = {}
        with open(resource.payload, newline="") as csvfile:
            reader = csv.reader(csvfile, delimiter=",")
            for row in reader:
                if row[0] not in payload:
                    payload[row[0]] = []
                payload[row[0]].append(row[1])
        return json.dumps(payload).encode()

        import zlib


class CompressionTransformer(ResourceTransformer):
    content_type = "zlib.bin"

    def transform(self, resource_or_payload, mode="compress", **kwargs):
        """Takes any resource or payload and compresses it."""

        if isinstance(resource_or_payload, Resource):
            payload = resource_or_payload.payload
        else:
            payload = resource_or_payload

        if mode == "decompress":
            return zlib.decompress(payload)
        else:
            return zlib.compress(payload)
