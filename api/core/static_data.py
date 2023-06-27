from enum import Enum


class ChannelType(str, Enum):

    google = "google"
    facebook = "facebook"


class FieldType(str, Enum):

    metric = "metric"
    dimension = "dimension"


# based on the channel types and the field names.
class ForeignKeys(dict, Enum):

    date = "[google.date == facebook.date]"
    name = "[google.name == facebook.campaign_name]"
