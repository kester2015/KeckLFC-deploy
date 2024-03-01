import socket

# Define the IP address and port number to use
ip_address = "127.0.0.1"
port = 8000

# Create a socket object
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to the server
client_socket.connect((ip_address, port))

# Send a command to the server
command = "ls"
client_socket.send(command.encode())

# Receive the response from the server
response = client_socket.recv(1024).decode()

# Print the response
print(response)

# Close the connection
#client_socket.close()
