import threading
import PIL.ImageFile
import cv2
import tkinter as tk
from tkinter.filedialog import askopenfilename
from PIL import ImageTk, Image
import os
import protocol
import socket
from constants import *

# global variables to work with gui buttons and more
is_file_selected = False
filename_selected = "Default.png"
running = True
root = tk.Tk()

FIRST_MESSAGE_LENGTH = 8
message = tk.Label()
image_label = tk.Label(root, width=900, height=850)  # crop picture/camera


def GUI(client):
    # setting up the window itself
    global filename_selected
    global message
    root.resizable(False, False)
    root.geometry("1000x1000")  # set the size
    root.title("cat or dogs recognizer")
    # greeting the user
    greetings = tk.Label(root, text="Hello and welcome to dog or cat recognizer!")
    greetings.pack()

    # giving instruction on how to use the application
    instructions = tk.Label(root, text="Please choose the image you want to check!")
    instructions.pack()

    message = tk.Label(root, text="Choose picture", font=5)
    message.pack()

    put_selected_picture_on_window()

    open_image = tk.Button(root, text="Open Image", command=lambda: open_image_chooser())
    open_image.pack()

    open_camera = tk.Button(root, text="Open Camera", command=lambda: open_webcam_thread(open_image))
    open_camera.pack()

    # Starting the Application
    root.protocol("WM_DELETE_WINDOW", lambda: on_closing_window(client))  # in case he exits from the window
    print("this framework shit runs good")
    root.mainloop()


def on_closing_window(client):
    global running
    if tk.messagebox.askokcancel("Quit", "Do you want to quit?"):
        client.send("Exit".encode())  # the server will know how to handle the exit
        client.close()
        running = False  # closing the threads
        root.destroy()


def resize_checker(img):
    if img.width > 900:
        img = img.resize((900, img.height), Image.ANTIALIAS)
    if img.height > 850:
        img = img.resize((img.width, 850), Image.ANTIALIAS)
    return img


def open_webcam_thread(openImage_button):
    thread = threading.Thread(target=open_webcam, args=(openImage_button,))
    thread.start()


def open_webcam(openImage_button):
    global is_file_selected
    global filename_selected
    global running
    openImage_button["state"] = "disabled"  # for only one way to get picture
    cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    cv2.namedWindow("test")

    x, y = 0, 100  # positions for text
    img_counter = 0

    while running:
        ret, frame = cam.read()
        frame = cv2.flip(frame, 1)
        without_text_frame = frame
        try:  # if the window only opening for first time
            without_text_frame = frame.copy()
        except AttributeError:
            print("webcam is now opening")
        cv2.putText(img=frame, text="Press space for screenshot", org=(x, y),
                    fontFace=cv2.FONT_HERSHEY_DUPLEX, fontScale=1, color=(255, 0, 0), thickness=4)
        if not ret:
            print("failed to grab frame")
            break
        cv2.imshow("test", frame)
        k = cv2.waitKey(1)
        if cv2.getWindowProperty("test", cv2.WND_PROP_VISIBLE) < 1:  # if the client closing the window
            cv2.destroyAllWindows()
            openImage_button["state"] = "active"  # to activate the option to choose file
            break
        elif k % 256 == 32:
            # SPACE pressed
            # taking screenshot:
            img_name = "webcam_opencv_frame.png"
            cv2.imwrite(img_name, without_text_frame)
            filename_selected = img_name
            is_file_selected = True  # to send the file
            print("{} written!".format(img_name))
            img_counter += 1

    cam.release()


def open_image_chooser():
    global filename_selected
    global is_file_selected
    global message
    try:
        filename_selected = askopenfilename()
        if put_selected_picture_on_window():
            is_file_selected = True  # after we see there is no problems with the file
            print("You have selected : %s" % filename_selected)
            message.configure(text="al good!the image in process...")
            message.pack()
    except AttributeError:  # if the user didn't choose a picture and just closed the explorer for file path
        is_file_selected = False
        message.configure(text="You need to choose a picture,please try again.")
        message.pack()
        print("he didn't chose a picture,fuck.")
        tk.messagebox.showerror(title="picture error",
                                message="there is no picture you chose. please chose again.")
    except:  # if we don't know what the error
        is_file_selected = False
        print("error that i dont know")
        message.configure(text="Error")
        message.pack()
        tk.messagebox.showerror(title="error",
                                message="please try again.")


def put_selected_picture_on_window():
    global filename_selected
    global is_file_selected
    global image_label
    global message
    try:
        img = Image.open(filename_selected)
        img = resize_checker(img)
        img = ImageTk.PhotoImage(img)
        image_label.image = img
        image_label.configure(image=img)
        image_label.pack()
        return True
    except PIL.UnidentifiedImageError:  # the format not supported
        is_file_selected = False
        print("wtf this format means error")
        message.configure(text="the format isn't good,try another one else.")
        message.pack()
        tk.messagebox.showerror(title="format error",
                                message="the format you chose not supported,please choose or convert for "
                                        "another picture format.")
        return False


def send_file(path: str, server_socket: socket.socket) -> bool:
    if os.path.isfile(path):
        packets_num = protocol.get_number_of_packets(os.path.getsize(path))  # know how many packets to send
        properties_message = protocol.make_properties_message(os.path.getsize(path), path)
        server_socket.send(properties_message.encode())
        with open(path, "rb") as file:  # "rb" mode opens the file in binary format for reading
            content = file.read(BUFFER_SIZE)
            print(f"sent image in {packets_num} packets")
            for i in range(0, int(packets_num)):  # if not all the data sent(the data sends in packets of 2048 bytes)
                server_socket.send(content)
                content = file.read(BUFFER_SIZE)
            print("done sending")
            file.close()
            return True
    return False


# running in thread and checking if user chose a file if a file was chosen it is sent and waits for an answer
def send_chosen_file(server_socket):
    global filename_selected
    global is_file_selected
    global message
    global running

    while running:
        # if file was selected from the gui we send the selected file
        if is_file_selected and put_selected_picture_on_window():
            is_file_selected = False
            # converting the file to image first
            image_path = filename_selected
            print("pizdez")
            # sending the image
            sent = send_file(image_path, server_socket)
            if sent:
                print("waiting for answer")
                response = server_socket.recv(BUFFER_SIZE).decode()
                print(response)
                message.configure(text=response)
                message.pack()
            else:
                message.configure(text="there isn't image to check")
                message.pack()


# connecting to server
def connect_client() -> socket.socket:
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((CLIENT_IP, PORT))
        print("connected")
        return client
    except:
        tk.messagebox.showerror(title="server connection",
                                message="the connection is not working with the server,please check your internet or "
                                        "the server.")
        exit()


def main():
    # connecting to server
    client = connect_client()
    print(client)
    # sending file and initiating gui
    send_file_thread = threading.Thread(target=send_chosen_file, args=(client,))
    send_file_thread.start()
    GUI(client)


if __name__ == "__main__":
    main()
