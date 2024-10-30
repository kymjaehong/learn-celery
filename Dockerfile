FROM python:3.12.1

# .pyc 파일을 생성하지 않도록 설정합니다.
ENV PYTHONDONTWRITEBYTECODE=1
# 출력 스트림(표준 출력 및 표준 에러 스트림)을 버퍼링하지 않고, 실시간으로 터미널에 출력되도록 설정합니다.
ENV PYTHONUNBUFFERED=1

# ARG DEV=false

COPY ./logging.conf /app/
COPY ./requirements.txt /app/
COPY ./src /app/src/
COPY ./logs /app/logs/

WORKDIR /app

RUN pip install -r ./requirements.txt

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0"]