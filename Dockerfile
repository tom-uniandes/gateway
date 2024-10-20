FROM python:3.9

WORKDIR /app

COPY . /app

RUN pip install pipenv && pipenv install

EXPOSE 5000

ENTRYPOINT ["pipenv", "run", "python", "app.py"]