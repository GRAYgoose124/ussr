def extension_from_content_type(content_type: str) -> str:
    return content_type.split("/")[1].split(";")[0]
