import logging
import logging.config
import time
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette import status

logging.config.fileConfig("./logging.conf")
my_logger = logging.getLogger()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    my_logger.info("START FASTAPI")
    yield
    my_logger.info("STOP FASTAPI")


def create_app() -> FastAPI:
    app = FastAPI(
        title="boilerplate",
        contact={
            "name": "hong",
            "email": "hong@gmail.com",
        },
        lifespan=lifespan,
    )

    return app


app = create_app()


@app.get("/")
async def health_check():
    import traceback

    try:
        1 / 0
    except Exception as e:
        traceback_str = traceback.format_exc()
        my_logger.error(f"\n e: {str(e)}\n traceback_str: {traceback_str}")

    return {"ping": "pong"}


@app.get("/celery")
async def celery_test():
    import traceback

    from .worker.consumer import add

    try:
        print("celery call start")
        result = add.delay(1, 2)
        result.get()
        print("celery call end")
    except Exception:
        traceback_str = traceback.format_exc()
        print(f"e: {traceback_str}")
    return {
        "task_id": result.task_id,
        "is_success": result.successful(),
    }


@app.middleware("http")
async def process_time_handler(request: Request, call_next):
    """요청 처리에 걸리는 시간을 측정"""
    start_time = time.time()  # 요청 처리 측정 시작
    response = await call_next(request)  # 사용자 요청 처리
    processing_time = time.time() - start_time
    my_logger.debug(
        f"{request.method} {request.url}'s PROCESSING TIME >>> {processing_time} SEC"
    )  # 요청 처리에 걸린 시간 출력
    if processing_time >= 1:
        # 슬로우 쿼리 등 개선이 필요한 요청
        my_logger.error(
            f"{request.method} {request.url}'s PROCESSING TIME >>> {processing_time} SEC"
        )
    return response  # 처리 결과 응답 반환


# DTO에서의 에러 처리는 return JSONResponse
@app.exception_handler(ValueError)
async def value_error_handler(request: Request, e: ValueError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": e.args[0]},
    )


# Catch Pydantic ValidationError
# Query Param, Request Body
@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, e: RequestValidationError):
    error = e.errors()[0]
    error_type = error["type"]
    error_loc = error["loc"]
    error_msg = error["msg"]

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": f"type: {error_type}\n location: {error_loc}\n message: {error_msg}"
        },
    )


# 알 수 없는 에러
@app.exception_handler(Exception)
async def unknown_error_handler(request: Request, e: Exception):
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": e.args[0]},
    )
