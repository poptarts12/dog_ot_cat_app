from constants import *


def make_propereties_message(message_len, path):
        foramt = get_format(path)
        # make number of packets
        number_of_packets = get_number_of_packets(message_len)
        clear_message = str(number_of_packets) + foramt
        message = (clear_message).zfill(FIRST_MESSAGE_LENGTH - 1) # because we added the length for the string
        message = str(len(clear_message)) + message
        return message


def filter_message(message):
    if message == "Exit":
        return "close", -1
    full_message = message[-int(message[0]):] # full message = without zeros and the length of the message
    # keep only letters
    format = "".join([ch for ch in full_message if ch.isalpha()])
    packets_num = "".join([ch for ch in full_message if not ch.isalpha()])
    return format, int(packets_num)

def get_number_of_packets(message_len):
    number_of_packets = message_len / BUFFER_SIZE
    if number_of_packets - int(number_of_packets) == 0:
        number_of_packets = int(number_of_packets)
    else:
        number_of_packets = int(number_of_packets) + 1
    return number_of_packets


def get_format(path):
    format_dot = path.rfind(".")
    format = path[format_dot + 1:]
    return format

