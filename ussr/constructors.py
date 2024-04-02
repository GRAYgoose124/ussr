from pathlib import Path
import magic
import requests

from .resource import Resource
from .helpers import extension_from_content_type


def from_file(file_path: str):
    file_path = Path(file_path)
    with open(file_path, "rb") as f:
        return Resource(
            name=file_path.stem,
            location=file_path.parent,
            location_type="fs",
            extension=file_path.suffix[1:],
            content_type=magic.Magic(mime=True).from_file(str(file_path)),
            payload=f.read(),
        )


def from_url(url: str):
    response = requests.get(url)
    return Resource(
        name=response.text.split("<title>")[1].split("</title>")[0],
        location=url,
        location_type="url",
        content_type=response.headers["Content-Type"],
        extension=extension_from_content_type(response.headers["Content-Type"]),
        encoding=response.encoding,
        payload=response.content,
    )
