from enum import Enum


class ChannelType(str, Enum):

    google = "google"
    facebook = "facebook"


class FieldType(str, Enum):

    metric = "metric"
    dimension = "dimension"
