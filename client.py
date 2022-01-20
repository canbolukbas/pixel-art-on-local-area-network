import socket

PACKET_SIZE = 1024
TCP_PORT = 12345
TARGET_IP = "172.20.10.9"


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((TARGET_IP, TCP_PORT))
    
    # receive until server closes the connection
    received_msg = ""
    while True:
        msg = s.recv(PACKET_SIZE)
        if len(msg) <= 0:
            break
        received_msg += msg.decode("utf-8")
    
    print(received_msg)

