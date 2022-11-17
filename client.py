import tkinter as tk
import threading
import socket

SERVER_HOST = '10.10.98.69'
SERVER_PORT = 9999
SERVER_ADDR = (SERVER_HOST, SERVER_PORT)


class ChatThread(threading.Thread):
    
    def __init__(self, chat_socket,address,  *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.chat_socket = chat_socket
        self.address = address
        self.buffer = b''
        self.chat_socket.settimeout(0.5)
        self.running = False
        
        
    def get_line(self):
         if b'\n' in self.buffer:
                index = self.buffer.index(b'\n')
                line = self.buffer[0:index+1]
                self.buffer = self.buffer[index+1:]
                return line
         return None   
           
            
    def read_line(self):
        line = self.get_line()
        if line:
            return line
        while self.running:        
            try:
                data = self.chat_socket.recv(1024)
            except TimeoutError:
                pass
            else:
                if data == b'':
                    raise ConnectionError
                self.buffer += data
                line = self.get_line()
                if line:
                    return line
            
        
        
    def write_line(self, data):
       self.chat_socket.sendall(data)
            
        
        
    def run(self):
       
        try:
            self.running = True
            while self.running:
                try:
                    line = self.read_line()
                except ConnectionError:
                    break 
                if not line:
                    break   
                print(f'Data from {self.address}: {repr(line)}')
                # try:
                #     data_in = json.loads(utils.decode_data(line))
                # except (ValueError,  TypeError):
                #     data_out = {'error':'Invalid input'}
                # else:
                #     data_out = self.process_data(data_in)
                # thread.write_line(utils.encode_data(json.dumps(data_out)))
                self.process_data(line)
                
        except (ConnectionResetError, BrokenPipeError):
            print(f'Connection error for {self.address}')
                    
        finally:
            print(f'Disconnection from {self.address}')
            self.chat_socket.close()    
        
          
                    
    def process_data(self, data_in):
         conversation_input.insert(tk.END, data_in.decode())

    def stop(self):
        self.running = False
        
        
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
    chat_thread.write_line((message_input.get() + '\n').encode())
    message_input.delete(0, tk.END)
    message_input.focus()

send_button.bind('<Button-1>', send_click)
message_input.bind('<Return>', send_click)
    
chat_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
chat_socket.connect(SERVER_ADDR)

try:
    chat_thread = ChatThread(chat_socket, SERVER_ADDR)
    chat_thread.start()
    try:    
        root.mainloop()
    finally:
        chat_thread.stop()
        chat_thread.join()
finally:
    chat_socket.close()












