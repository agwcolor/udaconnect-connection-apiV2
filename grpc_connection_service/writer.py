import grpc
import connection_pb2 #reuse these files for client and server
import connection_pb2_grpc

print("Sending sample payload...")

# NOTE : The channel ip configured this way assumes that you are testing the grpc server from outside of the kubernetes cluster. Otherwise a deployed client channel ip would use the ip of the grpc service which on this cluster is: 10.43.255.199:5005.

channel = grpc.insecure_channel("localhost:30003", options=(('grpc.enable_http_proxy', 0),))
connections_client = connection_pb2_grpc.ConnectionServiceStub(channel)

# Update this with desired payload. Create a message and set values ...
item = connection_pb2.ConnectionMessage(
    person_id=5,
    start_date="2020-1-1",
    end_date="2020-12-30",
    meters=5,
)
connections_response = connections_client.GetConnection(item)
print("Greeter client received: ... ")
print(connections_response.connections)