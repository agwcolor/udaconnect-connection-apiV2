FROM python:3.7.2

WORKDIR .
COPY . .
RUN python -m pip install --upgrade pip
RUN python -m pip install -r requirements.txt
RUN python -m grpc_tools.protoc -I./ --python_out=./ --grpc_python_out=./ connection.proto

EXPOSE 50051
ENTRYPOINT [ "python", "controllers.py" ]