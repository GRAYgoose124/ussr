from dataclasses import dataclass
from typing import Literal, Dict, Type


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
    content_type: str
    payload: bytes | str = None


USSR = Resource
