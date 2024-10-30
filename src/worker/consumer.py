from datetime import timedelta

from celery import Celery

app = Celery(
    "worker",
    include=["src.worker.tasks"],
)
app.config_from_object("src.worker.celery_config")

app.conf.task_default_rate_limit = "5/m"

app.conf.broker_transport_options = {
    "priority_steps": list(range(3)),
    "sep": ":",
    "queue_order_strategy": "priority",
}

# app.autodiscover_tasks()


app.conf.beat_schedule = {
    "add-every-5-seconds": {
        "task": "src.worker.tasks.add",
        "schedule": timedelta(seconds=5),
        "args": (5, 5),
        "options": {
            "queue": "celery",
        },
    },
    "add-every-7-seconds": {
        "task": "src.worker.tasks.add",
        "schedule": timedelta(seconds=7),
        "args": (7, 7),
        "options": {
            "queue": "celery:1",
        },
    },
    "add-every-9-seconds": {
        "task": "src.worker.tasks.add",
        "schedule": timedelta(seconds=9),
        "args": (9, 9),
        "options": {
            "queue": "celery:2",
        },
    },
}


@app.task(queue="celery:1")
def add(x, y):
    print(f"call celery: {(x, y)}")
    return x + y
