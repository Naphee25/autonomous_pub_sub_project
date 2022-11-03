from flask import Flask, request, render_template
import json
import pickle
import numpy as np
import os
import time
import csv

#Path for Server
path_dir = "/Users/nadia/Desktop/MiniProjectLatest/server app/"

# creating the Flask application
app = Flask(__name__)

#dictionary
dictionary = {}

#Creating indexes for msgs
msg_count = 1

#Default web page response
@app.route('/')
def index():
    return render_template('index.html')


#Method to publish data
@app.route('/publish', methods=['POST'])
def my_form_post():
    global msg_count
    global dictionary

    #getting the data from client
    data = request.form['data']

    #Converting string to list
    data_list = json.loads(data)

    #taking the key to store
    key = str(data_list[0])

    #Check if the key dictionary is not empty
    if(len(dictionary.keys()) != 0):

        #List to store the dot product results of the recieved key with the existing key in the key dictionary
        dotResult = []
        
        #Get the list of keys in the key dictionary
        keyList = list(dictionary)
        
        #Perform dot product between the recieved key and keys in the dictionary
        for item in dictionary.keys():
            itemList = json.loads(item)
            dotResult.append( (np.dot(itemList, data_list[0]))/1000 )

        #Check if the dot product is greater than the threshold 0.028
        if max(dotResult) > 0.028:
        
            print("Key exists")
            
            empty_list = []
            
            #finding the similar key index in the dictionary
            index = dotResult.index(max(dotResult))

            #Read from the databank (Key Pointer and Data) and store it in the empty_list
            with open(path_dir + 'db.csv', 'r', newline='') as read:
                reader = csv.reader(read)
                for row in reader:
                    empty_list.append(row)
                
            #Search for the data corresponding to the matching ID
            for i in range(0, len(empty_list)):
                if int(empty_list[i][0]) == index:
                    empty_list[i][1] = data_list
                    
            #Overwrite the data corresponding to the matching ID with the new ID
            with open(path_dir + 'db.csv', 'w', newline='') as h:
                writer = csv.writer(h)
                writer.writerows(empty_list)

        else:
            print("New Key")
            
            #Append the received key to the dictionary and the data to the data bank
            with open(path_dir + 'db.csv', 'a', newline='') as f:
                writer = csv.writer(f)
                z =len(dictionary)
                dictionary.update({key:z})
                writer.writerow([z, data_list])


    else:

        #If the dictionary and data bank are empty, append the received key to the dictionary and the data to the data bank
        with open(path_dir + 'db.csv', 'a', newline='') as f:
            writer = csv.writer(f)
            z =len(dictionary)
            dictionary.update({key:z})
            writer.writerow([z, data_list])


    return "data received"

#Method to send the data back to client
@app.route('/sub', methods=['GET'])
def get_id():

    global dictionary

    start = time.time()

    #checking database before calculating dot product
    check_db = len(dictionary.keys())
    if check_db == 0:
        return "No message found"

    # getting the ID and converting to list
    id_string = request.args.get('ID')

    # check if ID is in the right format
    try:
        id_int_list = json.loads(id_string)
    except:
        return "Invalid ID"

    #Converting the ID to bipolar format
    #ID = refine_id(id_int_list)

    #getting all keys as a matrix (from string to list)
    final_list = []
    for item in dictionary.keys():
        final_list.append(json.loads(item))

    #Calculating the dot product
    dot_prod = list(np.dot(final_list, id_int_list))

    my_list = []
    for i in final_list:
        my_list.append(str(i))

    #Finding the index of max
    my_index = dot_prod.index(max(dot_prod))


    #Retrieving the data and sending back to client
    
    with open(path_dir + 'db.csv', 'r', newline='') as ac:
        ascp = csv.reader(ac, delimiter=',')
        for row in ascp:
            if int(row[0]) == my_index:
                target_data = row[1]
    
    #target_data_key = my_list[my_index]
    #target_data = database.get(target_data_key)
    print("Size of the founded message:", len(target_data))

    end = time.time()
    print("Time to process a request: {:.20f}".format(end-start))

    #return database.get(target_data_key)
    return target_data


#Converting the ID to bipolar format
def refine_id(retrieved_id):
    id_string = ''.join(['{0:07b}'.format(x) for x in retrieved_id])

    #converting to int from binary
    idVectorBinary = [int(x) for x in id_string]


    #replacing 0s with -1
    idVectorBinary = [-1 if x == 0 else x for x in idVectorBinary] + [1,1,1,1,1,1]

    return idVectorBinary

@app.after_request
def add_header(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response

#Starting the web server
if __name__ == '__main__':
    app.run()
