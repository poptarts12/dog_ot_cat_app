import tkinter as tk
from tkinter.filedialog import askopenfilename
from tkinter import filedialog as fd

import socket
from constants import *



# global variables to work with gui buttons and more
is_file_selected = False
filename_selected = "Default.png"


canvas = ''
message = ""


def GUI():
    # setting up the window itself
    global filename_selected
    global canvas
    global message
    root = tk.Tk()
    root.resizable(False, False)
    root.geometry("1000x1000")  # set the size
    root.title("cat or dogs recognizer")
    # greeting the user
    greetings = tk.Label(root, text="Hello and welcome to dog or cat recognizer!")
    greetings.pack()

    # giving instruction on how to use the application
    instructions = tk.Label(root, text="Please choose the picture you want to check!")
    instructions.pack()

    open_image = tk.Button(root, text="Open Image", command=open_image_chooser)
    open_image.pack()

    # the image of the file just for entertainment
    canvas = tk.Canvas(root, width=1000, height=1000)
    canvas.pack()
    # putting an image
    img = tk.PhotoImage(file=filename_selected)
    canvas.create_image(20, 20, anchor=tk.NW, image=img)



    # Starting the Application
    root.mainloop()


def open_image_chooser():
    global filename_selected
    global is_file_selected
    filename_selected = askopenfilename()
    is_file_selected = True
    print("You have selected : %s" % filename_selected)


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
