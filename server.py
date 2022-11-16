import socket
import utils
import threading
import signal



LISTEN_HOST = '0.0.0.0'
LISTEN_PORT = 9999
LISTEN_ADDR = (LISTEN_HOST, LISTEN_PORT)

running = False
chat_threads = []
chat_lock = threading.RLock()


def handle_sigint(signum, frame):
    print('Interrupted')
    global running
    running =  False
    
signal.signal(signal.SIGINT, handle_sigint)    
signal.signal(signal.SIGTERM, handle_sigint) 


class ChatThread(threading.Thread):
    
    def __init__(self, chat_socket,address,  *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.chat_socket = chat_socket
        self.address = address
        self.buffer = b''
        self.chat_socket.settimeout(0.5)
        self.lock = threading.RLock()
        
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
        while running:        
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
        with self.lock:
            self.chat_socket.sendall(data)
            
        
        
    def run(self):
        try:
            try:
                while running:
                    try:
                        line = self.read_line()
                    except ConnectionError:
                        break 
                    if not line:
                        break   
                    with chat_lock:
                        threads = chat_threads.copy()
                    for thread in threads:
                        if thread != self:
                            thread.write_line(line)    
                    
                
            finally:
                print(f'Disconnection from {self.address}')
                self.chat_socket.close()    
            
        finally:
            with chat_lock:
                try:
                    index = chat_threads.index(self)
                except ValueError:
                    pass
                else:
                    del chat_threads[index]        
            


listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
listen_socket.settimeout(0.5)

try:
    listen_socket.bind(LISTEN_ADDR)
    listen_socket.listen()
    running = True
    while running:
        try:
            chat_socket, address = listen_socket.accept()
        except  TimeoutError:
            pass
        else:
            print(f'Connection from {address}')
            thread = ChatThread(chat_socket, address)
            thread.start()
            with chat_lock:
                chat_threads.append(thread)
    with chat_lock:
        # Make a copy of chat threads, because we must release the lock!
        threads = chat_threads.copy()
    for thread in threads:
        thread.join()         
finally:
    listen_socket.close()
 

# socket_file = chat_socket.makefile('r')
# 	try:
# 		#Received padlock packet
# 		data_in =utils.decode_data(socket_file.readline())
# 		# Add own lock and return the packet
# 		data_out = encrypt.encrypt(CRYPT_KEY, data_in)
# 		chat_socket.sendall(utils.encode_data(data_out))
# 		# Received packet with sender's padlock removed
# 		data_in =utils.decode_data(socket_file.readline())
# 		#Remove our padlock
# 		payload = encrypt.encrypt(CRYPT_KEY, data_in)
# 		print(f'Received {payload}!')
# 	finally:
# 		socket_file.close()		
