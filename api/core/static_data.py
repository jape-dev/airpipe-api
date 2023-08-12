from enum import Enum


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
