
import grpc
import logging
from concurrent import futures
from . import connection_pb2
from . import connection_pb2_grpc
from . controllers import ConnectionDataResource
from grpc_reflection.v1alpha import reflection

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=2))
    connection_serve = ConnectionDataResource()
    connection_pb2_grpc.add_ConnectionServiceServicer_to_server(connection_serve, server)
    logging.log(logging.INFO, 'gRPC server starting on port 5005.')
    server.add_insecure_port("[::]:5005")
    server.start()
    server.wait_for_termination()
        
if __name__ == '__main__':
    serve()