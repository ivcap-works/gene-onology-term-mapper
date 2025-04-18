FROM python:3.10-slim-buster

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN pip install poetry && poetry install --no-root --without dev

COPY . .

RUN chmod +x /app/run.sh

# Command to run
ENTRYPOINT ["/app/run.sh"]
