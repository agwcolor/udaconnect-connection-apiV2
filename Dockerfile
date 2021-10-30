FROM python:3.8

WORKDIR .

RUN apt-get update
COPY requirements.txt requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

EXPOSE 5002

COPY . .
CMD ["flask", "run", "--host", "0.0.0.0"]