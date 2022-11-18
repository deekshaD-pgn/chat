import tkinter as tk
import network
import socket
import json

# SERVER_HOST = '10.10.98.79'
SERVER_HOST = '10.10.98.83'
SERVER_PORT = 9999



class ChatThread(network.ClientChatThread):
    
    def process_packet(self, packet):
        request = json.loads(packet)
        if request['cmd'] == 'said': 
            message = request['params']['name'] +':' + request['params']['message']
            conversation_input.insert(tk.END, message + '\n')
            
   
root = tk.Tk()
root.title("Chat")
root.geometry("640x480")

BG_GRAY = "#F9CB9C"
BG_COLOR = "#C27BA0"
TEXT_COLOR = "#444444"

FONT = "Helvetica 14"
FONT_BOLD = "Helvetica 13 bold"

conversation_label = tk.Label(root, text="Conversation")
conversation_label.pack(anchor=tk.W)

conversation_input = tk.Text(root, height=8)
conversation_input.pack(fill=tk.Y, expand=tk.YES)

message_label = tk.Label(root, text="Message", borderwidth=1)
message_label.pack(anchor=tk.W)

send_button = tk.Button(root, text="Send")
send_button.pack(anchor=tk.W, side=tk.RIGHT)

message_input = tk.Entry(root)
message_input.pack(side=tk.RIGHT, fill=tk.X, expand=tk.YES)

def send_click(event):
    command = {
        'cmd': 'say',
        'params': {
            'message': message_input.get(),
        },
    }
    chat_thread.write_packet(json.dumps(command))
    message_input.delete(0, tk.END)
    message_input.focus()

send_button.bind('<Button-1>', send_click)
message_input.bind('<Return>', send_click)
    
chat_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
chat_socket.connect((SERVER_HOST, SERVER_PORT))


try:
    chat_thread = ChatThread(chat_socket,(SERVER_HOST, SERVER_PORT))
    chat_thread.start()
    try:    
        command = {
        'cmd': 'name',
        'params': {
            'name': 'Deeksha',
        },
    }
        
        chat_thread.write_packet(json.dumps(command))
        root.mainloop()
    finally:
        chat_thread.stop()
        chat_thread.join()
finally:
    chat_socket.close()












