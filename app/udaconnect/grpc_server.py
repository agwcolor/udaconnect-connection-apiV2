
import grpc
import logging
from concurrent import futures
from . import connection_pb2
from . import connection_pb2_grpc
from app.udaconnect.controllers import ConnectionDataResource
from grpc_reflection.v1alpha import reflection

with app.app_context():
    def serve():
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=2))
        connection_pb2_grpc.add_ConnectionServiceServicer_to_server(ConnectionDataResource(), server)
        logging.log(logging.INFO, 'gRPC server starting on port 5005.')
        server.add_insecure_port("[::]:5005")
        server.start()
        server.wait_for_termination()
        
    if __name__ == '__main__':
        serve()