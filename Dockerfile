# Builder stage
FROM python:3.11-slim as builder

ENV DEBIAN_FRONTEND noninteractive

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y gcc python3-dev
COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache pip wheel --no-deps --wheel-dir /usr/src/app/wheels -r requirements.txt


# App stage
FROM python:3.11-slim as app

ENV DEBIAN_FRONTEND noninteractive

WORKDIR /app

RUN apt-get update && apt-get install -y locales && rm -rf /var/lib/apt/lists/* \
	&& localedef -i ru_RU -c -f UTF-8 -A /usr/share/locale/locale.alias ru_RU.UTF-8
ENV LANG ru_RU.UTF-8
RUN apt-get update && apt-get install -y mc && rm -rf /var/lib/apt/lists/*

COPY --from=builder /app /app

COPY app app
COPY run.py run.py
COPY message_models message_models

COPY --from=builder /usr/src/app/wheels /wheels
RUN --mount=type=cache,target=/root/.cache pip install /wheels/*

ENTRYPOINT ["python", "run.py"]
