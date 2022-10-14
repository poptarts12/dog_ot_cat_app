import threading
import cv2
import tkinter as tk
from tkinter.filedialog import askopenfilename
from PIL import ImageTk, Image
import os
import socket
from constants import *

# global variables to work with gui buttons and more
is_file_selected = False
filename_selected = "Default.png"

root = tk.Tk()

canvas = ''
message = tk.Label()

def GUI():
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

    message = tk.Label(root, text="The family is: ")
    message.pack()

    img = ImageTk.PhotoImage(Image.open(filename_selected))
    label = tk.Label(root, image=img, width=900, height=850) #crop picture/camera
    label.pack()

    open_image = tk.Button(root, text="Open Image", command=lambda: open_image_chooser(label))
    open_image.pack()

    open_camera = tk.Button(root, text="Open Camera", command=lambda: open_webcam_thread(label))
    open_camera.pack()

    # Starting the Application
    print("this framework shit runs good")
    root.mainloop()


def resize_checker(img):
    if img.width > 900:
        img = img.resize((900, img.height), Image.ANTIALIAS)
    if img.height > 850:
        img = img.resize((img.width, 850), Image.ANTIALIAS)
    return img

def open_webcam_thread(label):
    webcam = threading.Thread(target=open_webcam)
    webcam.start()

def open_webcam():
    label = create_window()
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, label.winfo_width())
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, label.winfo_height())

    def show_frames():
        try:
            cv2image = cv2.cvtColor(cap.read()[1], cv2.COLOR_BGR2RGB)
            img = Image.fromarray(cv2image)
            imgtk = ImageTk.PhotoImage(image=img)
            label.imgtk = imgtk
            label.configure(image=imgtk)
            label.after(20, show_frames)
        except:
            tk.messagebox.showerror(title="camera problem",message="there is no camera connection. please check if the camera connected.")
    show_frames()

def create_window():
    another_window = tk.Toplevel(root)
    another_window.title("camera")
    another_window.geometry("600x800")
    label = tk.Label(another_window, width=900, height=850)
    label.pack()
    screenshot = tk.Button(another_window,text="take screenshot", command=lambda :take_screenshot(label))
    screenshot.pack()
    return label

def take_screenshot(label):
    file_name = f"{label.frame_num}.png"
    imagetk = label.imgtk
    imgpil = ImageTk.getimage( imagetk )
    imgpil.save(file_name, "PNG")
    imgpil.close()


def open_image_chooser(label):
    global filename_selected
    global is_file_selected
    filename_selected = askopenfilename()
    is_file_selected = True
    print("You have selected : %s" % filename_selected)
    img = Image.open(filename_selected)
    img = resize_checker(img)
    img = ImageTk.PhotoImage(img)
    label.image = img
    label.configure(image=img)
    label.pack()


def send_file(path: str, socket: socket.socket):
    if os.path.isfile(path):
        with open(path, "rb") as file:  # "rb" mode opens the file in binary format for reading
            content = file.read(BUFFER_SIZE)
            while content:  #if not all the data sent(the data sends in packets of 2048 bytes)
                socket.send(content)
                content = file.read(BUFFER_SIZE)
                print("sent something")



# running in thread and checking if user chose a file if a file was chosen it is sent and waits for an answer
def send_chosen_file(socket):
    global filename_selected
    global is_file_selected
    global message
    global answer
    global got_answer
    global canvas

    while True:
        # if file was selected from the gui we send the selected file
        if is_file_selected:
            is_file_selected = False
            # converting the file to image first
            image_path = filename_selected
            print("pizdez")
            # sending the image
            send_file(image_path, socket)
            response = socket.recv(BUFFER_SIZE).decode()
            print(response)
            message.configure(text=response)
            message.pack()


# connecting to server
def connect_client() -> socket.socket:
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((CLIENT_IP, PORT))
    print("conected")
    return client


def main():
    #connecting to server
    client = connect_client()
    print(client)
    # sending file and initiating gui
    client
    send_file_thread = threading.Thread(target=send_chosen_file, args=(client,))
    send_file_thread.start()

    GUI()


if __name__ == "__main__":
    main()
