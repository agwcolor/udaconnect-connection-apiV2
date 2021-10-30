import grpc
import connection_pb2 #reuse these files for client and server
import connection_pb2_grpc
import logging

"""
Sample implementation of a writer that can be used to write messages to gRPC.
"""
print("Sending sample payload...")
logging.basicConfig(level=logging.INFO)
channel = grpc.insecure_channel("localhost:5005", options=(('grpc.enable_http_proxy', 0),))
stub = connection_pb2_grpc.ConnectionServiceStub(channel)

# Update this with desired payload. Create a message and set values ...
item = connection_pb2.ConnectionMessage(
    person_id=5,
    start_date="2020-1-1",
    end_date="2020-12-30",
    meters=5
)
response = stub.GetConnection(item)
print("Greeter client received: " + response.message)
# response = stub.Create(connection)  #pass connection to Create method
# feature = stub.GetFeature(item)
# print(item)
