import socket

def Main():   
    host = '192.168.1.4' #Server ip
    # host = '127.0.0.1'
    port = 5000 # > 1024

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((host, port))
    
    clients = [('192.168.1.4', 7000), ('192.168.1.5', 7000), ('192.168.1.4', 8000), ('192.168.1.5', 8000)] # when using 2 laptops, each computer using sensors and a camera simultaneously
    # clients = [('192.168.1.4', 7000), ('192.168.1.5', 7000), ('192.168.1.4', 8000), ('192.168.1.5', 8000), ('192.168.1.15', 8000), ('192.168.1.58', 8000)] # when using 4 laptops, 2 for sensors, 2 for cameras
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