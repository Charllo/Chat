from datetime import datetime   # For timestamping messages
from tkinter import messagebox  # Quit dialouge box
import tkinter as tk            # GUI
import socket                   # Socket connections
import threading                # Running multiple functions at once

class MainApplication(tk.Frame):
    def __init__(self, parent, host, port, name, checkbox_value, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.parent.geometry("775x655")
        self.parent.title("Server | Error")  # This will be changed if no error occurs
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = host
        self.port = port
        self.name = name
        self.chatlog_bool = checkbox_value
        self.client_dict = {}
        self.buffer_size = 1024
        self.tag = ""
        self.parent.protocol("WM_DELETE_WINDOW", self.on_closing)

        #  create a Frame for the Text and Scrollbar
        self.txt_frm = tk.Frame(self.parent, width=775, height=600)
        self.txt_frm.grid(row=0, columnspan=2)
        #  ensure a consistent GUI size
        self.txt_frm.grid_propagate(False)
        #  implement stretchability
        self.txt_frm.grid_rowconfigure(0, weight=1)
        self.txt_frm.grid_columnconfigure(0, weight=1)
        #  create a Text widget
        self.message_area = tk.Text(self.txt_frm, borderwidth=3, relief="sunken", state="disabled")
        self.message_area.config(font=("consolas", 12), undo=True, wrap='word')
        self.message_area.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)
        #  create a Scrollbar and associate it with txt
        self.scrollb = tk.Scrollbar(self.txt_frm, command=self.message_area.yview)
        self.scrollb.grid(row=0, column=3, sticky="nsew")
        self.message_area["yscrollcommand"] = self.scrollb.set

        self.msg_entry = tk.Entry(self.parent, width=20)
        self.msg_entry.grid(row=2, sticky="E")

        self.parent.bind("<Return>", lambda event: self.send_message_from_box())  # Bind return to send msg
        self.btn_send = tk.Button(self.parent, text="Send", command=self.send_message_from_box, width=20)
        self.btn_send.grid(row=2, column=1, sticky="W")

        self.kick_entry = tk.Entry(self.parent, width=20)
        self.kick_entry.grid(row=3, sticky="E")

        self.btn_kick = tk.Button(self.parent, text="Kick", command=self.kick, width=20)
        self.btn_kick.grid(row=3, column=1, sticky="W")

         # Add colours to message_area
        self.message_area.tag_configure("self_message", foreground="blue")
        self.message_area.tag_configure("connection", foreground="red")
        self.message_area.tag_configure("server_config", foreground="purple")

        if self.chatlog_bool:
            self.chatlogfile = open("chatlog.txt", "w")
            self.addtotext(self.message_area, "[!] chatlog.txt ready to write", config_message=True)

        # socket.bind() checking
        try:
            self.s.bind((self.host, self.port))
        except OSError:  # Can't bind
            self.addtotext(self.message_area, "[!] Unable to bind to port {}".format(self.port), config_message=True)
            self.unexpected_shutdown()
        else:  # If everything went well
            self.addtotext(self.message_area, "[!] Socket bound", config_message=True)

            try:
                self.s.listen()
            except TypeError: # Py versions < 3.5
                # 5  = Connection queue
                self.s.listen(5)

            self.addtotext(self.message_area, "[!] Socket listening", config_message=True)
            self.parent.title("Server | {} | {}:{}".format(self.name, self.host, self.port))
            client_checking_thrd = threading.Thread(target=self.client_checking)
            client_checking_thrd.daemon = True
            client_checking_thrd.start()
            self.addtotext(self.message_area, "[!] Server started".format(self.host, self.port), config_message=True)
            self.addtotext(self.message_area, "= SERVER INFO ==================", config_message=True)
            self.addtotext(self.message_area, "IP:   {}".format(self.host), config_message=True)
            self.addtotext(self.message_area, "PORT: {}".format(self.port), config_message=True)
            self.addtotext(self.message_area, "NAME: {}".format(self.name), config_message=True)
            self.addtotext(self.message_area, "================================\n", config_message=True)

    def disable_all(self):
        self.btn_send.config(state="disabled")
        self.btn_kick.config(state="disabled")
        self.parent.bind("<Return>", lambda event: self.disable_all())  # Rebind to do nothing

    def send_message_from_box(self):
        message = self.msg_entry.get()
        self.msg_entry.delete(0, "end")
        if message.rstrip() != "":
            self.addtotext(self.message_area, "You: {}".format(message), True)
            self.send_all("", "Server-User: {}".format(message))

    def send_all(self, in_client, out_message):
        to_kick = []
        for c in self.client_dict.keys():  # For each client
            if c != in_client:  # If it is not the one that sent the msg
                try:
                    c.send(str.encode(out_message))  # Send the message
                except (BrokenPipeError, OSError):  # For Linux
                    to_kick.append(c)
        for k in to_kick:  # For each client to kick
            k.close()  # Will trigger connection exception

    def kick(self):
        name_map = {v: k for k, v in self.client_dict.items()}  # Swap names and client obj
        user = self.kick_entry.get()
        self.kick_entry.delete(0, "end")
        try:
            client_to_kick = name_map[user]  # Get client object
            client_to_kick.send(str.encode("[Server Message] You have been kicked by the server"))  # Send the message
            kick_msg = "[Server Message] {} kicked from server".format(user)
            self.addtotext(self.message_area, kick_msg, connection_flag=True)
            self.send_all("", kick_msg)
            client_to_kick.close()  # Force close the connection
        except KeyError:
            self.addtotext(self.message_area, "[Kick message] {} not recognized".format(user), connection_flag=True)

    def handler(self, client, addr):
        nickname_done = False  # Nickname set = False
        ip_port = "{}:{}".format(addr[0], addr[1])  # Looks like "127.0.0.1:1234"
        while True:
            try:
                r_msg = client.recv(self.buffer_size)  # Recieve message

                if r_msg:  # If there is text
                    decoded = r_msg.decode("utf-8")
                    if nickname_done == False:  # If nickname not set
                        nick_splt = decoded.split(" ")  # Split it
                        recieved_name = " ".join(nick_splt[1:])  # Extract the name part

                        if recieved_name in self.client_dict.values():
                            client.send(str.encode("[Server Message] Name already in use, please choose another"))
                            self.addtotext(self.message_area, "[Server Message] Client {} tried connecting with {} - already in use".format(ip_port, recieved_name), connection_flag=True)
                            nickname_done = False  # Reset, just in case
                            out_msg = False

                        else:
                            self.client_dict[client] = recieved_name  # Add to dict
                            self.addtotext(self.message_area, "[Server Message] {} set nickname to {}".format(ip_port, recieved_name), connection_flag=True)
                            nickname_done = True  # Nick has been set
                            out_msg = "[Server Message] {} joined".format(self.client_dict[client])  # Tell all clients
                            # \n because it looks cleaner on the client side
                            client.send(str.encode("[Server Message] {}, your connection to {} was successful!\n".format(recieved_name, self.name)))  # Tell the client
                            self.addtotext(self.message_area, "[Server Message] Client {} ({}) connection successful".format(recieved_name, ip_port), connection_flag=True)

                    else:  # If nick already set
                        self.addtotext(self.message_area, "{}: {}".format(self.client_dict[client], decoded))
                        out_msg = "{}: {}".format(self.client_dict[client], decoded)

                    if out_msg:
                        self.send_all(client, out_msg)

            except (ConnectionResetError, ConnectionAbortedError, OSError):
                try:
                    drop_msg = "[Server Message] Client {} ({}) dropped".format(self.client_dict[client], ip_port)
                    self.client_dict.pop(client)  # Remove client from dict
                    self.send_all(client, drop_msg)
                except KeyError:  # Client kicked/broke before fully connected
                    drop_msg = "[Server Message] Unknown client ({}) dropped before full connection".format(ip_port)
                    # No need to send everyone else this message

                self.addtotext(self.message_area, drop_msg, connection_flag=True)
                client.close()
                break  # End process

    def client_checking(self):
        while True:
            try:
                client, addr = self.s.accept()
            except OSError:  # socket closed
                break

            self.addtotext(self.message_area, "[Server Message] Accepted connection from: {}:{}".format(addr[0], addr[1]), connection_flag=True)
            client_handler = threading.Thread(target=self.handler, args=(client, addr))
            client_handler.daemon = True
            client_handler.start()

    def unexpected_shutdown(self):
        self.disable_all()  # Buttons can't be used

    def addtotext(self, widget, text, self_message=False, connection_flag=False, config_message=False):
        timestamp = datetime.now().strftime("%H:%M")
        text = "{} | {}".format(timestamp, text)  # Add timestamp

        if self.chatlog_bool:
            self.chatlogfile.write("{}\n".format(str(text)))  # Chat log

        if connection_flag == True:
            self.tag = "connection"
        elif self_message == True:
            self.tag = "self_message"
        elif config_message == True:
            self.tag = "server_config"
        else:
            self.tag = ""

        #  Adds a line to a text widget, makes it un-editable and then scrolls to the bottom
        widget.configure(state="normal")
        widget.insert("end", "\n{}".format(text), self.tag)
        widget.configure(state="disabled")
        widget.see(tk.END)

    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.addtotext(self.message_area, "[!] Server Stopped", config_message=True)  # Mainly just so this gets logged
            try:
                self.parent.destroy()
            except TclError:
                pass  # Root already destroyed
            if self.chatlog_bool:
                self.chatlogfile.close()  # Close connection to chatlog file
            self.s.close()  # Close connection
            quit()

