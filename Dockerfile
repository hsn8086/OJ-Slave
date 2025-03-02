FROM python:3.13
LABEL authors="hsn"

# Install Poetry
RUN pip3.13 install poetry 

WORKDIR /app

COPY ./pyproject.toml /app/pyproject.toml
COPY ./poetry.lock /app/poetry.lock

RUN poetry install --no-root

COPY ./src /app/src
ENTRYPOINT ["poetry", "run", "uvicorn", "src.main:app", "--host","0.0.0.0","--port","8000"]
