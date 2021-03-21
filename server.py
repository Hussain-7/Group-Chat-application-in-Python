import socket
import select
from middleware import *
from main import *
import os



class Server:
    def __init__(self,Port):
        self.IP = "127.0.0.1"
        self.PORT = int(Port)
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.IP, self.PORT))
        self.server_socket.listen()
        print(f'Listening for connections on {self.IP}:{self.PORT}...')
        os.system('cls||clear')
        print(f"<--------- Chat for Group : {self.getChatname()} --------->")
        setActivePort(readfromfile())
        self.main()
    def getChatname(self):
        data=readfromfile() 
        return data['groups'][self.PORT]['name']       
    def main(self):
        middleware=Middleware(self.server_socket)
        middleware.groupChat(self.PORT)






        









    