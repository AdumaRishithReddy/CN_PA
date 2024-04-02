import socket
import _thread
import cv2
import pickle
import struct


LOCALHOST = "127.0.0.1"
PORT = 8080
# calling server socket method
s = socket.socket(socket.AF_INET,
                       socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(('', PORT))        # Bind to the port
s.listen(5)  
mapping={}
clients=[]

def vid_stream(client):
    with open('tiny.mp4', 'rb') as video_file:
        while True:
            video_chunk = video_file.read(1024)
            if not video_chunk:
                break
            client.sendall(video_chunk)

def broadcast_dictionary(exclude_socket=None):
    """Broadcasts the updated dictionary to all clients except the sender."""
    message = "UPDATE_DICT:"
    for client_name, client_key in mapping.items():
        message += f"{client_name}:{client_key},"
    for client in clients:
        if client != exclude_socket:
            try:
                client.sendall(message[:-1].encode())  # Remove the last comma
            except:
                client.close()
                if client in clients:
                    clients.remove(client)

def on_new_client(c,addr):
    m1="Enter your Name: "
    c.sendall(m1.encode())
    r1=c.recv(1024).decode()
    print(r1)
    m2="Enter your public key: "
    c.sendall(m2.encode())
    pk=c.recv(1024).decode()
    print(pk)
    mapping[r1]=pk
    # new_client_notification = f"NEW_CLIENT:{r1}:{pk}"
    
    # for client_name, client_key in mapping.items():
    #         if client_name != r1:  # Do not send the message back to the sender
    #             c.sendall(r1.encode())
    #             c.sendall(pk.encode())
    broadcast_dictionary(exclude_socket=None)
    
    a=True
    while a:
        
        r=c.recv(1024).decode()
        msg=''
        # print(r)
        if r=='QUIT':
            print("Done and quiting")
            msg=msg+r1+" is exiting the connection"
            # broadcast_message(msg)
            a=False
            for client in clients:
                if client != c:
                    print("Sending")
                    client.sendall(msg.encode())
                if client ==c :
                    client.sendall("sent".encode())
            print("Sent msg: ",msg)
        elif r=='Msg':
            m1=c.recv(1024).decode()
            print("Here")
            msg=msg+m1
            msg="Enc:"+msg
            for client in clients:
                if client != c:
                    print("Sending")
                    client.sendall(msg.encode())
                if client ==c :
                    client.sendall("sent".encode())
            print("Sent msg: ",msg)
            # for client_name, client_key in mapping.items():
            #     if client_name != r1:  # Do not send the message back to the sender
            #         c.sendall(msg.encode())
        elif r=='vid':
            print(r)
            c.sendall("vid:".encode())
            vid_stream(c)
        else:
            msg=msg+r
        # for client_name, client_key in mapping.items():
        #     if client_name != r1:  # Do not send the message back to the sender
        #         c.sendall(msg.encode())
        
    del mapping[r1]
    clients.remove(c) 
    broadcast_dictionary(exclude_socket=c)
    print("Closing connection")
    c.close()
    return


while True:
   c, addr = s.accept() 
   clients.append(c) 
#    users.append()    # Establish connection with client.
   print ('Got connection from', addr)
#    print(mapping)
   _thread.start_new_thread(on_new_client,(c,addr))
   
s.close()