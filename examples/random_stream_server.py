 # client and server exchange random alphanumeric characters and print them.
 # send and recv are asymmetric, so the printing and the sending must be done in separate threads.

import time
import random
import threading
import httptunneling

# initialize server
server = httptunneling.HttpTunnelingSocketServer(8080)


def send_task(server):
    # send 8 random alphanumeric characters every second
    while True:
        data = ''.join([random.choice('QWERTYUIOPASDFGHJKLZXCVBNM0123456789') for _ in range(8)])
        server.send(data)
        print('sent: ' + data)
        time.sleep(1)


def recv_task(server):
    # receive 8 random alphanumeric and print them (8 for consistency with send_task, but is not necessary)
    while True:
        data = server.recv(8)
        print('recv: ' + str(data))


# start threads
threading.Thread(target=send_task, args=(server,)).start()
threading.Thread(target=recv_task, args=(server,)).start()