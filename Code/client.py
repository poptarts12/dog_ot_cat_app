import tkinter as tk
from tkinter.filedialog import askopenfilename
from PIL import ImageTk, Image

import socket
from constants import *

# global variables to work with gui buttons and more
is_file_selected = False
filename_selected = "Default.png"

root = tk.Tk()


canvas = ''
message = ""


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
    instructions = tk.Label(root, text="Please choose the picture you want to check!")
    instructions.pack()

    img = ImageTk.PhotoImage(Image.open(filename_selected))
    label = tk.Label(root, image=img,width= 900, height= 850)
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


# connecting to server
def connect_client() -> socket.socket:
    client = socket.socket()
    client.connect((CLIENT_IP, PORT))
    return client


def main():
    # generating keys
    # connecting to server
    # client = connect_client()
    # send publick key
    # sending file and initiating gui
    # send_file(PUBLICK_CLIENT,client)
    # client
    # send_file_thread = threading.Thread(target=send_chosen_file,args=(client,))
    # send_file_thread.start()

    GUI()


if __name__ == "__main__":
    main()
