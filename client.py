# client.py
import socket
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import base64
import threading
import pickle
import cv2

SERVER = "127.0.0.1"
PORT = 8080

def decrypt_and_print(encrypted_msg):
    try:
        cipher = PKCS1_OAEP.new(private_key)
        decrypted_msg = cipher.decrypt(base64.b64decode(encrypted_msg)).decode()
        print("Decrypted message:", decrypted_msg)
    except Exception as e:
        print("Error decrypting message:", e)

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
                print("Video block")
                data=client.recv(1024)
                frame_data = data[len(b"VIDEO:"):]
                frame = pickle.loads(frame_data)
                cv2.imshow('Received Video', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
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
        data = b''
        payload_size = 8  # Assuming 8 bytes for size indication

        while True:
            while len(data) < payload_size:
                data += client.recv(4096)
            frame_size = int.from_bytes(data[:payload_size], byteorder='big')
            data = data[payload_size:]
            while len(data) < frame_size:
                data += client.recv(4096)
            frame_data = data[:frame_size]
            data = data[frame_size:]
            frame = pickle.loads(frame_data)
            cv2.imshow('Received Video', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cv2.destroyAllWindows()
    else:
        pass

client.close()
