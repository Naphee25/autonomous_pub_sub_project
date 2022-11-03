import requests
from requests.structures import CaseInsensitiveDict
import numpy as np
import random
import json


#Converting the ID to bipolar format
def refine_id(retrieved_id):
    id_string = ''.join(['{0:07b}'.format(x) for x in retrieved_id])
    
    #converting to int from binary
    idVectorBinary = [int(x) for x in id_string]
    
    #replacing 0s with -1
    idVectorBinary = [-1 if x == 0 else x for x in idVectorBinary] + [1,1,1,1,1,1]
    
    return idVectorBinary


#converting the message to the original format
def get_original_msg(chunk_list, id):
    list_chunk_decrypted = []
    list_of_words = []

    for item in chunk_list:
        list_chunk_decrypted.append(decrypt_msg(item, id))

    x = len(list_chunk_decrypted)
    if x >= 2:
        for item in list_chunk_decrypted[:x-1]:
            item = convert_to_binary(item)
            list_of_words.append(convert_to_letters(item, 994))
    
    last_chunk = convert_to_binary(list_chunk_decrypted[x-1]).rstrip('0')
    size = len(last_chunk) - 6
    list_chunk_decrypted = convert_to_letters(last_chunk[:size], size-6)

    list_of_words.append(list_chunk_decrypted)
    
    return ''.join(list_of_words)


#converting bipolar to binary
def convert_to_binary(chunk):
    numbers = [0 if x == -1 else int(x) for x in chunk]
    wholeset = ''.join([str(x) for x in numbers])

    return wholeset


#converting binary to String of letters
def convert_to_letters(number_string, num_letter):

    ascii_letters = []
    for i in range(0, num_letter, 7):
        ascii_letters.append(chr(int(number_string[i:i+7], 2)))

    return "".join(ascii_letters)


# decrypting the message
def decrypt_msg(chunk, id):

    prod_subtract = np.subtract(chunk, id)

    prod_divide = np.divide(prod_subtract, id)

    return list(prod_divide)


# Retreiving the data from the server
def retrieve_data(url, id):

    headers = CaseInsensitiveDict()
    headers["Content-Type"] = "application/x-www-form-urlencoded"
    
    #Encrypt the sent ID
    IDList = json.loads(id)
    
    #Generate random data to encrypt ID
    randomData = []
    
    for i in range(1000):
        n = random.randrange(-1, 2, 2)
        randomData.append(n)
        
    #Encrypt ID
    encID = list(np.multiply(randomData, IDList) + IDList)
    
    #Convert Encrypt ID to string
    encIDStr = str(encID)
    
    x = requests.get(url, params = {"ID": encIDStr}, headers=headers)

    return x.text
