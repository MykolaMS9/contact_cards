FROM python:3.10

RUN pip install -U pip poetry==1.5.1

WORKDIR /app

COPY poetry.lock pyproject.toml README.md ./

ADD contact_cards ./contact_cards

RUN poetry config virtualenvs.create false \
    && poetry install --no-dev --no-interaction --no-ansi

ENTRYPOINT ["python", "contact_cards/__init__.py"]
