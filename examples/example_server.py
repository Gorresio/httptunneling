
import httptunneling

# initialize server
server = httptunneling.HttpTunnelingSocketServer(8080)

# send are no blocking
server.send('Hello!')    # send b'Hello World!'

# recv are blocking
data = server.recv(34) # wait until 34 bytes are received
print(data)            # print b"Hello World!3.1416{'a': 1, 'b': 2}"