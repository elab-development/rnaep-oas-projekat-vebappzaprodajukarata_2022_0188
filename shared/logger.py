from prometheus_fastapi_instrumentator import Instrumentator


def setup_metrics(app, service_name: str):
    Instrumentator(
        should_group_status_codes=True,
        should_ignore_untemplated=False,
        excluded_handlers=["/metrics"],
    ).instrument(app).expose(app)