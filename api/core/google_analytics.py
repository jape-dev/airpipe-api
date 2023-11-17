from datetime import datetime

from api.models.user import User
from api.models.google_analytics import GoogleAnalyticsQuery

from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange,
    Dimension,
    Metric,
    RunReportRequest,
)


def fetch_google_analytics_data(current_user: User, query: GoogleAnalyticsQuery):
    client = BetaAnalyticsDataClient()

    dimensions = [Dimension(name=dimension) for dimension in query.dimensions]
    metrics = [Metric(name=metric) for metric in query.metrics]
    request = RunReportRequest(
        property=f"properties/{query.property_id}",
        dimensions=dimensions,
        metrics=metrics,
        date_ranges=[
            DateRange(
                start_date=query.start_date.strftime("%Y-%m-%d"),
                end_date=query.end_date.strftime("%Y-%m-%d"),
            )
        ],
    )

    response = client.run_report(request)
    data = []

    for row in response.rows:
        data_row = {}
        for i, dimension in enumerate(query.dimensions):
            dimension_value = row.dimension_values[i].value
            if dimension == "date":
                date = str(row.dimension_values[i].value)
                date = datetime.strptime(date, "%Y%m%d")
                dimension_value = date.strftime("%Y-%m-%d")
            data_row[dimension] = dimension_value

        for i, metric in enumerate(query.metrics):
            metric_value = row.metric_values[i].value
            data_row[metric] = metric_value

        data.append(data_row)

    return data
