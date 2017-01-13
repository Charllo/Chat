import socket
import threading

host = "127.0.0.1"
port = 5005
buffer_size = 1024
client_list = []

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s.bind((host, port))
s.listen(5)

def handler(client, addr):
    client_list.append(client)
    while True:
        try:
            r_msg = client.recv(buffer_size)
            if r_msg:
                print ("Recieved: {}".format(r_msg))
                for c in client_list:
                    if c != client:
                        c.send(r_msg)
        except ConnectionResetError:
            print("Client {}:{} dropped".format(addr[0], addr[1]))

def main():
    while True:
        try:
            client,addr = s.accept()
            print ("Accepted connection from: {}:{}".format(addr[0], addr[1]))
            client_handler = threading.Thread(target=handler,args=(client,addr))
            client_handler.start()
        except KeyboardInterrupt:
            s.close()
            break

if __name__ == '__main__':
    main()
