import socket

# Define the IP address and port number to use
ip_address = "127.0.0.1"
port = 8000

# Create a socket object
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the IP address and port number
server_socket.bind((ip_address, port))

# Listen for incoming connections
server_socket.listen()

# Accept incoming connections
(client_socket, address) = server_socket.accept()

# Receive data from the client
data = client_socket.recv(1024).decode()

# Execute the command sent by the client and get the response
response = "Command executed successfully"

# Send the response back to the client
client_socket.send(response.encode())

# Close the connection
# client_socket.close()
