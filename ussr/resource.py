from dataclasses import dataclass
from typing import Literal, Dict, Type
import magic


class EasyDataClassMeta(type):
    def __new__(cls, name, bases, attrs):
        fields = {}
        for k, v in attrs.items():
            if isinstance(v, str):
                fields[k] = v
        attrs["__annotations__"] = fields
        return super().__new__(cls, name, bases, attrs)


@dataclass
class Resource:
    name: str
    location: str
    location_type: Literal["mem", "fs", "url"]
    extension: str = None
    content_type: str = None
    encoding: str = None
    payload: bytes | str = None

    def clone(self):
        return Resource(**self.__dict__)


USSR = Resource
