from tkinter import messagebox
from datetime import datetime
import tkinter as tk
import threading
import socket

class MainApplication(tk.Frame):
    def __init__(self, parent, host, port, nick, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.host = host
        self.port = port
        self.nick = nick
        self.buffer_size = 1024
        self.tag = ""
        self.parent.title("Client | Connected to {}:{}".format(host, port))
        self.parent.geometry("775x630")

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
        self.scrollb.grid(row=0, column=3, sticky='nsew')
        self.message_area['yscrollcommand'] = self.scrollb.set

        self.msg_entry = tk.Entry(self.parent, width=20)
        self.msg_entry.grid(row=2, sticky="E")

        # Only enable after connection made and nickname sent
        self.btn_send = tk.Button(self.parent, text="Send", width=20, state="disabled", command=self.send_message_from_box)
        self.btn_send.grid(row=2, column=1, sticky="W")

        # Add colours to message_area
        self.message_area.tag_configure("connection", foreground="red")
        self.message_area.tag_configure("self_message", foreground="blue")

        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.s.connect((host, port))
        except OSError:
            self.addtotext(self.message_area, "[Client] Socket attempted to connect to an unreachable network", important=True)
            self.parent.mainloop()
        except ConnectionRefusedError:
            self.addtotext(self.message_area, "[Client] No connection could be made", important=True)
            self.parent.mainloop()
        else:
            self.addtotext(self.message_area, "[Client] Connected to server", important=True)
            self.s.send("NICK {}".format(nick).encode("utf-8"))
            self.addtotext(self.message_area, "[Client] Name sent", important=True)
            self.main()

    def disable_sending(self):
        self.btn_send.config(state="disabled")
        self.parent.bind("<Return>", lambda event: self.disable_sending())  # Rebind to do nothing

    def addtotext(self, widget, text, self_message=False, important=False):
        timestamp = datetime.now().strftime("%H:%M")
        text = "{} | {}".format(timestamp, text)  # Add timestamp

        if self_message == True:
            self.tag = "self_message"
        elif important == True:
            self.tag = "connection"
        else:
            self.tag = ""

        #  Adds a line to a text widget, makes it un-editable and then scrolls to the bottom
        widget.configure(state="normal")
        widget.insert("end", "\n{}".format(text), self.tag)
        widget.configure(state="disabled")
        widget.see(tk.END)

    def send_message_from_box(self):
        message = self.msg_entry.get()
        self.msg_entry.delete(0, "end")
        if message.rstrip() != "":
            try:
                self.addtotext(self.message_area, "You: {}".format(message), True)
                self.s.send(str.encode(message))
            except (ConnectionResetError, OSError):  # Needed after being kicked
                self.s.close()

    def msg_handler(self):
        while True:
            try:
                data = self.s.recv(self.buffer_size)
                if data:
                    decoded = data.decode("utf-8")
                    split = decoded.split(" ")
                    if decoded == "[Server Message] YOU HAVE BEEN KICKED BY THE SERVER":
                        self.addtotext(self.message_area, decoded, important=True)
                        raise ConnectionResetError

                    elif decoded == "[Server Message] Name already is use, please choose another":
                        self.addtotext(self.message_area, decoded, important=True)
                        raise ConnectionResetError

                    # If it's an official server message
                    elif str(split[0])+str(split[1]) == "[ServerMessage]":
                        self.addtotext(self.message_area, str(decoded), important=True)
                    else:
                        self.addtotext(self.message_area, str(decoded))

            except (ConnectionResetError, OSError):
                self.s.close()
                self.disable_sending()
                self.addtotext(self.message_area, "[Client] Connection to server lost", important=True)
                break

    def main(self):
        self.parent.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.parent.bind("<Return>", lambda event: self.send_message_from_box()) # Bind return to send msg
        self.btn_send.config(state="normal")  # Connected, so user can send messages now
        self.message_handler = threading.Thread(target=self.msg_handler)
        self.message_handler.daemon = True  # Thread is killed when main ends
        self.message_handler.start()

    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            try:
                self.parent.destroy()
            except TclError:
                pass  # Root already destroyed
            self.s.close()  # Close connection
            quit()  # Original login window will destry along with this

class LaunchWindow(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.parent.title("Connect")
        self.parent.geometry("300x100")
        self.host_entry = tk.Entry(self.parent, width=20)
        self.port_entry = tk.Entry(self.parent, width=20)
        self.nick_entry = tk.Entry(self.parent, width=20)
        self.btn_connect = tk.Button(self.parent, text="Connect", command=self.checkvalues, width=20)
        self.host_entry.grid(row=0)
        self.port_entry.grid(row=1)
        self.nick_entry.grid(row=2)
        self.btn_connect.grid(row=3)

    def checkvalues(self):
        self.host = self.host_entry.get()
        try:
            socket.inet_aton(self.host)  # Throws a socket error if IP is illegal
        except socket.error:
            messagebox.showinfo("Error", "Not a valid IP address")
            return

        try:
            self.port = int(self.port_entry.get())
        except ValueError:
            messagebox.showinfo("Error", "Invalid port")
            return
        else:
            if self.port > 65535 or self.port < 0:
                messagebox.showinfo("Error", "Port must be 0-65535")
                return
            elif str(self.port) == "":
                messagebox.showinfo("Error", "Invalid port")
                return

        self.nick = self.nick_entry.get()
        if self.nick == "":
            messagebox.showinfo("Error", "Invalid name")
            return

        self.new_root = tk.Tk()
        MainApplication(self.new_root, self.host, self.port, self.nick)
        self.parent.withdraw()  # Hide this connection window
        self.new_root.mainloop()
        self.new_root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    LaunchWindow(root)
    root.mainloop()