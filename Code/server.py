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
    try:  # if the client crached
        propereties_message = client.recv(BUFFER_SIZE).decode()  # first message is how many packets
        format, packets_num = protocol.filter_message(propereties_message)
        file_name_for_client = str(thread_number) + file_name  + format
        file = open(file_name_for_client, "wb")
        sended_data = True
        if packets_num == -1 and format == "close":  # the client in exit mode
            sended_data = False
        if sended_data:  # if true there is image to recive
            print(f"reciving data from {packets_num} packets")
            for i in range(0, packets_num + 1):
                image_data = client.recv(BUFFER_SIZE)
                file.write(image_data)
                if i == packets_num - 1:
                    break
            print("there is no more data")
            file.close()
            print("done receiving\n")
        return sended_data,file_name_for_client
    except ConnectionResetError:
        print("client crash")
        client.close()
        return False,"no file"


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
        get_file_data_check,file_name_for_client = get_file_data(client,thread_number)
        if get_file_data_check:
            result = get_result(model, file_name_for_client)
            # Print result
            print("Prediction: " + result)
            # send result
            client.send(result.encode())
            print("prediction sent")
        else:
            print(f"client number {thread_number} is done,client closed.")
            client.close()
            break


def get_result(model,file_name_for_thread) -> str:
    test_image = image.load_img(file_name_for_thread, target_size=(64, 64))
    # Add a 3rd Color dimension to match Model expectation
    test_image = image.img_to_array(test_image)
    # Add one more dimension to beginning of image array so 'Predict' function can receive it (corresponds to Batch, even if only one batch)
    test_image = np.expand_dims(test_image, axis=0)
    result = model.predict(test_image)
    # Map is 2D so check the first row, first column value
    if result[0][0] == 1:
        answer = 'this is dog'
    else:
        answer = 'this is cat'
    return answer


if __name__ == "__main__":
    main()
