from .consumer import app


@app.task
def add(x, y):
    print(f"call batch celery: {(x, y)}")
    return x + y
