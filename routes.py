@app.route('/', methods=['GET'])
def home():
    return"<h1>Domain Proxy</h1><p>test version</p>"

@app.route('/dp/v1/test', methods=['POST'])
def dp_test():
    testSN = request.args.get('key1')
    return testSN