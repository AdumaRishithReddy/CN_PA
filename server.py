import socket
import _thread
import cv2
import pickle
import struct
import time
import imutils
import os 
import queue
import base64
BUFF_SIZE=65535
q = queue.Queue()


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

videos_avail=['Mountain','valley','space']

# vid = cv2.VideoCapture('medium.mp4')
# fps = vid.get(cv2.CAP_PROP_FPS)
# delay = int(1000 / fps)

def generate_video(client,ind):
    vid_file=ind
    print(vid_file)
    # global vid
    vid_l= cv2.VideoCapture(vid_file+"_low.mp4")
    vid_m=cv2.VideoCapture(vid_file+"_med.mp4")
    vid_h=cv2.VideoCapture(vid_file+"_high.mp4")
    total_frames = int(vid_m.get(cv2.CAP_PROP_FRAME_COUNT))
    # if vid is None:
    #     print("No file")
    fps = vid_l.get(cv2.CAP_PROP_FPS)
    # global delay
    delay = int(1000 / fps)
    WIDTH=400
    count=0
    while True:
    # Capture the video frame by frame
        if count<=total_frames/3:
            vid=vid_l
        elif count<=2*total_frames/3 and count>total_frames/3:
            vid=vid_m
            vid.set(cv2.CAP_PROP_POS_FRAMES, count-1)
        else:
            vid=vid_h
            vid.set(cv2.CAP_PROP_POS_FRAMES, count-1)
        ret, frame = vid.read()
        if not ret:
            print("Can't receive frame (stream end?). Exiting ...")
            break
        count+=1
        # Display the resulting frame
        cv2.imshow('Sending', frame)
        data = pickle.dumps(frame, 0)
        size = len(data)
        message_size = struct.pack("L", len(data)) ### CHANGED


# Then data
        client.sendall(message_size + data)
        q.put(frame)

        # Wait for the appropriate time or until 'q' is pressed
        if cv2.waitKey(delay) & 0xFF == ord('q'):
            break
    end_signal = b'vid_end'
    end_message = pickle.dumps(end_signal)  # Pickle the end signal for consistency
    end_message_size = struct.pack("L", len(end_message))  # Pack the size as done with frames
    client.sendall(end_message_size + end_message)  # Send the end signal

    cv2.destroyAllWindows()
    
    print('Player closed')
    BREAK=True
    # vid.release()

def vid_stream(client):
    # client.sendall(fps)
    while True:
        if not q.empty:
            f=q.get()
            print("Recieved frame")
            cv2.imshow('frame', f)
            if cv2.waitKey(delay) & 0xFF == ord('q'):
                break
            # result, f = cv2.imencode('.jpg', f)
            data = pickle.dumps(f, 0)
            size = len(data)
            message_size = struct.pack("L", len(data)) ### CHANGED

    # Then data
            client.sendall(message_size + data)


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
 
    r1=c.recv(1024).decode()
    print(r1)
    m2="Enter your public key: "
    pk=c.recv(1024).decode()
    print(pk)
    mapping[r1]=pk

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
            for i in videos_avail:
                print(i)
                a='vida:'+i
                c.sendall(a.encode())
            time.sleep(0.1)
            c.sendall("end_list".encode())
            print("AS")
            choice=c.recv(1024).decode()
            print(choice)
            c.sendall("vid:".encode())
            generate_video(c,choice)
            # c.sendall("vid_end".encode())
            # _thread.start_new_thread(generate_video,(c,))
            # _thread.start_new_thread(vid_stream,(c,))
            # vid_stream(c)
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