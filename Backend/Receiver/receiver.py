from flask import Flask, request, jsonify, make_response
from flask_cors import CORS, cross_origin

app = Flask(__name__)
CORS(app, supports_credentials=True)
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route('/api/send_resistances', methods=['OPTIONS'])
@cross_origin(supports_credentials=True)
def options():
    return '', 204

@app.route("/api/send_resistances", methods=['OPTIONS', 'POST'])
@cross_origin(supports_credentials=True)
def receive_resistances():
    resistances = request.json[0]
    print(resistances)
    return resistances

#Then, handle the infos

def run():
    app.run(host='0.0.0.0', port=5000)


if __name__ == '__main__':
    run()