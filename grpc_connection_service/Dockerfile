FROM python:3.7.2

WORKDIR .
COPY . .
RUN python -m pip install --upgrade pip
RUN python -m pip install -r requirements.txt
RUN python -m grpc_tools.protoc -I./ --python_out=./ --grpc_python_out=./ connection.proto


ENV DB_USERNAME=postgres
ENV DB_PASSWORD=d293aW1zb3NlY3VyZQ==
ENV DB_NAME=geoconnections
ENV DB_HOST=postgres
ENV DB_PORT=5432


EXPOSE 5005
ENTRYPOINT [ "python", "controllers.py" ]