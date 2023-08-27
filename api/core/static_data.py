from enum import Enum


def get_enum_member_by_value(enum_cls, value):
    for member in enum_cls.__members__.values():
        if member.value == value:
            return member
    raise ValueError(f"No {enum_cls.__name__} member with value '{value}'")


class ChannelType(str, Enum):
    google = "google"
    facebook = "facebook"
    google_analytics = "google_analytics"


class FieldType(str, Enum):
    metric = "metric"
    dimension = "dimension"


class OnboardingStage(str, Enum):
    connect = "connect"
    add_data = "add_data"
    ask = "ask"
    complete = "complete"


class Environment(str, Enum):
    production = "production"
    development = "development"
