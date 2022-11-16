from base64 import b64decode, b64encode

def decode_data(data):
    #Convert a line of base64 encoded data received from a socket into a plain string
    return b64decode(data.rstrip(b'\n\r')).decode()

def encode_data(data):
    # T ake plain text convert to base64 and add new line for sending via
    # a socket
	return b64encode(data.encode()) + b'\n'