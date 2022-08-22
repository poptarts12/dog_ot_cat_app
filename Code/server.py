from constants import *
import socket
from keras.models import load_model
import numpy as np
from tensorflow.keras.preprocessing import image

file_name = "temp file.jpg"


# get one user to the server
def get_user(server: socket.socket):
    server.listen(NUMBER_OF_USERS)
    return server.accept()


def get_file(client: socket.socket):
    seconds_to_wait_for_data = 6
    file = open(file_name, "wb")
    print(file)
    image_data = client.recv(BUFFER_SIZE)  # stream based protocol
    print("receiving data")
    while image_data:
        client.settimeout(seconds_to_wait_for_data)
        # save the data
        file.write(image_data)
        # get the rest of the data
        try:
            image_data = client.recv(BUFFER_SIZE)
            print("receiving data")
        except socket.timeout:
            print('there is no more data to pass')
            client.settimeout(None)
            break
    print("done")


def main():
    # load the model
    model = load_model('../Data/saved_model/CNN_Cat_Dog_Model.h5')
    # Examine model
    model.summary()

    # Examine Weights
    model.weights

    # Examine Optimizer
    model.optimizer

    print("yes it works!!!yes!!")

    # create server
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((SERVER_IP, PORT))

    while True:
        print("waiting for client")
        # get client
        client, client_address = get_user(server)
        # get files analyze them and send the results
        while True:
            get_file(client)
            print("conected")
            test_image = image.load_img(file_name, target_size=(64, 64))
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
            # Print result
            print("\nPrediction: " + answer)
            # send result
            client.send(answer.encode())


if __name__ == "__main__":
    main()
