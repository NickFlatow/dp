@app.route('/', methods=['GET'])
def home():
    return"<h1>Domain Proxy</h1><p>test version</p>"

@app.route('/dp/v1/test', methods=['POST'])
@cross_origin()
def dp_test():
    testSN = request.args.get('key1')
    print("!!!!!!!!!!!!!!!!!!!!!\n" + testSN + "11111111111111111111\n")
    return testSN