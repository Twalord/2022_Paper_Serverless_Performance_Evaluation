FROM python:3.9-bullseye

RUN mkdir app

WORKDIR /app

RUN apt-get update -y

RUN apt-get install -y tzdata

ENV TZ Europe/Berlin

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY Models.py .

COPY TestRunSettings.py .

COPY FunctionDirector.py .

CMD ["FunctionDirector.py"]

ENTRYPOINT ["python3"]