import logging
import grpc
import time
from datetime import datetime
from concurrent import futures
from schemas import ConnectionSchema
from services import ConnectionService
from typing import Optional, List
from connection_pb2 import ConnectionResponse
import connection_pb2
import connection_pb2_grpc
from grpc_reflection.v1alpha import reflection

DATE_FORMAT = "%Y-%m-%d"

logging.basicConfig(level=logging.INFO)

class ConnectionDataResource(connection_pb2_grpc.ConnectionServiceServicer):
    # @responds(schema=ConnectionSchema, many=True)
    def GetConnection(self, request, context):
        person_id = request.person_id
        start_date = datetime.strptime(
            request.start_date, DATE_FORMAT)
        end_date = datetime.strptime(request.end_date, DATE_FORMAT)
        distance = request.meters
        print("person_id:", type(person_id),"\n",
              "start_date:", type(start_date),"\n",
              "end_date:", type(end_date), "\n",
              "distance:", type(distance), "\n")
        results = ConnectionService.find_contacts(
            person_id=person_id,
            start_date=start_date,
            end_date=end_date,
            meters=distance,
        )

        print("Hello there")
        # result = connection_pb2.ConnectionMessageList()
        # result.connections.extend(results)
        # results = request.person_id
        print(result, "These are the results returned from gRPC call \
            to ConnectionService")
        return ConnectionResponse(connections=results)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=2))
    connection_serve = ConnectionDataResource()
    connection_pb2_grpc.add_ConnectionServiceServicer_to_server(ConnectionDataResource(), server)
    SERVICE_NAMES = (
        connection_pb2.DESCRIPTOR.services_by_name['ConnectionService'].full_name,
        reflection.SERVICE_NAME,
    )
    reflection.enable_server_reflection(SERVICE_NAMES, server)
    logging.log(logging.INFO, 'gRPC server starting on port 5005.')
    server.add_insecure_port("[::]:5005")
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    serve()

'''
////// Dummy Data


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
