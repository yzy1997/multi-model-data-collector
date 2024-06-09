import socket

def Main():   
    host = '192.168.1.137' #Server ip
    # host = '127.0.0.1'
    port = 5000 # > 1024

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((host, port))
    # clients = [('192.168.1.15', 7000), ('192.168.1.237',7000), ('192.168.1.15', 8000), ('192.168.1.137', 8000)]
    clients = [('192.168.1.137', 8000),('192.168.1.137', 7000)]
    # clients = [('192.168.1.25', 7000), ('192.168.1.107', 7000)]
    # clients = [('192.168.1.107', 7000)] # this is the movesense client
    # clients = [('192.168.1.3', 8000), ('192.168.1.25', 8000), ('192.168.1.218', 8000), ('192.168.1.219', 8000)] # clients in the local network
    # clients = [('192.168.1.107', 7000),('192.168.1.3', 8000), ('192.168.1.25', 8000), ('192.168.1.218', 8000), ('192.168.1.219', 8000)] # clients in the local network, inclue server
    print("Server Started")
    control_message = input("Enter control message (1 for starting to collect data, 0 for stopping):->")
    while control_message !='q':
        for client in clients:
            s.sendto(control_message.encode('utf-8'), client)
            data, addr = s.recvfrom(1024)
            data = data.decode('utf-8')
            print(f"Received from server: {addr} " + data)
        control_message = input("Enter control message (1 for starting to collect data, 0 for stopping):->")
    s.close()


if __name__=='__main__':
    Main()