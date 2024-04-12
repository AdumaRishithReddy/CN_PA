import socket
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import threading
import time
import pickle
import cv2
import base64
import struct
import queue

BUFF_SIZE = 65535
frame_queue = queue.Queue()
critical_event = threading.Event()
SERVER = "127.0.0.1"
PORT = 8080

# Create a lock object to synchronize user inputs during video streaming
# global incorrect
msg_q=[]
end=[]
input_lock = threading.Lock()
vid_list=[]
done=[]
end_prog=[]
vid_end=[]
def decrypt_and_print(encrypted_msg):
    try:
        cipher = PKCS1_OAEP.new(private_key)
        decrypted_msg = cipher.decrypt(base64.b64decode(encrypted_msg)).decode()
        print("Decrypted message:", decrypted_msg)
    except Exception as e:
        pass
        # print("Error decrypting message:", e)

def display_video():
    while True:
        if not frame_queue.empty():
            frame = frame_queue.get()
            cv2.imshow('Buffered', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        else:
            time.sleep(0.1)

    cv2.destroyAllWindows()

def receive_message():
    # with input_lock:
    # global incorrect
    while True:
        # with input_lock:
            try:
                msg = client.recv(1024).decode()
                # print("Recv: ",msg,"do")
                if msg.startswith("UPDATE_DICT:"):
                    new_mapping = {}
                    _, dict_str = msg.split(":", 1)
                    for item in dict_str.split(","):
                        name, key = item.split(":")
                        new_mapping[name] = key
                    global mapping
                    mapping = new_mapping
                    # print("Updated client list received.")
                elif msg.startswith("Enc:"):
                    encrypted_msg = msg[len("Enc:"):]
                    decrypt_and_print(encrypted_msg)
                elif msg.startswith("vid:"):
                    vid_end.append(False)
                    data = b''
                    payload_size = struct.calcsize("L")
                    while True:
                        while len(data) < payload_size:
                            data += client.recv(4096)
                        
                        packed_msg_size = data[:payload_size]
                        data = data[payload_size:]
                        msg_size = struct.unpack("L", packed_msg_size)[0]

                        while len(data) < msg_size:
                            data += client.recv(4096)

                        frame_data = data[:msg_size]
                        data = data[msg_size:]
                        if frame_data == pickle.dumps(b'vid_end'):  # Check for the end signal
                            cv2.destroyAllWindows()
                            vid_end.clear()
                            break
                        frame = pickle.loads(frame_data)
                        cv2.imshow('Received', frame)
                        cv2.waitKey(1)
                        # if frame_data == b'vid_end':
                        #     cv2.destroyAllWindows()
                        #     break
                elif msg.startswith("vid_end"):
                    cv2.destroyAllWindows()
                elif msg.startswith("vida:"):
                    ol=msg[len("vida:"):]
                    lis=ol.split('vida:')
                    for a in lis:
                        # print(a)
                        vid_list.append(a)
                elif msg.startswith("end_list"):
                    done.append(True)
                elif "QUIT" in msg:
                    print("ASAAD")
                    end_prog.append(True)
                    break

                else:
                    # incorrect=incorrect+1
                    # print("else",msg,"ends")
                    
                    # if msg=="end_list":
                    #     end.append(1)
                    msg_q.append(msg)
                    # print(msg_q)
                    # pass
            except Exception as e:
                print("Error receiving message:", e)
                break
        # time.sleep(1)

def handle_video_stream():
    # global incorrect
    try:
        # Acquire the lock to ensure exclusive access to video streaming inputs
        with input_lock:
            client.sendall('vid'.encode())
            videos = []
            while True not in done:
                time.sleep(0.5)
            print("Available Videos:")
            for i, video in enumerate(vid_list):
                print(f"{i}: {video}")

            choice = input("Which video do you want to stream (Enter index): ")
            if choice.isdigit() and 0 <= int(choice) < len(vid_list):
                selected_video = vid_list[int(choice)]
                client.sendall(selected_video.encode())
                while False in vid_end:
                    pass
                vid_list.clear()
                done.clear()
            else:
                print("Invalid choice. Please enter a valid index.")

    except Exception as e:
        print("Error handling video stream:", e)


client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((SERVER, PORT))

mapping = {}

receive_thread = threading.Thread(target=receive_message)
receive_thread.start()

name = input("Enter your name: ")
client.sendall(name.encode())

mykey = RSA.generate(2048)
private_key = mykey
pubkey = mykey.publickey().exportKey(format='PEM').decode('utf-8')
client.sendall(pubkey.encode())

print("Connected to the server.")

while True:
        print("INSTRUCTIONS\n-Msg to start chat\n-vid to start Video streaming \n-QUIT to exit from the application")
        r = input("Enter op: ")
        if r == 'QUIT' or True in end_prog :
            client.sendall(r.encode())
            break
        elif r == 'Msg':
            client.sendall('Msg'.encode())
            print("Available Users")
            for user in mapping.keys():
                print("User:", user)
            recipient = input("Who are you sending it to?: ")
            if recipient not in mapping.keys():
                print("User unavailable")
                continue
            message = input("What is the message: ").encode()
            client_b_public_key_string = mapping.get(recipient)
            client_b_public_key = RSA.importKey(client_b_public_key_string)
            cipher = PKCS1_OAEP.new(client_b_public_key)
            encrypted_message = cipher.encrypt(message)
            encoded_message = base64.b64encode(encrypted_message)
            client.sendall(encoded_message)
        elif r == 'vid':
            handle_video_stream()
        else:
            pass

# receive_thread.join()
print("Thank you for using the application!!")
client.close()
