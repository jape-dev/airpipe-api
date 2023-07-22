from api.models.user import User
from api.models.google_analytics import GoogleAnalyticsQuery
from api.database.models import UserDB
from api.utilities.google.ga_runner import REFRESH_ERROR, create_client
from api.utilities.string import underscore_to_camel_case
from api.database.database import session

from fastapi import HTTPException
from typing import List, Optional
from datetime import datetime, timedelta

from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange,
    Dimension,
    Metric,
    RunReportRequest,
)


def fetch_google_analytics_query(current_user: User, query: GoogleAnalyticsQuery):
        
    client = BetaAnalyticsDataClient()

    request = RunReportRequest(
        property=f"properties/{query.property_id}",
        dimensions=[Dimension(name=query.dimensions[0])],
        metrics=[Metric(name=query.metrics[0])],
        date_ranges=[DateRange(start_date=start, end_date=end)],
    )
    
    response = client.run_report(request)

    data = []

    for row in response.rows:

        data_row = {}

        for i, dimension in enumerate(query.dimensions):
            dimension_value = row.dimension_values[i].value
            data_row[dimension] = dimension_value

        for i, metric in enumerate(query.metrics):
            metric_value = row.metric_values[i].value
            data_row[metric] = metric_value

        data.append(data_row)

    return data



    




