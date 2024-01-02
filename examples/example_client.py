
import httptunneling

# initialize client
client = httptunneling.HttpTunnelingSocketClient('127.0.0.1', 8080)

# send some data to server. send are no blocking
client.send('Hello World!')    # send b'Hello World!'
client.send(3.1416)            # send b'3.1416'
client.send({'a': 1, 'b': 2})  # send b"{'a': 1, 'b': 2}"

# recv are blocking
data = client.recv(32)  # wait until 32 bytes are received