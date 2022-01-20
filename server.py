import socket
from threading import Thread
from time import sleep

PACKET_SIZE = 1024
TCP_PORT = 12345
OUTGOING_MESSAGES = list()  # To-do: Queue would be better.
CHAT_COMPLETED = False

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
    
    print("Chat started! (Type exit to exit)")
    while not CHAT_COMPLETED:
        message = input()
        OUTGOING_MESSAGES.append(message)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # no need to wait socket closures which may take long.
my_ip = get_my_ip()
s.bind((my_ip, TCP_PORT))
s.listen()
try:
    while True:
        client_socket, address = s.accept()
        print("Connection from {} has been accomplished!".format(address))
        chat_io = Thread(target=chat, daemon=True)
        chat_io.start()

        while True:
            if len(OUTGOING_MESSAGES)==0:
                continue

            text = OUTGOING_MESSAGES.pop(0)
            if text == "exit":
                break
            client_socket.send(bytes(text, "utf-8"))

        CHAT_COMPLETED = False
        OUTGOING_MESSAGES = list()
        client_socket.close()
        print("Connection from {} has been closed!".format(address))

except Exception as e:
    print(e)
finally:
    s.close()
