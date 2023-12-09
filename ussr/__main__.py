import json
import os
import logging

from ussr import *

log = logging.getLogger(__name__)


def main():
    logging.basicConfig(level=logging.DEBUG)

    #
    RM = ResourceManager()

    # Create a resource with JSON content
    json_payload = json.dumps({"key": "value", "age": 30}).encode()
    resource = USSR(
        name="my_resource",
        location=".",
        location_type="fs",
        content_type="json",
        payload=json_payload,
    )

    # Register transformers
    RM.register_transformer(JsonToYamlTransformer(), "yaml")
    RM.register_transformer(YamlToJsonTransformer(), "json")
    yaml_zip = YamlToJsonTransformer() >> CompressionTransformer()
    RM.register_transformer(yaml_zip, "zlib.bin")

    # Save the resource as YAML
    RM.transform(resource, "yaml")
    RM.save(resource)

    # CLone then transform
    resource2 = RM.clone(resource)
    RM.transform(resource2, "json")
    # RM.save(resource2)
    RM.transform(resource2, "zlib.bin")
    RM.save(resource2)

    # assert os.path.exists("my_resource.yaml")
    # assert os.path.exists("my_resource.yml.zip")

    # decompress and load
    r3 = RM.clone(resource2)
    r3.payload = ""
    print(r3)
    RM.load(r3)
    print(r3)
    RM.transform(r3, "zlib.bin", mode="decompress")


if __name__ == "__main__":
    main()
