import socket
import cv2
import threading
import queue
import os
from datetime import datetime

base_path = "/home/researcher/multi-model-data-collector/webcam/data/"

def listen_for_input(input_queue):
    host='192.168.1.4' #client ip, substitute this with your concrate local ip addr
    # host = '127.0.0.1'
    port = 8000
    
    server = ('192.168.1.4', 5000) # server ip
    # server = ('127.0.0.1', 5000)
    
    c = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    c.bind((host,port))
    
    # with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    #     # Connect to the server (replace 'server_address' and 'port' with actual values)
    #     s.bind(('192.168.1.107', 8000))
        
    while True:
        # Receive data from the server
        data, addr = c.recvfrom(1024)
        data = data.decode('utf-8')
        print("server address:"+ str(addr) +",client address:" + host + ":" + str(port))
        print("Received from server: " + data)
        c.sendto(data.encode('utf-8'), server)
        if not data:
            break  # Break the loop if no data is received
        
        user_input = data.strip()
        input_queue.put(user_input)
        

def video_shooting():
    # Initialize the video capture
    video_capture = cv2.VideoCapture(4)

    # Initialize variables for video writer which will be used when recording starts
    out = None
    is_recording = False  # Control flag for recording status

    # Input queue to receive commands from the listener thread
    input_queue = queue.Queue()

    # Start the input listener thread
    input_thread = threading.Thread(target=listen_for_input, args=(input_queue,))
    input_thread.daemon = True
    input_thread.start()
    frame_count = 1
    filename_txt = ''
    while True:
        # Non-blocking check for control commands
        try:
            control_bit = input_queue.get_nowait()
            if control_bit == '1' and not is_recording:
                # Start recording
                print("Starting recording...")
                frame_size = (int(video_capture.get(cv2.CAP_PROP_FRAME_WIDTH)),
                              int(video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT)))
                fps = video_capture.get(cv2.CAP_PROP_FPS)
                # frame_size = (int(video_capture.get(3)), int(video_capture.get(4)))
                # fps = video_capture.get(5)
                
                fourcc = cv2.VideoWriter_fourcc(*'DIVX')
                filename = update_file_name("output.avi")
                synthetic_filename = base_path + filename
                print(f"Recording to {synthetic_filename}")
                out = cv2.VideoWriter(synthetic_filename, fourcc, fps, frame_size)
                filename_txt = synthetic_filename.replace('.avi', '.csv')
                with open(filename_txt, 'w', encoding='utf-8') as f:
                    f.write(f"Timestamp, Id, Get Frame\n")
                is_recording = True
            elif control_bit == '0' and is_recording:
                # Stop recording
                print("Stopping recording...")
                out.release()
                is_recording = False
        except queue.Empty:
            pass

        

        # Record if is_recording is True
        if is_recording:
            # Read frame
            ret, frame = video_capture.read()
            timestamp = datetime.timestamp(datetime.now())
            if ret:
                file_str = f"{timestamp},{frame_count}\n"
            elif not ret:
                file_str = f"{timestamp},{frame_count}, {ret}\n"

            with open(filename_txt, 'a', encoding='utf-8') as f:
                f.write(file_str)
            frame_count += 1
            out.write(frame)

        # Display the frame
        # cv2.imshow('Video', frame)

        if cv2.waitKey(1) & 0xFF == ord('0'):  # Allow exiting with 'q'
            break

    video_capture.release()
    if is_recording:  # Ensure the video writer is released if still recording
        out.release()
    cv2.destroyAllWindows()
    f.close()

# This function will update the file name
def update_file_name(filename=None):
    
    if filename is not None:
        filename_, extension = os.path.splitext(filename)
        counter = 1
        while os.path.exists(base_path+filename):
            filename = f"{filename_}_{counter}{extension}"
            counter += 1
    elif os.path.exists(base_path+"output.avi"):
        counter = 1
        while os.path.exists(base_path+f"output_{counter}.avi"):
            counter += 1
        filename = f"output_{counter}.avi"
    else:
        filename = "output.avi"
    return filename

video_shooting()
