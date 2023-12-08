import json
import os
import logging

from ussr import USSR, JsonToYamlTransformer, YamlToJsonTransformer, ResourceManager

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

    # Save the resource as YAML
    RM.transform(resource, "yaml")
    RM.save(resource)

    assert os.path.exists("my_resource.yaml")


if __name__ == "__main__":
    main()
