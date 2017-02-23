import socket
import threading

host = ""
port = ""
buffer_size = 1024
client_list = {}

while host == "":
    host = input("IP >> ")
    if host == "":
        print("Invalid")

while port == "":
    port = int(input("Port >> "))
    if str(port) == "":
        print("Invalid")

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s.bind((host, port))
s.listen(5)

def handler(client, addr):
    nickname_done = False  # Nickname set = False
    ip_port = "{}:{}".format(addr[0], addr[1])  # Looks like "127.0.0.1:1234"
    while True:
        try:
            r_msg = client.recv(buffer_size)  # Recieve message

            if r_msg:  # If there is text
                if nickname_done == False:  # If nickname not set
                    nick_msg = r_msg.decode("utf-8")  # Decode it
                    nick_splt = nick_msg.split(" ")  # Split it
                    client_list[client] = " ".join(nick_splt[1:])  # Add to dict
                    print("{} set nick to {}".format(ip_port, client_list[client]))
                    nickname_done = True  # Nick has been set
                    out_msg = "{} joined".format(client_list[client])  # Tell all clients

                else:  # If nick already set
                    # r_msg decoded so a) it will print and b) it wont get double encoded
                    print ("{}: {}".format(client_list[client], r_msg.decode("utf-8")))
                    out_msg = "{}: {}".format(client_list[client], r_msg.decode("utf-8"))

                for c in client_list.keys():  # For each client
                    if c != client:  # If it is not the one that sent the msg
                        c.send(str.encode(out_msg))  # Sent the message

        except ConnectionResetError:
            out_msg = "Client {} ({}) dropped".format(client_list[client], ip_port)
            print(out_msg)
            client_list.pop(client)  # Remove client from dict
            for c in client_list.keys():  # For each client
                if c != client:  # If it is not the one that sent the msg
                    c.send(str.encode(out_msg))  # Sent the message
            break  # End process

def main():
    while True:
        try:
            client,addr = s.accept()
            print ("Accepted connection from: {}:{}".format(addr[0], addr[1]))
            client_handler = threading.Thread(target=handler,args=(client,addr))
            client_handler.daemon = True
            client_handler.start()
        except KeyboardInterrupt:
            s.close()
            break

if __name__ == '__main__':
    main()
    quit()
