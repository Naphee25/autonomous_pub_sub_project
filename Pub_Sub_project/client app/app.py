from flask import Flask, request, render_template, redirect


import json
from flask.helpers import url_for
import numpy as np
import encoder
import decoder
app = Flask(__name__)

#Initialize number of message for running client
numMsg = 0

#Host address
#host = "http://16.171.43.25:8080"
host = "http://127.0.0.1:83"

@app.route('/')
def index():
    #Load the page for list of clients IDs
    rows =[]
    with open("listOFIDs.txt") as l:
        ids = l.readlines()

    for n in ids:
        rows.append(n)

    return render_template('table.html', len = len(rows), Data = rows)

@app.route('/home')
def client():
    #Load client home page
    return render_template('index.html')


@app.route('/get', methods=['GET'])
def getData():
    #Retrive data from the publisher
    id = request.args.get('data')
    
    resp = decoder.retrieve_data(host + "/sub", id)

    if resp == "No message found":
        return "No message found"

    if resp == "Invalid ID":
        return "ID Does not exist"

    data = json.loads(resp)
    idList = json.loads(id)

    try:
        #Decode the bipolar msg and get the msg recieved from the publisher
        pub_msg = decoder.get_original_msg(data, idList)
        return pub_msg
    except:
        return "No Corresponding ID found"

@app.route('/post', methods=['POST'])
def post():
    global numMsg
    
    #Increment the number of sent messages for running client
    numMsg = numMsg + 1

    #Retrieve the message entered by the user
    msg = request.form['data']
    
    #Send data to the Network Facilitator
    id = encoder.send(host + '/publish', msg, numMsg)

    #Update the list of ID file
    if numMsg == 1:
        with open("listOFIDs.txt", "a") as file:
            file.write(str(id) + '\n')

    return str(id)

@app.after_request
def add_header(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)

