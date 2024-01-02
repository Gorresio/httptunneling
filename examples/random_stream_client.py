 # client and server exchange random alphanumeric characters and print them.
 # send and recv are asymmetric, so the printing and the sending must be done in separate threads.

import time
import random
import threading
import httptunneling

# initialize client
client = httptunneling.HttpTunnelingSocketClient('127.0.0.1', 8080)


def send_task(client):
    # send 8 random alphanumeric characters every second
    while True:
        data = ''.join([random.choice('QWERTYUIOPASDFGHJKLZXCVBNM0123456789') for _ in range(8)])
        client.send(data)
        print('sent: ' + data)
        time.sleep(1)


def recv_task(client):
    # receive 8 random alphanumeric and print them (8 for consistency with send_task, but is not necessary)
    while True:
        data = client.recv(8)
        print('recv: ' + str(data))


# start threads
threading.Thread(target=send_task, args=(client,)).start()
threading.Thread(target=recv_task, args=(client,)).start()