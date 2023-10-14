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
    sheets = "sheets"


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


class LookerFieldType(str, Enum):
    text = "TEXT"
    number = "NUMBER"
    date = "YEAR_MONTH_DAY"
    boolean = "BOOLEAN"


facebook_metrics = [
    {
        "value": "clicks",
        "label": "Clicks",
        "alt_value": "facebook_clicks",
        "type": FieldType.metric,
        "channel": ChannelType.facebook,
        "img": "facebook-icon",
    },
    {
        "value": "conversions",
        "label": "Conversions",
        "alt_value": "facebook_conversions",
        "type": FieldType.metric,
        "channel": ChannelType.facebook,
        "img": "facebook-icon",
    },
    {
        "value": "cost_per_conversion",
        "label": "Cost Per Conversion",
        "alt_value": "facebook_cost_per_conversion",
        "type": FieldType.metric,
        "channel": ChannelType.facebook,
        "img": "facebook-icon",
    },
    {
        "value": "cpc",
        "label": "CPC",
        "alt_value": "facebook_cpc",
        "type": FieldType.metric,
        "channel": ChannelType.facebook,
        "img": "facebook-icon",
    },
    {
        "value": "cpm",
        "label": "CPM",
        "alt_value": "facebook_cpm",
        "type": FieldType.metric,
        "channel": ChannelType.facebook,
        "img": "facebook-icon",
    },
    {
        "value": "cpp",
        "label": "CPP",
        "alt_value": "facebook_cpp",
        "type": FieldType.metric,
        "channel": ChannelType.facebook,
        "img": "facebook-icon",
    },
    {
        "value": "ctr",
        "label": "CTR",
        "alt_value": "facebook_ctr",
        "type": FieldType.metric,
        "channel": ChannelType.facebook,
        "img": "facebook-icon",
    },
    {
        "value": "frequency",
        "label": "Frequency",
        "alt_value": "facebook_frequency",
        "type": FieldType.metric,
        "channel": ChannelType.facebook,
        "img": "facebook-icon",
    },
    {
        "value": "impressions",
        "label": "Impressions",
        "alt_value": "facebook_impressions",
        "type": FieldType.metric,
        "channel": ChannelType.facebook,
        "img": "facebook-icon",
    },
    {
        "value": "reach",
        "label": "Reach",
        "alt_value": "facebook_reach",
        "type": FieldType.metric,
        "channel": ChannelType.facebook,
        "img": "facebook-icon",
    },
    {
        "value": "spend",
        "label": "Spend",
        "alt_value": "facebook_spend",
        "type": FieldType.metric,
        "channel": ChannelType.facebook,
        "img": "facebook-icon",
    },
]

facebook_dimensions = [
    {
        "value": "account_id",
        "label": "Account Id",
        "alt_value": "facebook_account_id",
        "type": FieldType.dimension,
        "channel": ChannelType.facebook,
        "img": "facebook-icon",
    },
    {
        "value": "account_name",
        "label": "Account Name",
        "alt_value": "facebook_account_name",
        "type": FieldType.dimension,
        "channel": ChannelType.facebook,
        "img": "facebook-icon",
    },
    {
        "value": "adset_id",
        "label": "Adset Id",
        "alt_value": "facebook_adset_id",
        "type": FieldType.dimension,
        "channel": ChannelType.facebook,
        "img": "facebook-icon",
    },
    {
        "value": "adset_name",
        "label": "Adset Name",
        "alt_value": "facebook_adset_name",
        "type": FieldType.dimension,
        "channel": ChannelType.facebook,
        "img": "facebook-icon",
    },
    {
        "value": "campaign_id",
        "label": "Campaign Id",
        "alt_value": "facebook_campaign_id",
        "type": FieldType.dimension,
        "channel": ChannelType.facebook,
        "img": "facebook-icon",
    },
    {
        "value": "campaign_name",
        "label": "Campaign Name",
        "alt_value": "facebook_campaign_name",
        "type": FieldType.dimension,
        "channel": ChannelType.facebook,
        "img": "facebook-icon",
    },
    {
        "value": "ad_id",
        "label": "Ad Id",
        "alt_value": "facebook_ad_id",
        "type": FieldType.dimension,
        "channel": ChannelType.facebook,
        "img": "facebook-icon",
    },
    {
        "value": "ad_name",
        "label": "Ad Name",
        "alt_value": "facebook_ad_name",
        "type": FieldType.dimension,
        "channel": ChannelType.facebook,
        "img": "facebook-icon",
    },
]

