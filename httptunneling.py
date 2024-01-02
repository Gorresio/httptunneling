# BSD 2-Clause License

# Copyright (c) 2024, Stefano Gorresio

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:

# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.

# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import sys
import time
import socket
import requests
import threading



class HttpTunnelingSocketBase:


    def __init__(self):
        self.send_buffer = b''
        self.recv_buffer = b''
    

    def send(self, data):
        if not type(data) == bytes:
            # stringify data and encode it in utf-8
            data = str(data).encode('utf-8')
        self.send_buffer += data


    def recv(self, size):
        # if recv buffer is empty, wait for data
        # if data is not enough, wait for more data
        while len(self.recv_buffer) < size:
            time.sleep(0.01)
        # get data from recv buffer
        data = self.recv_buffer[:size]
        # remove data from recv buffer
        self.recv_buffer = self.recv_buffer[size:]
        # return data
        return data



class HttpTunnelingSocketClient(HttpTunnelingSocketBase):


    def __init__(self, rhost, rport, polling_delta_time=0.1, ssl=False, uri='/', chunk_size=1024, http_request_timeout=8):
        self.rhost = rhost
        self.rport = rport
        self.polling_delta_time = polling_delta_time
        self.uri = uri
        self.protocol = 'https' if ssl else 'http'
        self.chunk_size = chunk_size
        self.http_request_timeout = http_request_timeout
        super().__init__() # call base class constructor
        threading.Thread(target=self.management_task).start()


    def management_task(self):
        while True:
            # wait for next polling
            time.sleep(self.polling_delta_time)
            # check send buffer
            if self.send_buffer == b'':
                payload = b''
            else:
                # send oldest send buffer chunk
                payload = self.send_buffer[:self.chunk_size]
            # send http request
            try:
                r = requests.post('{}://{}:{}{}'.format(self.protocol, self.rhost, self.rport, self.uri), data=payload, timeout=self.http_request_timeout)
                if r.status_code != 200:
                    raise Exception('')
            except Exception as e:
                # error
                continue
            # ok. remove sent data from send buffer
            self.send_buffer = self.send_buffer[len(payload):]
            # if response contains data, put it in recv buffer
            if not len(r.content) == 0:
                self.recv_buffer += r.content



class HttpTunnelingSocketServer(HttpTunnelingSocketBase):


    def __init__(self, lport, lhost='', polling_delta_time=0.1, chunk_size=1024, http_request_timeout=8):
        self.lport = lport
        self.lhost = lhost
        self.polling_delta_time = polling_delta_time
        self.chunk_size = chunk_size
        self.http_request_timeout = http_request_timeout
        super().__init__() # call base class constructor
        threading.Thread(target=self.management_task).start()


    def management_task(self):
        # create tcp socket server with reuse address option
        sock_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # bind socket to local host and port
        sock_server.bind((self.lhost, self.lport))
        # listen for incoming connections
        sock_server.listen(socket.SOMAXCONN)
        # accept incoming connections
        while True:
            sock_client, addr = sock_server.accept()
            # handle incoming request
            try:
                # receive http request
                sock_client.settimeout(self.http_request_timeout)
                request = sock_client.recv(self.chunk_size + 512) # 512 is the max size that http headers + double newline must have
                # skip http headers starting from first double newline
                payload = request[request.find(b'\r\n\r\n')+4:]
                # check if payload is empty
                if not len(payload) == 0:
                    # send payload to recv buffer
                    self.recv_buffer += payload
                # send as response oldest send buffer chunk, otherwise send empty response
                if self.send_buffer == b'':
                    payload = b''
                else:
                    payload = self.send_buffer[:self.chunk_size]
                # send http response
                sock_client.sendall(b'HTTP/1.1 200 OK\r\n\r\n')
                sock_client.sendall(payload)
                # close connection
                sock_client.close()
            except Exception as e:
                # error
                sock_client.close()
                continue
            # if no error occurred, remove sent data from send buffer
            if not len(payload) == 0:
                self.send_buffer = self.send_buffer[len(payload):]
    
