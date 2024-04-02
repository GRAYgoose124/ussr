import json
import os
import logging
import magic

from ussr import *

from .constructors import from_file, from_url

log = logging.getLogger(__name__)


def main():
    logging.basicConfig(level=logging.DEBUG)

    #
    RM = ResourceManager()

    # Create a resource with JSON content
    # json_payload = json.dumps({"key": "value", "age": 30}).encode()
    # resource = USSR(
    #     name="my_resource",
    #     location=".",
    #     location_type="fs",
    #     content_type="json",
    #     payload=json_payload,
    # )

    # # Register transformers
    # RM.register_transformer(JsonToYamlTransformer(), "yaml")
    # RM.register_transformer(YamlToJsonTransformer(), "json")
    yaml_zip = YamlToJsonTransformer() >> CompressionTransformer()
    RM.register_transformer(yaml_zip, "yaml.zlib.bin")

    compressor = CompressionTransformer()
    RM.register_transformer(compressor, "zlib.bin")

    # # Save the resource as YAML
    # RM.transform(resource, "yaml")
    # RM.save(resource)

    # # CLone then transform
    # resource2 = resource.clone()
    # print(resource2)
    # # RM.transform(resource2, "json")
    # # RM.save(resource2)
    # RM.transform(resource2, "yaml.zlib.bin")
    # RM.save(resource2)

    # # assert os.path.exists("my_resource.yaml")
    # # assert os.path.exists("my_resource.yml.zip")

    # # decompress and load
    # r3 = resource2.clone()
    # print(r3)
    # # print(r3)
    # # r3.payload = ""
    # # print(r3)
    # # RM.load(r3)
    # # print(r3)
    # t = RM.transform(r3, "yaml.zlib.bin", mode="decompress", inverse=True)
    # print(t)

    r = from_file("my_resource.yaml")
    print(r)
    r = RM.transform(r, "yaml.zlib.bin")
    r0 = r.clone()
    print(r)
    r1 = RM.transform(r, "zlib.bin", inverse=True)
    print(r1)
    r2 = RM.transform(r0, "yaml.zlib.bin", inverse=True)
    print(r2)
    print(yaml_zip)
    a = from_url("https://www.google.com")

    T = StrToBytesTransformer() >> BytesToMimeMessageTransformer()

    print(a)
    BytesToMimeMessageTransformer().transform(a)
    print(a)


if __name__ == "__main__":
    main()