class LaunchWindow(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.check_log_var = tk.IntVar()

        self.host = socket.gethostbyname(socket.gethostname())
        if self.host == "127.0.0.1":  # Try a different way
            self.host = socket.gethostbyname(socket.getfqdn())

        self.parent.title("~")
        self.parent.geometry("190x115")
        self.host_label_filled = tk.Label(self.parent, text = "{}".format(self.host))
        self.host_label = tk.Label(self.parent, text = "Host IP:")
        self.port_label = tk.Label(self.parent, text = "Host Port:")
        self.name_label = tk.Label(self.parent, text = "Server Name:")
        self.port_entry = tk.Entry(self.parent, width=20)
        self.name_entry = tk.Entry(self.parent, width=20)
        self.btn_start = tk.Button(self.parent, text="Start", command=self.checkvalues, width=20)
        self.chatlog_checkbutton = tk.Checkbutton(self.parent, text="Enable Chatlog", variable=self.check_log_var)
        self.port_entry.insert(0, "5640")  # Insert default value
        self.name_entry.insert(0, "TCP Server")  # Insert default value
        self.host_label.grid(row=0)
        self.port_label.grid(row=1)
        self.name_label.grid(row=2)
        self.host_label_filled.grid(row=0, column=1)
        self.port_entry.grid(row=1, column=1)
        self.name_entry.grid(row=2, column=1)
        self.btn_start.grid(row=3, columnspan=2)
        self.chatlog_checkbutton.grid(row=4, columnspan=2)
        self.chatlog_checkbutton.select()  # Defaults to being checked
        self.parent.bind("<Return>", lambda event: self.checkvalues())

    def checkvalues(self):
        try:
            port = int(self.port_entry.get())
        except ValueError:
            messagebox.showinfo("Error", "Invalid port")
            return
        else:
            if port > 65535 or port < 0:
                messagebox.showinfo("Error", "Port must be 0-65535")
                return
            elif str(port) == "":
                messagebox.showinfo("Error", "Invalid port")
                return

        name = self.name_entry.get()
        if name == "":
            messagebox.showinfo("Error", "Invalid server name")
            return

        self.parent.withdraw()  # Hide this connection window
        self.new_root = tk.Tk()
        MainApplication(self.new_root, self.host, port, name, self.check_log_var.get())
        self.new_root.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    LaunchWindow(root)
    root.mainloop()
