FROM python:3.12

EXPOSE 80

WORKDIR /code

COPY ./.env /code/.env

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./app /code/app

CMD uvicorn app.main:app --host 0.0.0.0 --port 80 --reload