facebook_date = [
    {
        "value": "date",
        "label": "Date",
        "alt_value": "date",
        "type": FieldType.dimension,
        "channel": ChannelType.facebook,
        "img": "facebook-icon",
    }
]

google_metrics = [
    {
        "value": "metrics.average_cpc",
        "label": "CPC",
        "alt_value": "google_cpc",
        "type": FieldType.metric,
        "channel": ChannelType.google,
        "img": "google-ads-icon",
    },
    {
        "value": "metrics.average_cpe",
        "label": "CPE",
        "alt_value": "google_cpe",
        "type": FieldType.metric,
        "channel": ChannelType.google,
        "img": "google-ads-icon",
    },
    {
        "value": "metrics.average_cpm",
        "label": "CPM",
        "alt_value": "google_cpm",
        "type": FieldType.metric,
        "channel": ChannelType.google,
        "img": "google-ads-icon",
    },
    {
        "value": "metrics.average_cpv",
        "label": "CPV",
        "alt_value": "google_cpv",
        "type": FieldType.metric,
        "channel": ChannelType.google,
        "img": "google-ads-icon",
    },
    {
        "value": "metrics.clicks",
        "label": "Clicks",
        "alt_value": "google_clicks",
        "type": FieldType.metric,
        "channel": ChannelType.google,
        "img": "google-ads-icon",
    },
    {
        "value": "metrics.conversions",
        "label": "Conversions",
        "alt_value": "google_conversions",
        "type": FieldType.metric,
        "channel": ChannelType.google,
        "img": "google-ads-icon",
    },
    {
        "value": "metrics.cost_micros",
        "label": "Spend",
        "alt_value": "google_spend",
        "type": FieldType.metric,
        "channel": ChannelType.google,
        "img": "google-ads-icon",
    },
    {
        "value": "metrics.cost_per_conversion",
        "label": "Cost Per Conversion",
        "alt_value": "google_cost_per_conversion",
        "type": FieldType.metric,
        "channel": ChannelType.google,
        "img": "google-ads-icon",
    },
    {
        "value": "metrics.engagements",
        "label": "Engagements",
        "alt_value": "google_engagements",
        "type": FieldType.metric,
        "channel": ChannelType.google,
        "img": "google-ads-icon",
    },
    {
        "value": "metrics.impressions",
        "label": "Impressions",
        "alt_value": "google_impressions",
        "type": FieldType.metric,
        "channel": ChannelType.google,
        "img": "google-ads-icon",
    },
    {
        "value": "metrics.interactions",
        "label": "Interactions",
        "alt_value": "google_interactions",
        "type": FieldType.metric,
        "channel": ChannelType.google,
        "img": "google-ads-icon",
    },
]

google_date = [
    {
        "value": "segments.date",
        "label": "Date",
        "alt_value": "date",
        "type": FieldType.dimension,
        "channel": ChannelType.google,
        "img": "google-ads-icon",
    }
]

google_dimensions = [
    {
        "value": "ad_group_ad.ad.id",
        "label": "Ad Id",
        "type": FieldType.dimension,
        "channel": ChannelType.google,
        "alt_value": "google_ad_id",
        "img": "google-ads-icon",
    },
    {
        "value": "ad_group_ad.ad.name",
        "label": "Ad Name",
        "type": FieldType.dimension,
        "channel": ChannelType.google,
        "alt_value": "google_ad_name",
        "img": "google-ads-icon",
    },
    {
        "value": "ad_group.name",
        "label": "Ad Group Name",
        "type": FieldType.dimension,
        "channel": ChannelType.google,
        "alt_value": "google_ad_group_name",
        "img": "google-ads-icon",
    },
    {
        "value": "ad_group.id",
        "label": "Ad Group Id",
        "alt_value": "google_ad_group_id",
        "type": FieldType.dimension,
        "channel": ChannelType.google,
        "img": "google-ads-icon",
    },
    {
        "value": "campaign.id",
        "label": "Campaign Id",
        "alt_value": "google_campaign_id",
        "type": FieldType.dimension,
        "channel": ChannelType.google,
        "img": "google-ads-icon",
    },
    {
        "value": "campaign.name",
        "label": "Campaign Name",
        "alt_value": "google_campaign_name",
        "type": FieldType.dimension,
        "channel": ChannelType.google,
        "img": "google-ads-icon",
    },
    {
        "value": "segments.keyword.info.text",
        "label": "Keyword Text",
        "alt_value": "google_keyword_text",
        "type": FieldType.dimension,
        "channel": ChannelType.google,
        "img": "google-ads-icon",
    },
]

