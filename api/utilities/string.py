def underscore_to_camel_case(s):
    parts = s.split("_")
    return parts[0] + "".join(part.title() for part in parts[1:])
