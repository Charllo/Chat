----

<p align="center">
  <a href="https://github.com/thatguywiththatname/Chat/archive/master.zip">Download</a>
</p>

----

# Notes/Warnings

 + The server and client are .pyw files. This means that the console window will not open, just the tkinter GUI
 + UNICODE CHARACTERS ARE NOT SUPPORTED
 + When a client is dropped, they are popped from a dictionary. This is also added to when someone joins, so
 there is a tiny chance that 2 functions will be trying to access the same dictionary at the same time. This
 can cause a conflict but it is extremely unlikely and I can't be bothered to fix it ;)

---

# Using the client:

 + Input the server IP
 + Input the server Port
 + Input the name which you want other people to see when you send a message
 + Press enter or the connect button to connect
 + Type in the message bar then press enter or the send button to send message

---

# Using the server:
 + Input the chosen port (a default one will already be in the box)
 + Input a server name (a default one will also already be in the box)
 + Choose whether to log the chat with the checkbox
 + Press enter or start to start server
 + Type in the message bar then press enter or the send button to send message
 + You can also kick people by typing in their name and pressing `kick`

---

# Credits

 + Thanks to @Cutwell for the fancy graphic stuff in client.pyw

---
