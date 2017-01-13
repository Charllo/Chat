import socket
import threading

host = "127.0.0.1"
port = 5005
buffer_size = 1024

def request_input():
    to_send = input("\nMessage to send >> ").encode("utf-8")
    s.send(to_send)
    request_input()

def msg_handler():
    while True:
        data = s.recv(buffer_size)
        if data:
            print("\n\nRecieved: {}".format(data))
            # Input still trailing from before, so just print the prompt again
            print("\nMessage to send >> ", end="")  # Remove end so input is in same place

def main():
    try:
        message_handler = threading.Thread(target=msg_handler)
        message_handler.start()
        while True:
            request_input()
    except KeyboardInterrupt:
        s.close()
        quit()

if __name__ == '__main__':
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    main()
