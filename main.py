from server import *
from client import *
import pickle
import os.path
import os

import socket, errno

def setActivePort(data):
    for key in data['groups']:
        # print(f"Group Id : {key} - Group Name : {data['groups'][key]['name']} - Active : {data['groups'][key]['active']}")     
        port=key
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.bind(("127.0.0.1",int(port)))
            data['groups'][key]['active']=False
        except socket.error as e:
            if e.errno == errno.EADDRINUSE:
                data['groups'][key]['active']=True
            else:
                # something else raised the socket.error exception
                print(e)
        s.close()    
    writeinfile(data)

def readfromfile():
    rdata=""
    currentdir=os.getcwd()
    currentdir=currentdir+'\data.pkl'
    file = open(currentdir, 'rb')
    while True:
        try:
            rdata=pickle.load(file);
        except EOFError:
            break
    return rdata

def writeinfile(data):
     currentdir=os.getcwd()
     currentdir=currentdir+'\data.pkl'
     file = open(currentdir, 'wb')
     pickle.dump(data,file)                  
     file.close()


def main():
   rdata=""
   data = {'GroupId':1234,'groups': {},'activeclients':{},'clientId':0}
   currentdir=os.getcwd()
   currentdir=currentdir+'\data.pkl'
   if os.path.isfile(currentdir) is False:
      writeinfile(data)
   setActivePort(readfromfile())
   
   command=""
   while(True): 
        print("\n<--------------- Chat Application Menu -------->\n\n1 : Create New Group(server)\n2 : Host Existing Group(server)\n3 : Join Group(client)\n4 : To delete a Group\n5 : for Exit\n")
        command=input("Enter Command: ")
        if command=="1":
            rdata=readfromfile()
            name=input("Enter Group Name : ")
            rdata['GroupId']+=1
            id=rdata['GroupId']
            rdata['groups'][id]={}
            rdata['groups'][id]['name']=name
            rdata['groups'][id]['active']=True
            writeinfile(rdata)
            Server(id)

        if command == "2":
            rdata=readfromfile()
            setActivePort(rdata)
            index=1
            groups=[]
            print("\nAvailable Chat Groups: ",end='')
            i=0
            for key in rdata['groups']:
                if rdata['groups'][key]['active'] is False:
                    if(i==0):
                        print(f"\n\n{index}) Group Id : {key} - Group Name : {rdata['groups'][key]['name']}")
                        i+=1
                    else:
                        print(f"{index}) Group Id : {key} - Group Name : {rdata['groups'][key]['name']}")  
                    groups.append(key)
                    index+=1  
            if groups == []:
                print("\rNo Active Groups to join!!!")
                continue
            while(True):
                port = input("\nEnter a valid GroupId of group you want to host : ")
                if int(port) in groups:
                    break
            Server(port)

        if command =="3":
            rdata=readfromfile()
            index=1
            groups=[]
            print("\nAvailable Chat Groups:",end='')
            i=0
            for key in rdata['groups']:
                if rdata['groups'][key]['active'] is True:
                    if(i==0):
                        print(f"\n\n{index}) Group Id : {key} - Group Name : {rdata['groups'][key]['name']}")
                        i+=1
                    else:
                        print(f"{index}) Group Id : {key} - Group Name : {rdata['groups'][key]['name']}")
                        
                    groups.append(key)
                    index+=1          
            if groups == []:
                print("\rNo Active Groups to join!!!")
                continue
            while(True):
                port = input("\nEnter a valid GroupId of group you want to join : ")
                if int(port) in groups:
                    break
            command=input("Press 1 : To allow all group member to see messages\nPress 2 : To unicast to someone specific\ncommand : ")
            if(int(command)==1):
                Client(int(port),int(-1))
            if(int(command)==2):
                rdata=readfromfile()
                if(rdata['activeclients']=={}):
                    print("No other active client!!!")
                    continue
                activemembers=[]
                print('<-------Active Clients------>')
                if(rdata['clientId']!=0):
                    for key in rdata['activeclients']:
                        print(f"id : {key} - Name : {rdata['activeclients'][key]['name']}")
                        activemembers.append([])
                print("\nEnter client id you want to unicast to:\n")
                id=input("Enter id:")
                Client(int(port),int(id))
            else:
                continue
        if command == "4" :
            rdata=readfromfile()
            # print(rdata)
            index=1
            groups=[]
            print("\nAvailable Chat Groups:\n")
            for key in rdata['groups']:
                if rdata['groups'][key]['active'] is False:
                    print(f"{index}) Group Id : {key} - Group Name : {rdata['groups'][key]['name']}")
                    groups.append(key)
                    index+=1          
            if groups == []:
                print("No Active Groups to join!!!")
                continue
            port=0
            while(True and int(port) != -1):
                port = input("\nEnter a valid GroupId of group you want to delete : ")
                if int(port) in groups:
                    del rdata['groups'][int(port)]
                    writeinfile(rdata)
                    break
        if  command == "5":
            break
        else:
            continue
   

if __name__ == "__main__":
    main()
    print("Exiting Chat application!!!!")
    