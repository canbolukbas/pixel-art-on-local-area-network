import socket
import queue
from threading import Thread

PACKET_SIZE = 1024
TCP_PORT = 12345
OUTGOING_MESSAGES = queue.Queue()

# returns local IP.
def get_my_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip_address = s.getsockname()[0]
    finally:
        s.close()
    return ip_address

def chat():
    global OUTGOING_MESSAGES  # to be able to update global variable.
    
    print("Chat started! (Type exit to exit)\n")
    while True:
        message = input()
        OUTGOING_MESSAGES.put(message)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    my_ip = get_my_ip()
    s.bind((my_ip, TCP_PORT))
    s.listen()
    while True:
        client_socket, address = s.accept()
        print("Connection from {} has been accomplished!".format(address))
        chat_io = Thread(target=chat, daemon=True)
        chat_io.start()

        while True:
            if OUTGOING_MESSAGES.empty():
                # wait for IO
                continue

            text = OUTGOING_MESSAGES.get()
            if text == "exit":
                break
            client_socket.send(bytes(text, "utf-8"))
        
        client_socket.close()
