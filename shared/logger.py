from prometheus_fastapi_instrumentator import Instrumentator


def setup_metrics(app, service_name: str):
    Instrumentator(
        excluded_handlers=["/metrics"],
    ).instrument(app).expose(app)