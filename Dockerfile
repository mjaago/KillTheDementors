FROM ubuntu:20.04

RUN apt-get install python
RUN apt-get install pip
RUN pip install poetry

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app

COPY pyproject.toml ./

RUN poetry install --no-root && rm -rf $POETRY_CACHE_DIR

COPY src ./src

ENTRYPOINT ["poetry", "run", "python", "-m", "src.game"]