import socket
import sys
import select
import errno
import os
import threading
import signal
import msvcrt


# import continuous_threading

import sys

clear = lambda: os.system('cls')


class Client:
    def __init__(self,port,id):
        self.HEADER_LENGTH = 10
        IP = "127.0.0.1"
        PORT = port
        unicastid=id
        self.my_username= input("Username: ")

        # Create a socket socket.AF_INET - address family, IPv4, some otehr possible are AF_INET6, AF_BLUETOOTH,
        # AF_UNIX socket.SOCK_STREAM - TCP, conection-based, socket.SOCK_DGRAM - UDP, connectionless, datagrams,
        # socket.SOCK_RAW - raw IP packets
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Connect to a given ip and port
        self.client_socket.connect((IP, PORT))

        # Set connection to non-blocking state, so .recv() call won;t block, just return some exception we'll handle
        self.client_socket.setblocking(False)
        self.t = threading.Thread(target=self.send_message)
        self.signalval=False
        self.message=""
        # Prepare username and header and send them We need to encode username to bytes, then count number of bytes and
        # prepare header of fixed size, that we encode to bytes as well
        self.username = self.my_username.encode('utf-8')
        self.detail=str({'username':self.username,'id':unicastid}).encode('utf-8')
        self.username_header = f"{len(self.detail):<{self.HEADER_LENGTH}}".encode('utf-8')
        self.client_socket.send(self.username_header + self.detail)
        self.recieve_message()
    def getmessage(self):
        return self.message
    def send_message(self):
        while(True):
            # Wait for user to input a message
            if not self.signalval:
                try:
                    self.message=input(f'\r{self.my_username} > ')
                except Exception as e:
                    # Any other exception - something happened, exit
                    sys.exit()
                # If message is not empty - send it
                if self.message == '^C':
                    break
                if self.signalval==True:
                    break
                if self.message:
                    # Encode message to bytes, prepare header and convert to bytes, like for username above, then send
                    if self.client_socket:
                        self.message = str({"message":self.message}).encode('utf-8')
                        message_header = f"{len(self.message):<{self.HEADER_LENGTH}}".encode('utf-8')
                        self.client_socket.send(message_header + self.message)
            
    
    def signal_handler(self,sig, frame):
        # print("Client Exiting")
        # self.signalval=True
        self.signalval=True
        self.client_socket.close()
        print("\nExit signal from client\nClosing Connection!!!")
   
    def recieve_message(self):
        signal.signal(signal.SIGINT, self.signal_handler)
        while True:
                check = self.t.is_alive()
                if not check and (not self.signalval):  
                    print("[starting send message thread]")
                    self.t.start()
                if self.signalval:
                    break;
                try:
                    # Now we want to loop over received messages (there might be more than one) and print them
                    while True:

                        # Receive our "header" containing username length, it's size is defined and constant
                        username_header = self.client_socket.recv(self.HEADER_LENGTH)
                        # If we received no data, server gracefully closed a connection, for example using socket.close() or
                        # socket.shutdown(socket.SHUT_RDWR)
                        if not len(username_header):
                            print('Connection closed by the server')
                            sys.exit()
                        
                        if self.signalval:
                             print('Connection closed by the Client')
                             sys.exit()
                        # Convert header to int value
                        username_length = int(username_header.decode('utf-8').strip())
                        # Receive and decode username
                        username = self.client_socket.recv(username_length).decode('utf-8')

                        # Now do the same for message (as we received username, we received whole message, there's no need to
                        # check if it has any length)
                        message_header = self.client_socket.recv(self.HEADER_LENGTH)
                        message_length = int(message_header.decode('utf-8').strip())
                        message = self.client_socket.recv(message_length).decode('utf-8')

                        


                        # Print message                    
                        print ("\033                                     \033",end='')
                        message=message +'\t\t\t'
                        print(f'\r{username} > {message}')
                        print(f'\r{self.my_username } > ',end='')

                except IOError as e:
                    # This is normal on non blocking connections - when there are no incoming data error is going to be raised
                    # Some operating systems will indicate that using AGAIN, and some using WOULDBLOCK error code
                    # We are going to check for both - if one of them - that's expected, means no incoming data, continue as normal
                    # If we got different error code - something happened
                    if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                        print('Reading error: {}'.format(str(e)))
                        sys.exit()

                    # We just did not receive anything
                    continue

                except Exception as e:
                    # Any other exception - something happened, exit
                    print('Reading error: '.format(str(e)))
                    sys.exit()
