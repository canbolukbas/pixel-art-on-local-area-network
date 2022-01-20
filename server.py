import socket

PACKET_SIZE = 1024
TCP_PORT = 12345

# returns local IP.
def get_my_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip_address = s.getsockname()[0]
    finally:
        s.close()
    return ip_address

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    my_ip = get_my_ip()
    s.bind((my_ip, TCP_PORT))
    s.listen()
    while True:
        client_socket, address = s.accept()
        print("Connection from {} has been accomplished!".format(address))

        client_socket.send(bytes("Naber la essek... :D", "utf-8"))
        client_socket.close()