google_analytics_date = [
    {
        "value": "date",
        "label": "Date",
        "alt_value": "date",
        "type": FieldType.dimension,
        "channel": ChannelType.google_analytics,
        "img": "google-analytics-icon",
    }
]

google_analytics_metrics = [
    {
        "value": "totalUsers",
        "label": "Total Users",
        "alt_value": "google_analytics_users",
        "type": FieldType.metric,
        "channel": ChannelType.google_analytics,
        "img": "google-analytics-icon",
    },
    {
        "value": "newUsers",
        "label": "New Users",
        "alt_value": "google_analytics_new_users",
        "type": FieldType.metric,
        "channel": ChannelType.google_analytics,
        "img": "google-analytics-icon",
    },
    {
        "value": "activeUsers",
        "label": "Active Users",
        "alt_value": "google_analytics_active_Users",
        "type": FieldType.metric,
        "channel": ChannelType.google_analytics,
        "img": "google-analytics-icon",
    },
    {
        "value": "sessions",
        "label": "Sessions",
        "alt_value": "google_analytics_sessions",
        "type": FieldType.metric,
        "channel": ChannelType.google_analytics,
        "img": "google-analytics-icon",
    },
    {
        "value": "transactions",
        "label": "Transactions",
        "alt_value": "google_analytics_transactions",
        "type": FieldType.metric,
        "channel": ChannelType.google_analytics,
        "img": "google-analytics-icon",
    },
    {
        "value": "checkouts",
        "label": "Checkouts",
        "alt_value": "google_analytics_checkouts",
        "type": FieldType.metric,
        "channel": ChannelType.google_analytics,
        "img": "google-analytics-icon",
    },
    {
        "value": "conversions",
        "label": "Conversions",
        "alt_value": "google_analytics_conversions",
        "type": FieldType.metric,
        "channel": ChannelType.google_analytics,
        "img": "google-analytics-icon",
    },
]


# Define the data as Python objects
google_analytics_dimensions = [
    {
        "value": "browser",
        "label": "Browser",
        "alt_value": "google_analytics_browser",
        "type": FieldType.dimension,
        "channel": ChannelType.google_analytics,
        "img": "google-analytics-icon",
    },
    {
        "value": "city",
        "label": "City",
        "alt_value": "google_analytics_city",
        "type": FieldType.dimension,
        "channel": ChannelType.google_analytics,
        "img": "google-analytics-icon",
    },
    {
        "value": "continent",
        "label": "Continent",
        "alt_value": "google_analytics_continent",
        "type": FieldType.dimension,
        "channel": ChannelType.google_analytics,
        "img": "google-analytics-icon",
    },
    {
        "value": "country",
        "label": "Country",
        "alt_value": "google_analytics_country",
        "type": FieldType.dimension,
        "channel": ChannelType.google_analytics,
        "img": "google-analytics-icon",
    },
    {
        "value": "eventName",
        "label": "Event Name",
        "alt_value": "google_analytics_event_Name",
        "type": FieldType.dimension,
        "channel": ChannelType.google_analytics,
        "img": "google-analytics-icon",
    },
    {
        "value": "deviceCategory",
        "label": "Device Category",
        "alt_value": "google_analytics_device_Category",
        "type": FieldType.dimension,
        "channel": ChannelType.google_analytics,
        "img": "google-analytics-icon",
    },
    {
        "value": "medium",
        "label": "Medium",
        "alt_value": "google_analytics_medium",
        "type": FieldType.dimension,
        "channel": ChannelType.google_analytics,
        "img": "google-analytics-icon",
    },
    {
        "value": "source",
        "label": "Source",
        "alt_value": "google_analytics_source",
        "type": FieldType.dimension,
        "channel": ChannelType.google_analytics,
        "img": "google-analytics-icon",
    },
]
