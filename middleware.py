from os import read
import socket
import select
from main import *
class Middleware:
    def __init__(self,server_socket):
        self.clients = {}
        self.sockets_list = []
        self.sockets_list.append(server_socket)
        self.HEADER_LENGTH = 10
        self.server_socket=server_socket
    # Handles message receiving

    def receive_message(self,client_socket):
        try:
            # Receive our "header" containing message length, it's size is defined and constant
            message_header = client_socket.recv(self.HEADER_LENGTH)
            # If we received no data, client gracefully closed a connection, for example using socket.close() or
            # socket.shutdown(socket.SHUT_RDWR)1
            if not len(message_header):
                return False
            # Convert header to int value
            message_length = int(message_header.decode('utf-8').strip())
            # Return an object of message header and message data
            message=client_socket.recv(message_length)
            message=eval(message.decode('utf-8'))
            return {'header': message_header, 'data':message}

        except:

            # If we are here, client closed connection violently, for example by pressing ctrl+c on his script or just
            # lost his connection socket.close() also invokes socket.shutdown(socket.SHUT_RDWR) what sends information
            # about closing the socket (shutdown read/write) and that's also a cause when we receive an empty message
            print("Exception occurring errro!!!!!!!!!!!!!!!!!")
            return False

   

    def groupChat(self,GroupId):
        while True:

            read_sockets, _, exception_sockets = select.select(self.sockets_list, [], self.sockets_list)
            # Iterate over notified sockets
            for notified_socket in read_sockets:

                # If notified socket is a server socket - new connection, accept it
                if notified_socket == self.server_socket:

                    # Accept new connection
                    # That gives us new socket - client socket, connected to this given client only, it's unique for that client
                    # The other returned object is ip/port set
                    client_socket, client_address = self.server_socket.accept()
                    # Client should send his name right away, receive it
                    user = self.receive_message(client_socket)
                    # If False - client disconnected before he sent his nam
                    if user is False:
                        continue
                
                    # Add accepted socket to select.select() list
                    
                    self.sockets_list.append(client_socket)

                    # Also save username and username header
                    data=readfromfile()
                    id=data['clientId']
                    data['activeclients'][id]={}
                    data['activeclients'][id]['name']=user['data']['username'].decode('UTF-8')
                    data['activeclients'][id]['address']=client_address
                    data['activeclients'][id]['GroupId']=GroupId
                    data['clientId']+=1
                    writeinfile(data)
                    self.clients[client_socket] = {'user':user,'address':client_address}
                    # print(self.clients)
                    print('[Accepted new connection from {}:{}]'.format(*client_address))
                    print("[{} joined the chat!!]". format((user['data']['username'].decode('utf-8'))))

                # Else existing socket is sending a message
                else:

                    # Receive message
                    message = self.receive_message(notified_socket)

                    # If False, client disconnected, cleanup
                    if message is False:
                        print('[{} left the chat!!]'.format(self.clients[notified_socket]['user']['data']['username'].decode('utf-8')))

                        # Remove from list for socket.socket()
                        self.sockets_list.remove(notified_socket)

                        # Remove from our list of users
                        
                        readdata=readfromfile()
                        for key in list(readdata['activeclients']):
                            if (readdata['activeclients'][key]['address']==self.clients[notified_socket]["address"]):
                                del readdata['activeclients'][key]
                        del self.clients[notified_socket]
                        # print(readdata)
                        writeinfile(readdata)
                        continue

                    # Get user by notified socket, so we will know who sent the message
                    user = self.clients[notified_socket]['user']

                    print(f'{user["data"]["username"].decode("utf-8")} > {message["data"]["message"]}')

                    # Iterate over connected clients and broadcast message
                    if(int(user["data"]["id"])==-1):# meaning broadcast to everyclient connected in groupchat
                     for client_socket in self.clients:
                            # But don't sent it to sender
                            if client_socket != notified_socket:
                                # Send user and message (both with their headers) We are reusing here message header sent by
                                # sender, and saved username header send by user when he connected
                                client_socket.send("{:<10}".format(str(len(user['data']['username']))).encode('utf-8') + user['data']['username'] + "{:<10}".format(str(len(message['data']['message']))).encode('utf-8') + message['data']['message'].encode('utf-8'))
                    else:
                        reciever_address=readfromfile()
                        for client_socket in self.clients:
                            if client_socket != notified_socket:
                                if(self.clients[client_socket]["address"]==reciever_address['activeclients'][user["data"]["id"]]['address']):
                                    client_socket.send("{:<10}".format(str(len(user['data']['username']))).encode('utf-8') + user['data']['username'] + "{:<10}".format(str(len(message['data']['message']))).encode('utf-8') + message['data']['message'].encode('utf-8'))

                            

            # It's not really necessary to have this, but will handle some socket exceptions just in case
            for notified_socket in exception_sockets:
                # Remove from list for socket.socket()
                self.sockets_list.remove(notified_socket)

                # Remove from our list of users
                del self.clients[notified_socket]
