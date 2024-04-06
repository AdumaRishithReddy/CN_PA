# client.py
import socket
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import numpy as np
import base64
import threading
import os
import time
import pickle
import cv2
import struct
import queue
BUFF_SIZE=65535

frame_queue= queue.Queue()


SERVER = "127.0.0.1"
PORT = 8080

def decrypt_and_print(encrypted_msg):
    try:
        cipher = PKCS1_OAEP.new(private_key)
        decrypted_msg = cipher.decrypt(base64.b64decode(encrypted_msg)).decode()
        print("Decrypted message:", decrypted_msg)
    except Exception as e:
        print("Error decrypting message:", e)

def display_video():
    while True:
        if not frame_queue.empty():
            frame = frame_queue.get()
            cv2.imshow('Received Video', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        else:
            # print(frame_queue.qsize())
            # print("Buffer is empty. Waiting for frames...")
            # If you want to close the window automatically when there are no more frames,
            # you can check for some condition to break this loop.
            # For example, if a 'streaming_stopped' flag is True, then break.
            pass
    cv2.destroyAllWindows()


def receive_message():
    while True:
        try:
            msg = client.recv(1024).decode()
            if msg.startswith("UPDATE_DICT:"):
                new_mapping = {}
                _, dict_str = msg.split(":", 1)
                for item in dict_str.split(","):
                    name, key = item.split(":")
                    new_mapping[name] = key
                global mapping
                mapping = new_mapping
                print("Updated client list received.")
            elif msg.startswith("Enc:"):
                encrypted_msg = msg[len("Enc:"):]
                decrypt_and_print(encrypted_msg)
                # pass
            elif msg.startswith("vid:"):
                ##################################
                # while True:
                #     # First, receive the size of the frame
                #     frame_size_data = client.recv(8)  # Assuming the size is sent in 8 bytes
                #     if len(frame_size_data) < 8:
                #         print("Failed to receive proper frame size data.")
                #         break
                #     frame_size = struct.unpack('Q', frame_size_data)[0]

                #     # Then, receive the frame data based on the size
                #     frame_data = b''
                #     while len(frame_data) < frame_size:
                #         frame_data += client.recv(1024)

                #     frame = pickle.loads(frame_data)
                #     cv2.imshow('Received Video', frame)
                #     if cv2.waitKey(1) & 0xFF == ord('q'):
                #         break
                ####################################
                # data = client.recv(1024)
                # frame_data = data
                # try:
                #     frame = pickle.loads(frame_data)
                #     frame_queue.put(frame)  # Put the frame into the queue
                # except Exception as e:
                #     print("Failed to load frame:", e)   
                ######################################
                # print("Hello")
                # data = b''
                # payload_size = 8  # Assuming 8 bytes for size indication

                # while True:
                #     while len(data) < payload_size:
                #         data += client.recv(4096)
                #     frame_size = int.from_bytes(data[:payload_size], byteorder='big')
                #     data = data[payload_size:]
                #     while len(data) < frame_size:
                #         data += client.recv(4096)
                #     frame_data = data[:frame_size]
                #     data = data[frame_size:]
                #     frame = pickle.loads(frame_data)
                #     print("Recieved 1 frame")
                #     frame_queue.put(frame)
                    # cv2.imshow('Received Video', frame)
                    # if cv2.waitKey(1) & 0xFF == ord('q'):
                    #     break
                ###################
                # print("Checking")
                # data = ""
                # payload_size = struct.calcsize("H") 
                # while True:
                #     print("Found")
                #     while len(data) < payload_size:
                #         data += client.recv(4096)
                #     packed_msg_size = data[:payload_size]
                #     data = data[payload_size:]
                #     msg_size = struct.unpack("H", packed_msg_size)[0]
                #     while len(data) < msg_size:
                #         data += client.recv(4096)
                #     frame_data = data[:msg_size]
                #     data = data[msg_size:]
                #     ###

                #     frame=pickle.loads(frame_data)
                #     # print frame
                #     cv2.imshow('frame',frame)
                #     if cv2.waitKey(2) & 0xFF == ord('q'):
                #         break

                data = b'' ### CHANGED
                payload_size = struct.calcsize("L") 
                while True:
                        # Retrieve message size
                    while len(data) < payload_size:
                        data += client.recv(4096)

                    packed_msg_size = data[:payload_size]
                    data = data[payload_size:]
                    msg_size = struct.unpack("L", packed_msg_size)[0] ### CHANGED

                    # Retrieve all data based on message size
                    while len(data) < msg_size:
                        data += client.recv(4096)

                    frame_data = data[:msg_size]
                    data = data[msg_size:]

                    # Extract frame
                    frame = pickle.loads(frame_data)

                    # Display
                    cv2.imshow('Recieved', frame)
                    cv2.waitKey(1)        
                    # client.close()
                    # cv2.destroyAllWindows() 

            else:
                pass
                # print(msg)
        except Exception as e:
            print("Error receiving message:", e)
            break

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((SERVER, PORT))

mapping = {}

receive_thread = threading.Thread(target=receive_message)
receive_thread.start()

name = input("Enter your name: ")
client.sendall(name.encode())

mykey = RSA.generate(2048)
private_key=mykey
pubkey = mykey.publickey().exportKey(format='PEM').decode('utf-8')
client.sendall(pubkey.encode())

print("Connected to the server.")

while True:
    r = input("Enter op: ")
    if r == 'QUIT':
        client.sendall(r.encode())
        break
    elif r=='Msg':
        client.sendall('Msg'.encode())
        print(mapping)
        d=input("Who are you sending it to?: ")
        if not d  in mapping.keys():
            print("User unavailable")
            continue
        client_b_public_key_string = mapping.get(d)
        client_b_public_key = RSA.importKey(client_b_public_key_string)
        cipher = PKCS1_OAEP.new(client_b_public_key)
        encrypted_message = cipher.encrypt(b"Hello, Client B!")
        encoded_message = base64.b64encode(encrypted_message)
        client.sendall(encoded_message)
        out = client.recv(1024).decode()
        print(out)
    elif r=='vid':
        client.sendall('vid'.encode())
        display_video()
        # data = b''
        # payload_size = 8  # Assuming 8 bytes for size indication

        # while True:
        #     while len(data) < payload_size:
        #         data += client.recv(4096)
        #     frame_size = int.from_bytes(data[:payload_size], byteorder='big')
        #     data = data[payload_size:]
        #     while len(data) < frame_size:
        #         data += client.recv(4096)
        #     frame_data = data[:frame_size]
        #     data = data[frame_size:]
        #     frame = pickle.loads(frame_data)
        #     cv2.imshow('Received Video', frame)
        #     if cv2.waitKey(1) & 0xFF == ord('q'):
        #         break

        # cv2.destroyAllWindows()
    else:
        pass

client.close()
