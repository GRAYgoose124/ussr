import json
import os

from ussr import USSR, JsonToYamlTransformer, YamlToJsonTransformer


def test_USSR_basic_transform():
    # Create a resource with JSON content
    json_payload = json.dumps({"key": "value", "age": 30}).encode()
    resource = USSR(
        name="my_resource",
        location="example",
        location_type="fs",
        content_type="json",
        payload=json_payload,
    )

    # Register transformers
    resource.register_transformer(JsonToYamlTransformer())
    resource.register_transformer(YamlToJsonTransformer())

    # Save the resource as YAML
    print(resource.save(content_type="yaml"))
    assert os.path.exists("example.yaml")

    resource.save()
    assert os.path.exists("example.json")

    # remove the files
    os.remove("example.yaml")
    os.remove("example.json")
