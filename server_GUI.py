from datetime import datetime   # For timestamping messages
from tkinter import messagebox  # Quit dialouge box
from tkinter import *           # GUI
import socket                   # Socket connections
import threading                # Running multiple functions at once
import argparse                 # Arguments

host = ""
buffer_size = 1024
client_dict = {}
tag = ""

fancy_server_ouput = """
= SERVER INFO ==================
 IP:   {}
 PORT: {}
 NAME: {}
================================"""

root = Tk()
root.geometry("775x655")
root.title("Server | Error")  # This will be changed if no error occurs

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

host = socket.gethostbyname(socket.gethostname())
if host == "127.0.0.1":  # Try a different way
    host = socket.gethostbyname(socket.getfqdn())

# Argument parsing stuff
parser = argparse.ArgumentParser()
parser.add_argument("-p", "--port", help="The port which this server will be bound to", type=int, default=5640)
parser.add_argument("-n", "--name", help="The name of the server", default="TCP Server")
args = parser.parse_args()
# default port = 5640 -> iana.org -> unassigned port
# -p has to be provided if you want a custom name
port = args.port
name = args.name

def addtotext(widget, text, self_message=False, connection_flag=False, config_message=False):
    timestamp = datetime.now().strftime("%H:%M")
    text = "{} | {}".format(timestamp, text)  # Add timestamp

    f.write("{}\n".format(str(text)))  # Chat log

    if connection_flag == True:
        tag = "connection"
    elif self_message == True:
        tag = "self_message"
    elif config_message == True:
        tag = "server_config"
    else:
        tag = ""

    #  Adds a line to a text widget, makes it un-editable and then scrolls to the bottom
    widget.configure(state="normal")
    widget.insert("end", "\n{}".format(text), tag)
    widget.configure(state="disabled")
    widget.see(END)

def disable_all():
    btn_send.config(state="disabled")
    btn_kick.config(state="disabled")
    root.bind("<Return>", lambda event: disable_all())  # Rebind to do nothing

def send_message_from_box():
    message = msg_entry.get()
    msg_entry.delete(0, "end")
    if message.rstrip() != "":
        addtotext(message_area, "You: {}".format(message), True)
        send_all("", "Server-User: {}".format(message))

def send_all(in_client, out_message):
    to_kick = []
    for c in client_dict.keys():  # For each client
        if c != in_client:  # If it is not the one that sent the msg
            try:
                c.send(str.encode(out_message))  # Send the message
            except (BrokenPipeError, OSError):  # For Linux
                to_kick.append(c)
    for k in to_kick:  # For each client to kick
        k.close()  # Will trigger connection exception

def kick():
    name_map = {v: k for k, v in client_dict.items()}  # Swap names and client obj
    user = kick_entry.get()
    kick_entry.delete(0, "end")
    try:
        client_to_kick = name_map[user]  # Get client object
        client_to_kick.send(str.encode("[Server Message] You have been kicked by the server"))  # Send the message
        kick_msg = "[Server Message] {} kicked from server".format(user)
        addtotext(message_area, kick_msg, connection_flag=True)
        send_all("", kick_msg)
        client_to_kick.close()  # Force close the connection
    except KeyError:
        addtotext(message_area, "[Kick message] {} not recognized".format(user), connection_flag=True)

def handler(client, addr):
    nickname_done = False  # Nickname set = False
    ip_port = "{}:{}".format(addr[0], addr[1])  # Looks like "127.0.0.1:1234"
    while True:
        try:
            r_msg = client.recv(buffer_size)  # Recieve message

            if r_msg:  # If there is text
                decoded = r_msg.decode("utf-8")
                if nickname_done == False:  # If nickname not set
                    nick_splt = decoded.split(" ")  # Split it
                    recieved_name = " ".join(nick_splt[1:])  # Extract the name part

                    if recieved_name in client_dict.values():
                        client.send(str.encode("[Server Message] Name already in use, please choose another"))
                        addtotext(message_area, "[Server Message] Client {} tried connecting with {} - already in use".format(ip_port, recieved_name), connection_flag=True)
                        nickname_done = False  # Reset, just in case
                        out_msg = False

                    else:
                        client_dict[client] = recieved_name  # Add to dict
                        addtotext(message_area, "[Server Message] {} set nickname to {}".format(ip_port, recieved_name), connection_flag=True)
                        nickname_done = True  # Nick has been set
                        out_msg = "[Server Message] {} joined".format(client_dict[client])  # Tell all clients
                        # \n because it looks cleaner on the client side
                        client.send(str.encode("[Server Message] {}, your connection to {} was successfu!\n".format(recieved_name, name)))  # Tell the client
                        addtotext(message_area, "[Server Message] Client {} ({}) connection successful".format(recieved_name, ip_port), connection_flag=True)

                else:  # If nick already set
                    addtotext(message_area, "{}: {}".format(client_dict[client], decoded))
                    out_msg = "{}: {}".format(client_dict[client], decoded)

                if out_msg != False:
                    send_all(client, out_msg)

        except (ConnectionResetError, ConnectionAbortedError, OSError):
            try:
                drop_msg = "[Server Message] Client {} ({}) dropped".format(client_dict[client], ip_port)
                client_dict.pop(client)  # Remove client from dict
                send_all(client, drop_msg)
            except KeyError:  # Client kicked/broke before fully connected
                drop_msg = "[Server Message] Unknown client ({}) dropped before full connection".format(ip_port)
                # No need to send everyone else this message

            addtotext(message_area, drop_msg, connection_flag=True)
            client.close()
            break  # End process

