import os

from constants import *
import socket
from keras.models import load_model
import numpy as np
import threading
import protocol
from tensorflow.keras.preprocessing import image

file_name = "temp file."


# get one user to the server
def get_users(server: socket.socket, model):
    print('Socket is listening..')
    server.listen(NUMBER_OF_USERS)
    ThreadCount = 0
    while True:
        Client, address = server.accept()
        print('\n\nConnected to: ' + address[0] + ':' + str(address[1]))
        ThreadCount += 1
        print('Thread Number: ' + str(ThreadCount))
        client_thread_taker = threading.Thread(target=client_thread, args=(Client, model, ThreadCount,))
        client_thread_taker.start()


def get_file_data(client: socket.socket, thread_number):
    global file_name
    try:  # if the client crashed
        properties_message = client.recv(BUFFER_SIZE).decode()  # first message is how many packets
        print(properties_message)
        format_type, packets_num = protocol.filter_message(properties_message)
        file_name_per_thread = str(thread_number) + file_name + format_type
        sent_data = True
        if packets_num == -1 and format_type == "close":  # the client in exit mode
            sent_data = False
        if sent_data:  # if true then there is image to receive
            file = open(file_name_per_thread, "wb")
            print(f"receiving data from {packets_num} packets in thread {thread_number}")
            for i in range(0, packets_num + 1):
                image_data = client.recv(BUFFER_SIZE)
                file.write(image_data)
                if i == packets_num - 1:  # because the receiving not stopping, so we need to force it.
                    break
            print("there is no more data")
            file.close()
            print("done receiving\n")
        return sent_data, file_name_per_thread
    except ConnectionResetError:
        print("client crash")
        client.close()
        return False, "no file"


def create_server() -> socket.socket():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server.bind((SERVER_IP, PORT))
    except socket.error as e:
        print(str(e))
    return server


def main():
    # load the model
    model = load_model('CNN_Cat_Dog_Model.h5')
    # Examine model
    model.summary()
    server = create_server()
    print("yes it works!!!yes!!")
    print("waiting for clients")
    # get client
    get_users(server, model)


def client_thread(client: socket.socket, model, thread_number):
    # get first message and check if there is any data to get
    while True:
        get_file_data_check, file_name_for_client = get_file_data(client, thread_number)
        if get_file_data_check:
            result = get_result(model, file_name_for_client)
            # Print result
            print("Prediction: " + result)
            # send result
            client.send(result.encode())
            print("Prediction sent")
        else:
            print(f"client number {thread_number} is done,client closed.\n")
            client.close()
            break


def get_result(model, file_name_for_thread) -> str:
    test_image = image.load_img(file_name_for_thread, target_size=(64, 64))
    # Add a 3rd Color dimension to match Model expectation
    test_image = image.img_to_array(test_image)
    # Add one more dimension to beginning of image array so 'Predict' function can receive it (corresponds to Batch,
    # even if only one batch)
    test_image = np.expand_dims(test_image, axis=0)
    result = model.predict(test_image)
    # Map is 2D so check the first row, first column value
    if result[0][0] == 1:
        answer = 'this is dog'
    else:
        answer = 'this is cat'
    os.remove(file_name_for_thread)  # clean trash and be with security :)
    return answer


if __name__ == "__main__":
    main()
