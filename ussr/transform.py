import logging
import json, yaml, csv, zlib
import email

from abc import ABC, abstractmethod
from pathlib import Path
from dataclasses import dataclass
from typing import Literal, Type

from .resource import Resource


log = logging.getLogger(__name__)


@dataclass
class ResourceTransformer(ABC):
    extension: str = None

    @abstractmethod
    def inverse(self, resource, **kwargs):
        pass

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
    def __init__(self, *transformers: ResourceTransformer):
        self.transformers = transformers

    def inverse(self, resource, **kwargs):
        until = kwargs.get("until", None)
        for transformer in self.transformers[:until:-1]:
            transformer.inverse(resource, **kwargs)

    def transform(self, resource, **kwargs):
        until = kwargs.get("until", None)
        for transformer in self.transformers[:until]:
            transformer.transform(resource, **kwargs)

    def __repr__(self):
        return " -> ".join(
            [str(transformer.__class__.__name__) for transformer in self.transformers]
        )


class JsonToYamlTransformer(ResourceTransformer):
    extension = "yaml"

    def inverse(self, resource):
        YamlToJsonTransformer().transform(resource)

    def transform(self, resource):
        payload = json.loads(resource.payload.decode())
        resource.payload = yaml.dump(payload).encode()


class YamlToJsonTransformer(ResourceTransformer):
    extension = "json"

    def inverse(self, resource):
        JsonToYamlTransformer().transform(resource)

    def transform(self, resource):
        payload = yaml.load(resource.payload.decode(), Loader=yaml.FullLoader)
        resource.payload = json.dumps(payload).encode()


class JsonToCsvTransformer(ResourceTransformer):
    extension = "csv"

    def inverse(self, resource):
        CsvToJsonTransformer().transform(resource)

    def transform(self, resource):
        """We will construct our csv payload as a list of lists representing the rows and columns of the json payload."""
        payload = json.loads(resource.payload.decode())
        csv_payload = []
        for key, value in payload.items():
            csv_payload.append([key, value])
        resource.payload = csv_payload


class CsvToJsonTransformer(ResourceTransformer):
    extension = "json"

    def inverse(self, resource):
        JsonToCsvTransformer().transform(resource)

    def transform(self, resource):
        """We will construct our json payload as a dictionary of lists representing the rows and columns of the csv file."""
        payload = {}
        with open(resource.payload, newline="") as csvfile:
            reader = csv.reader(csvfile, delimiter=",")
            for row in reader:
                if row[0] not in payload:
                    payload[row[0]] = []
                payload[row[0]].append(row[1])
        resource.payload = json.dumps(payload).encode()


class CompressionTransformer(ResourceTransformer):
    extension = "zlib.bin"

    def inverse(self, resource):
        resource.payload = zlib.decompress(resource.payload)

    def transform(self, resource):
        """Takes any resource or payload and compresses it."""
        resource.payload = zlib.compress(resource.payload)


class StrToBytesTransformer(ResourceTransformer):
    extension = "bytes"

    def inverse(self, resource):
        resource.payload = resource.payload.decode()

    def transform(self, resource):
        """Takes any resource or payload and compresses it."""
        resource.payload = resource.payload.encode()


class BytesToMimeMessageTransformer(ResourceTransformer):
    extension = "email"

    def inverse(self, resource):
        resource.payload = resource.payload.as_bytes()

    def transform(self, resource):
        """Takes any resource or payload and compresses it."""
        resource.payload = email.message_from_bytes(resource.payload)