def client_checking():
    while True:
        try:
            client,addr = s.accept()
        except OSError:  # socket closed
            break

        addtotext(message_area, "[Server Message] Accepted connection from: {}:{}".format(addr[0], addr[1]), connection_flag=True)
        client_handler = threading.Thread(target=handler,args=(client,addr))
        client_handler.daemon = True
        client_handler.start()

def main():
    client_checking_thrd = threading.Thread(target=client_checking)
    client_checking_thrd.daemon = True
    client_checking_thrd.start()
    addtotext(message_area, "[!] Server started".format(host, port), config_message=True)
    addtotext(message_area, "= SERVER INFO ==================", config_message=True)
    addtotext(message_area, "IP:   {}".format(host), config_message=True)
    addtotext(message_area, "PORT: {}".format(port), config_message=True)
    addtotext(message_area, "NAME: {}".format(name), config_message=True)
    addtotext(message_area, "================================\n", config_message=True)
    root.mainloop()

def unexpected_shutdown():
    disable_all()  # Buttons can't be used
    root.mainloop()  # Allow user to see message, when [x] pressed all will quit

def on_closing():
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        addtotext(message_area, "[!] Server Stopped", config_message=True)  # Mainly just so this gets logged
        try:
            root.destroy()
        except TclError:
            pass  # Root already destroyed
        s.close()  # Close connection
        quit()

root.protocol("WM_DELETE_WINDOW", on_closing)  # Bind the [X] button to on_closing

#  create a Frame for the Text and Scrollbar
txt_frm = Frame(root, width=775, height=600)
txt_frm.grid(row=0, columnspan=2)
#  ensure a consistent GUI size
txt_frm.grid_propagate(False)
#  implement stretchability
txt_frm.grid_rowconfigure(0, weight=1)
txt_frm.grid_columnconfigure(0, weight=1)
#  create a Text widget
message_area = Text(txt_frm, borderwidth=3, relief="sunken", state="disabled")
message_area.config(font=("consolas", 12), undo=True, wrap='word')
message_area.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)
#  create a Scrollbar and associate it with txt
scrollb = Scrollbar(txt_frm, command=message_area.yview)
scrollb.grid(row=0, column=3, sticky="nsew")
message_area["yscrollcommand"] = scrollb.set

msg_entry = Entry(root, width=20)
msg_entry.grid(row=2, sticky="E")

root.bind("<Return>", lambda event: send_message_from_box())  # Bind return to send msg
btn_send = Button(root, text="Send", command=send_message_from_box, width=20)
btn_send.grid(row=2, column=1, sticky="W")

kick_entry = Entry(root, width=20)
kick_entry.grid(row=3, sticky="E")

btn_kick = Button(root, text="Kick", command=kick, width=20)
btn_kick.grid(row=3, column=1, sticky="W")

 # Add colours to message_area
message_area.tag_configure("self_message", foreground="blue")
message_area.tag_configure("connection", foreground="red")
message_area.tag_configure("server_config", foreground="purple")

if __name__ == '__main__':  # Hasn't been imported
    with open ("chatlog.txt", "w") as f:
        addtotext(message_area, "[!] chatlog.txt ready to write", config_message=True)

        # Port input checking
        if port > 65535 or port < 0:
            addtotext(message_area, "[!] Port must be 0-65535", config_message=True)
            unexpected_shutdown()

        # socket.bind() checking
        try:
            s.bind((host, port))
        except OSError:  # Can't bind
            addtotext(message_area, "[!] Unable to bind to port {}".format(port), config_message=True)
            unexpected_shutdown()

        else:  # If everything went well
            addtotext(message_area, "[!] Socket bound", config_message=True)

            try:
                s.listen()
            except TypeError: # Py versions < 3.5
                # 5  = Connection queue
                s.listen(5)

            addtotext(message_area, "[!] Socket listening", config_message=True)
            root.title("Server | {} | {}:{}".format(name, host, port))
            main()  # Start main processes
