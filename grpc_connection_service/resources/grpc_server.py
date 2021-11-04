
import grpc
import logging
from concurrent import futures
import app.connection_pb2 as connection_pb2
import app.connection_pb2_grpc as connection_pb2_grpc
from app.controllers import ConnectionDataResource
from grpc_reflection.v1alpha import reflection

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=2))
    connection_serve = ConnectionDataResource()
    connection_pb2_grpc.add_ConnectionServiceServicer_to_server(connection_serve, server)
    SERVICE_NAMES = (
        connection_pb2.DESCRIPTOR.services_by_name['ConnectionService'].full_name,
        reflection.SERVICE_NAME,
    )
    reflection.enable_server_reflection(SERVICE_NAMES, server)
    logging.log(logging.INFO, 'gRPC server starting on port 5005.')
    server.add_insecure_port("[::]:5005")
    server.start()
    server.wait_for_termination()
'''

if __name__ == '__main__':
    serve()
'''