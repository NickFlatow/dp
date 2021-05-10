import requests
import flask
import pymysql.cursors
import sys
from flask import request, jsonify

app = flask.Flask(__name__, instance_relative_config=True)
app.config.from_object('config.default')
app.config.from_pyfile('config.py')


data = {"registrationRequest":[
{
"cbsdSerialNumber": "1111",
"fccId": "cde456",
"cbsdCategory": "B",
"userId": "Robert Smith"
}
]}



@app.route('/', methods=['GET'])
def home():
    return"<h1>Domain Proxy</h1><p>test version</p>"

@app.route('/dp/v1/registration', methods=['POST'])
def dp_reg():
    # print(request.data)
    response = requests.post('https://192.168.4.222:5001/v1.2/registration', 
    cert=('certs/client.cert','certs/client.key'),
    verify=('certs/ca.cert'),
    json=data)

    #     #  "registrationRequest":[
    #     #     {
    #     #         "cbsdSerialNumber": "1111",
    #     #         "fccId": "cde456",
    #     #         "cbsdCategory": "B",
    #     #         "userId": "Robert Smith"
    #     #     }
    #     # ]
    

    # print("Status code: ", response.status_code)
    # print("Printing Entire Post Request")
    # return response.json()

    # print(response.json())
    print(app.config["EMAIL"])
    print(response.json)
    return response.json
    # return request.json

@app.route('/dp/v1/spectrumInquiry', methods=['POST'])
def dp_peg():
    # print(request.data)
    response = requests.post('https://192.168.4.222:5001/v1.2/spectrumInquiry', 
    cert=('/certs/client.cert','../certs/client.key'),
    verify=('/certs/ca.cert'),
    json=request.json)

    #     #  "registrationRequest":[
    #     #     {
    #     #         "cbsdSerialNumber": "1111",
    #     #         "fccId": "cde456",
    #     #         "cbsdCategory": "B",
    #     #         "userId": "Robert Smith"
    #     #     }
    #     # ]
    

    # print("Status code: ", response.status_code)
    # print("Printing Entire Post Request")
    # return response.json()

    print(response.json())
    
    return response.json()
    # return request.json
@app.route('/dp/v1/grant', methods=['POST'])
def dp_geg():
    # print(request.data)
    response = requests.post('https://192.168.4.222:5001/v1.2/grant', 
    cert=('../certs/client.cert','../certs/client.key'),
    verify=('../certs/ca.cert'),
    json=request.json)

    #     #  "registrationRequest":[
    #     #     {
    #     #         "cbsdSerialNumber": "1111",
    #     #         "fccId": "cde456",
    #     #         "cbsdCategory": "B",
    #     #         "userId": "Robert Smith"
    #     #     }
    #     # ]
    

    # print("Status code: ", response.status_code)
    # print("Printing Entire Post Request")
    # return response.json()

    print(response.json())
    
    return response.json()
    # return request.json
@app.route('/dp/v1/heartbeat', methods=['POST'])
def dp_heg():
    # print(request.data)
    response = requests.post('https://192.168.4.222:5001/v1.2/heartbeat', 
    cert=('../certs/client.cert','../certs/client.key'),
    verify=('../certs/ca.cert'),
    json=request.json)

    #     #  "registrationRequest":[
    #     #     {
    #     #         "cbsdSerialNumber": "1111",
    #     #         "fccId": "cde456",
    #     #         "cbsdCategory": "B",
    #     #         "userId": "Robert Smith"
    #     #     }
    #     # ]
    

    # print("Status code: ", response.status_code)
    # print("Printing Entire Post Request")
    # return response.json()

    print(response.json())
    
    return response.json()
    # return request.json
@app.route('/dp/v1/test', methods=['POST'])
def dp_test():
    print(request.json())

connection = pymysql.connect(host='localhost',
                             user='root',
                             password='N3wPr1vateNw',
                             database='ACS_V1_1',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

with connection.cursor() as cursor:
    # Read a single record
    sql = "Select `SN`  FROM `apt_cpe_list_SiriusFly` "
    cursor.execute(sql)
    result = cursor.fetchall()
    print(result)


if __name__ == "__main__":
    dp_reg()


app.run(port = app.config["PORT"])

