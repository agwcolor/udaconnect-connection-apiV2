import sys, os
# sys.path.append('/path/to/2014_07_13_test')
basedir = os.path.abspath(os.path.dirname(__file__))

from datetime import datetime
import time
from concurrent import futures
from app.services import ConnectionService
from typing import Optional, List

import grpc
from . import grpc_server
from . import connection_pb2
from . import connection_pb2_grpc
import logging
from grpc_reflection.v1alpha import reflection
import sys

print(basedir, " is the path")


DATE_FORMAT = "%Y-%m-%d"

# api = Namespace("UdaConnect", description="Connections via geolocation.")
# noqa
logging.basicConfig(level=logging.INFO)

class ConnectionDataResource(connection_pb2_grpc.ConnectionServiceServicer):
    def GetConnection(self, request, context):

        person_id=request.person_id
        start_date=datetime.strptime(
            request.start_date, DATE_FORMAT)
        end_date=datetime.strptime(request.end_date, DATE_FORMAT)
        meters=request.meters

        results = ConnectionService.find_contacts(
            person_id=person_id,
            start_date=start_date,
            end_date=end_date,
            meters=meters,
        )
        '''
        item_1 = connection_pb2.ConnectionMessage(
            person_id=5,
            start_date="2020-1-1",
            end_date="2020-12-30",
            meters=5
        )

        item_2 = connection_pb2.ConnectionMessage(
            person_id=5,
            start_date="2020-1-1",
            end_date="2020-12-30",
            meters=5
        )
        
        item_3 = connection_pb2.ConnectionMessage(
            person_id=5,
            start_date="2020-1-1",
            end_date="2020-12-30",
            meters=5
        )
        '''
        print("Hello there")
        result = connection_pb2.ConnectionMessageList()
        result.connections.extend(results)
        # results = request.person_id
        print(result, "These are the results returned from gRPC call to ConnectionService")
        return result


grpc_server.serve()
'''
# Initialize gRPC server
def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=2))
    connection_pb2_grpc.add_ConnectionServiceServicer_to_server(ConnectionDataResource(), server)

    print("Server starting on port 5005...")
    SERVICE_NAMES = (
        connection_pb2.DESCRIPTOR.services_by_name['ConnectionService'].full_name,
        reflection.SERVICE_NAME,
    )
    reflection.enable_server_reflection(SERVICE_NAMES, server)

    server.add_insecure_port("[::]:5005")
    server.start()
    # Keep thread alive
    server.wait_for_termination()

serve()
'''