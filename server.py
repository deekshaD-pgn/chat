import signal
import network
import json

LISTEN_ADDR = '0.0.0.0'
LISTEN_PORT = 9999

def handle_sigint(signum, frame):
    print('Interrupted')
    listener.stop()

    
signal.signal(signal.SIGINT, handle_sigint)    
signal.signal(signal.SIGTERM, handle_sigint) 


class ChatThread(network.ServerChatThread):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = 'Anonymous'
    

    def process_packet(self, packet):
        if packet is not None:
            request = json.loads(packet)
            if request['cmd'] == 'name': 
                self.name = request['params']['name']
            elif request['cmd'] == 'say':
                command = {
                    'cmd' : 'said',
                    'params' : {
                        'name': self.name,
                        'message': request['params']['message'],
                    },
                }
                self.listener.broadcast(json.dumps(command))

listener = network.Listener(LISTEN_ADDR, LISTEN_PORT, ChatThread)
listener.run()