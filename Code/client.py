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
import sys

# global variables to work with gui buttons and more
is_file_selected = False
filename_selected = "Default.png"
running = True
root = tk.Tk()

canvas = ''
message = tk.Label()


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

    message = tk.Label(root, text="The family is: ")
    message.pack()

    img = ImageTk.PhotoImage(Image.open(filename_selected))
    label = tk.Label(root, image=img, width=900, height=850)  # crop picture/camera
    label.pack()

    open_image = tk.Button(root, text="Open Image", command=lambda: open_image_chooser(label))
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
        running = False
        root.destroy()


def resize_checker(img):
    if img.width > 900:
        img = img.resize((900, img.height), Image.ANTIALIAS)
    if img.height > 850:
        img = img.resize((img.width, 850), Image.ANTIALIAS)
    return img

def open_webcam_thread(openImage_button):
    thread = threading.Thread(target=open_webcam,args=(openImage_button,))
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
            openImage_button["state"] = "active"
            break
        elif k % 256 == 32:
            # SPACE pressed
            img_name = "webcam_opencv_frame.png"
            cv2.imwrite(img_name, without_text_frame)
            filename_selected = img_name
            is_file_selected = True
            print("{} written!".format(img_name))
            img_counter += 1

    cam.release()


def take_screenshot(label):
    file_name = "screenshot.png"
    imagetk = label.imgtk
    imgpil = ImageTk.getimage(imagetk)
    imgpil.save(file_name, "PNG")
    imgpil.close()


def open_image_chooser(label):
    global filename_selected
    global is_file_selected
    global message
    try:
        filename_selected = askopenfilename()
        print("You have selected : %s" % filename_selected)
        img = Image.open(filename_selected)
        img = resize_checker(img)
        img = ImageTk.PhotoImage(img)
        label.image = img
        # show to the client what he chose
        label.configure(image=img)
        label.pack()
        is_file_selected = True  # after we see there is no problems with the file
        message.configure(text="al good!the message in process...")
        message.pack()
    except AttributeError:  # if the user didn't choose a picture and just closed the explorer for file path
        is_file_selected = False
        print("he didnt chose a picture,fuck.")
        tk.messagebox.showerror(title="picture error",
                                message="there is no picture you chose. please chose again.")
    except PIL.UnidentifiedImageError:
        is_file_selected = False
        print("wtf this format means eror")
        tk.messagebox.showerror(title="format error",
                                message="the format you chose not supported,please choose or convert for "
                                        "another picture format.")
    except:  # if we dont know what the eror
        is_file_selected = False
        print("error that i dont know")
        tk.messagebox.showerror(title="error",
                                message="please try again.")


def send_file(path: str, socket: socket.socket) -> bool:
    if os.path.isfile(path):
        packets_num = protocol.get_number_of_packets(os.path.getsize(path))  # know how many packets to send
        properties_message = protocol.make_propereties_message(os.path.getsize(path), path)
        socket.send(properties_message.encode())
        with open(path, "rb") as file:  # "rb" mode opens the file in binary format for reading
            content = file.read(BUFFER_SIZE)
            print("sent something")
            for i in range(0, int(packets_num)):  # if not all the data sent(the data sends in packets of 2048 bytes)
                socket.send(content)
                content = file.read(BUFFER_SIZE)
            print("done sending")
            file.close()
            return True
    return False


# running in thread and checking if user chose a file if a file was chosen it is sent and waits for an answer
def send_chosen_file(socket):
    global filename_selected
    global is_file_selected
    global message
    global answer
    global got_answer
    global canvas
    global running

    while running:
        # if file was selected from the gui we send the selected file
        if is_file_selected:
            is_file_selected = False
            # converting the file to image first
            image_path = filename_selected
            print("pizdez")
            # sending the image
            sended = send_file(image_path, socket)
            if sended:
                print("waiting for answer")
                response = socket.recv(BUFFER_SIZE).decode()
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
        print("conected")
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
    client
    send_file_thread = threading.Thread(target=send_chosen_file, args=(client,))
    send_file_thread.start()
    GUI(client)


if __name__ == "__main__":
    main()
