
import cv2
import threading
import queue
import os
from datetime import datetime

# This function will run in a separate thread to listen for input
def listen_for_input(input_queue):
    while True:
        user_input = input("Type '0' to stop recording: ")
        input_queue.put(user_input)

# This function will run in the main thread to record video
def video_shooting(control_bit):
    # Set up video capture
    video_capture = cv2.VideoCapture(0)
    frame_size = (int(video_capture.get(cv2.CAP_PROP_FRAME_WIDTH)),
                  int(video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT)))
    fps = video_capture.get(cv2.CAP_PROP_FPS)

    print("FPS: ", fps)

    # Set up video writer
    fourcc = cv2.VideoWriter_fourcc(*'DIVX')
    filename = update_file_name("output.avi")
    out = cv2.VideoWriter(filename, fourcc, fps, frame_size)
    filename_txt = filename.replace('.avi', '.csv')
    with open(filename_txt, 'w', encoding='utf-8') as f:
        f.write(f"Timestamp, Id, Get Frame\n")
    # Input queue to receive input from the thread
    input_queue = queue.Queue()

    # Start the input listener thread
    input_thread = threading.Thread(target=listen_for_input, args=(input_queue,))
    input_thread.daemon = True
    input_thread.start()

    # Start recording
    if control_bit == '1':
        frame_count = 0
        while True:
            ret, frame = video_capture.read()
            # ret, frame = False, None
            timestamp = datetime.timestamp(datetime.now())
            if ret:
                file_str = f"{timestamp},{frame_count}\n"
                with open(filename_txt, 'a', encoding='utf-8') as f:
                    f.write(file_str)
                frame_count += 1
            elif not ret:
                file_str = f"{timestamp},{frame_count}, {ret}\n"
                with open(filename_txt, 'a', encoding='utf-8') as f:
                    f.write(file_str)
                frame_count += 1
                # break

            out.write(frame)
            cv2.imshow('Video', frame)

            # Non-blocking check if '0' was entered
            try:
                if input_queue.get_nowait() == '0':
                    print("Stopping recording...")
                    break
            except queue.Empty:
                pass

            if cv2.waitKey(1) & 0xFF == ord('q'):  # Also allow exiting with 'q'
                break

        video_capture.release()
        out.release()
        cv2.destroyAllWindows()


# This function will update the file name
def update_file_name(filename=None):
    if filename is not None:
        filename_, extension = os.path.splitext(filename)
        counter = 1
        while os.path.exists(filename):
            filename = f"{filename_}_{counter}{extension}"
            counter += 1
    elif os.path.exists("output.avi"):
        counter = 1
        while os.path.exists(f"output_{counter}.avi"):
            counter += 1
        filename = f"output_{counter}.avi"
    else:
        filename = "output.avi"
    return filename

# Main function
if __name__ == "__main__":
    control_bit = input('Please input a control bit (0 or 1): ')
    video_shooting(control_bit=control_bit)

 