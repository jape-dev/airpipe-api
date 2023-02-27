from ga_runner import create_client


def get_google_ads_metrics(customer_id, metrics,
                           dimensions, start_date,
                           end_date, token):
    client = create_client(token)
    ga_service = client.get_service("GoogleAdsService")

    # Combine metrics and dimensions.
    # build select query using metrics and dimensions.
    fields = metrics + dimensions
    query_fields = ", ".join(fields)
    query = f"""
        SELECT
            {query_fields}
        WHERE segments.date >= '{start_date}' and segments.date <= '{end_date}'
    """

    search_request = client.get_type("SearchGoogleAdsStreamRequest")
    search_request.customer_id = customer_id
    search_request.query = query
    stream = ga_service.search_stream(search_request)

    for batch in stream:
        for row in batch.results:
            metrics = row.metrics

    return "something"
