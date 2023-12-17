from datetime import datetime
from fastapi import HTTPException
import requests

from api.models.user import User
from api.models.google_analytics import GoogleAnalyticsQuery
from api.core.google import get_access_token

from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange,
    Dimension,
    Metric,
    RunReportRequest,
)


def fetch_google_analytics_data(current_user: User, query: GoogleAnalyticsQuery):
    dimensions = [{"name": dimension} for dimension in query.dimensions]
    metrics = [{"name": metric}  for metric in query.metrics]
    request_body = {
        "dimensions": dimensions,
        "metrics": metrics,
        "dateRanges": [
            {
                "startDate": query.start_date.strftime("%Y-%m-%d"),
                "endDate": query.end_date.strftime("%Y-%m-%d")
            }
        ]
    }

    # response = client.run_report(request)
    access_token = get_access_token(current_user.google_analytics_refresh_token)
    response = requests.post(
        f"https://analyticsdata.googleapis.com/v1beta/properties/{query.property_id}:runReport",
        json=request_body,
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )   

    data = []
    if response.status_code == 200:
        json_response = response.json()
        if "rows" in json_response:
            for row in json_response["rows"]:
                data_row = {}
                for i, dimension in enumerate(query.dimensions):
                    dimension_value = row["dimensionValues"][i]["value"]
                    if dimension == "date":
                        date = str(row["dimensionValues"][i]["value"])
                        date = datetime.strptime(date, "%Y%m%d")
                        dimension_value = date.strftime("%Y-%m-%d")
                    data_row[dimension] = dimension_value

                for i, metric in enumerate(query.metrics):
                    metric_value = row["metricValues"][i]["value"]
                    data_row[metric] = metric_value

                data.append(data_row)
        else:
            raise HTTPException(
                status_code=400,
                detail=f"No values found. {json_response}"
            )
    else:
        print(response.text)
        raise HTTPException(
                status_code=400,
                detail=f"Could not get data. {response.text}",
            )

    return data
