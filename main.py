import subprocess
from threading import Thread
import json
import socket
from datetime import datetime

UDP_PORT = 12345
TCP_PORT = 12345

class PixelArtApp:
    online_users = []  # [{"ip": "123.942.1.3", "name": "efe"}, ...]
    burst_ID_set = set()  # stores ID of discovery messages

    def __init__(self, ip, name):
        self.ip = ip
        self.name = name

    # returns IPs of users as a set.
    def get_user_ips(self):
        user_ips = set()
        for user in self.online_users:
            user_ips.add(user["ip"])
        return user_ips

    def print_online_users(self):
        print("Online Users:")
        for user in self.online_users:
            if user["name"] == self.name:
                continue
            print(user["name"])
        print()

    def create_discover_message(self):
        timestamp_integer = int(datetime.timestamp(datetime.now()))
        message = {"type":1, "name":self.name, "IP":self.ip, "ID":timestamp_integer}
        return message

    def handle_tcp_connection(self, conn):
        with conn:
            data = conn.recv(10240)

        message_as_json_string = data.decode(encoding="utf-8")
        message = json.loads(message_as_json_string)

        if message["type"] == "2":
            if message["IP"] not in self.get_user_ips():
                self.online_users.append({"ip": message["IP"], "name": message["name"]})

    def listen_tcp(self):
        # listens the port for possible TCP connections and calls handle_tcp_connection() when necessary.
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((self.ip, TCP_PORT))
            s.listen()
            while True:
                conn, addr = s.accept()
                tcp_handler = Thread(target=self.handle_tcp_connection, args=(conn,), daemon=True)
                tcp_handler.start()

    def get_udp_message(self):
        while True:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.bind(('', UDP_PORT))
                msg, addr = s.recvfrom(10240)
            except Exception as e:
                print("an exception {} happened".format(e))
            finally:
                s.close()
            
            message_as_json_string = msg.decode(encoding="utf-8")
            message = json.loads(message_as_json_string)

            if message["type"] == "1":
                # skip if discover message comes from itself.
                if message["IP"] == self.ip:
                    continue

                # update online users list.
                if message["IP"] not in self.get_user_ips():
                    self.online_users.append({"ip": message["IP"], "name": message["name"]})

                # skip if that user is already discovered with the given burst ID (timestamp).
                # or save that burst ID.
                if message["ID"] in self.burst_ID_set:
                    continue
                self.burst_ID_set.add(message["ID"])

                # prepare for discovery response.
                receiver_name = message["name"]
                outgoing_IP = self.get_ip_from_name(name=receiver_name)
                outgoing_message = {"type":2, "name":self.name, "IP":self.ip}
                outgoing_message_as_json = json.dumps(outgoing_message)
                outgoing_message_as_json_encoded_to_utf8 = outgoing_message_as_json.encode(encoding="utf-8")

                # send discovery response message.
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.connect((outgoing_IP, TCP_PORT))
                    s.settimeout(1.0)
                    s.sendall(outgoing_message_as_json_encoded_to_utf8)
                except:
                    print("{} is not online currently.".format(receiver_name))
                    self.online_users.remove({"ip": outgoing_IP, "name": receiver_name})
                finally:
                    s.close()

    def send_discovery_messages(self):
        message = self.create_discover_message()
        message_as_json_string = json.dumps(message)
        message_as_json_string_encoded_to_utf8 = message_as_json_string.encode("utf-8")

        # send them by broadcasting.
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.bind(('', 0))
            s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            for _ in range(10):
                s.sendto(message_as_json_string_encoded_to_utf8, ('<broadcast>', UDP_PORT))
        except:
            pass
        finally:
            s.close()

    def run(self):
        tcp_listener = Thread(target=self.listen_tcp, daemon=True)
        udp_listener = Thread(target=self.get_udp_message, daemon=True)
        tcp_listener.start()
        udp_listener.start()

        self.send_discovery_messages()

        while True:
            command = input("What do you want to do? (see_onlines/exit)\n")
            if command == "see_onlines":
                self.print_online_users()
            elif command == "exit":
                break

def get_my_ip():
    # for MacOS.
    return subprocess.run(["ipconfig", "getifaddr", "en0"], text=True, stdout=subprocess.PIPE).stdout[0:-1]


print("Welcome to Pixel Art!")
my_ip = get_my_ip()
print("Your IP is: {}".format(my_ip))
name = input("Please tell me your name: ")

app = PixelArtApp(ip=my_ip, name=name)
app.run()