import ast
import re


def underscore_to_camel_case(s):
    parts = s.split("_")
    return parts[0] + "".join(part.title() for part in parts[1:])


def remove_decimal(s, is_list=True):
    pattern = r"Decimal\(([^)]+)\)"
    replaced = re.sub(pattern, r"\1", s)
    if is_list:
        replaced = ast.literal_eval(replaced)
    return replaced
