from celery import Celery
from .setting import settings

app = Celery(
    "oj-salve",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["src.backend.runners"],
)
class CeleryConfig:
    task_serializer = "pickle"
    result_serializer = "pickle"
    event_serializer = "json"
    accept_content = ["application/json", "application/x-python-serialize"]
    result_accept_content = ["application/json", "application/x-python-serialize"]


app.config_from_object(CeleryConfig)