import socket
import threading
from base64 import b64decode, b64encode



class BaseChatThread(threading.Thread):
    
    def __init__(self, chat_socket, address, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.chat_socket = chat_socket
        self.address = address
        self.buffer = b''
        self.chat_socket.settimeout(0.5)
        self.running = False
        
    def decode_packet(self, data):
        #Convert a line of base64 encoded data received from a socket into a plain string
        return b64decode(data.rstrip(b'\n\r')).decode()

    def encode_packet(self, data):
        # Take plain text convert to base64 and add new line for sending via
        # a socket
        return b64encode(data.encode()) + b'\n'
        
        
    def read_line(self):
         if b'\n' in self.buffer:
                index = self.buffer.index(b'\n')
                line = self.buffer[0:index+1]
                self.buffer = self.buffer[index+1:]
                return line
         return None   
           
            
    def read_packet(self):
        line = self.read_line()
        if line is not None:
            return self.decode_packet(line)
        while self.running:        
            try:
                data = self.chat_socket.recv(1024)
            except TimeoutError:
                pass
            else:
                if data == b'':
                    raise ConnectionError
                self.buffer += data
                line = self.read_line()
                if line is not None:
                    return self.decode_packet(line)
            
        
        
    def write_packet(self, data):
        
       self.chat_socket.sendall(self.encode_packet(data))
            
        
        
    def run(self):
       
        try:
            self.running = True
            while self.running:
                try:
                    packet = self.read_packet()
                except ConnectionError:
                    break 
                if packet is not None:
                    self.process_packet(packet)
        except (ConnectionResetError, BrokenPipeError):
            print(f'Connection error for {self.address}')
                    
        finally:
            print(f'Disconnection from {self.address}')
            self.chat_socket.close()    
        
          
                    
    def process_packet(self, packet):
         pass

    def stop(self):
        self.running = False
        
class ClientChatThread(BaseChatThread):
    pass
        
class ServerChatThread(BaseChatThread):
    def __init__(self, listener, chat_socket, address, *args, **kwargs):
        super().__init__(chat_socket, address, *args, **kwargs)
        self.listener = listener
        
    def run(self):
        try:
            super().run()
        finally:
            self.listener.chat_thread_stopped(self)
            
class Listener:
    def __init__(self, address, port, thread_class):
        self.address = address
        self.port = port
        self.thread_class = thread_class
        self.running = False
        self.chat_threads = []
        self.chat_lock = threading.RLock()
        
    def run(self):
        listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listen_socket.settimeout(0.5)

        try:
            listen_socket.bind((self.address, self.port))
            listen_socket.listen()
            self.running = True
            while self.running:
                try:
                    chat_socket, address = listen_socket.accept()
                except  TimeoutError:
                    pass
                else:
                    print(f'Connection from {address}')
                    thread = self.thread_class(self, chat_socket, address)
                    thread.start()
                    with self.chat_lock:
                        self.chat_threads.append(thread)
            with self.chat_lock:
                # Make a copy of chat threads, because we must release the lock!
                threads = self.chat_threads.copy()
            for thread in threads:
                thread.join()         
        finally:
            listen_socket.close()
            
    def chat_thread_stopped(self, thread):
        with self.chat_lock:
            try:
                self.chat_threads.remove(thread)
            except ValueError:
                pass
            
            
            
            
    def broadcast(self, packet):
        with self.chat_lock:
            threads = self.chat_threads.copy()
        for thread in threads:
            thread.write_packet(packet)    
            
    def stop(self):
        self.running = False
        with self.chat_lock:
            threads = self.chat_threads.copy()
        for thread in threads:
            thread.stop()
            thread.join()
        
        