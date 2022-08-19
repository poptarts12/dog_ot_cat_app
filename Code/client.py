import threading
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
    label = tk.Label(root, image=img, width=900, height=850)
    label.pack()

    open_image = tk.Button(root, text="Open Image", command=lambda: open_image_chooser(label))
    open_image.pack()

    # Starting the Application
    root.mainloop()


def resize_checker(img):
    if img.width > 900:
        img = img.resize((900, img.height), Image.ANTIALIAS)
    if img.height > 850:
        img = img.resize((img.width, 850), Image.ANTIALIAS)
    return img


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
            content = file.read()
            # calculating in how many packets the file will be sent
            number_of_packets = len(content) // BUFFER_SIZE + (1 if len(content) % BUFFER_SIZE != 0 else 0)
            try:
                bytes_number_of_packets = number_of_packets.to_bytes(2, "big")
            except:
                exit("File too large to be sent")
            # sending amount of packets
            socket.send(bytes_number_of_packets)
            # sending file
            for packet_index in range(number_of_packets):
                socket.send(content[packet_index * BUFFER_SIZE: (packet_index + 1) * BUFFER_SIZE])


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
    client = socket.socket()
    client.connect((CLIENT_IP, PORT))
    return client


def main():
    # generating keys
    # connecting to server
    client = connect_client()
    # send public key
    # sending file and initiating gui
    client
    send_file_thread = threading.Thread(target=send_chosen_file, args=(client,))
    send_file_thread.start()

    GUI()


if __name__ == "__main__":
    main()
